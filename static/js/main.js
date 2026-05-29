'use strict';

// =====================
// Utility Functions
// =====================
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

function showToast(message, type = 'success') {
  let container = document.getElementById('messagesContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'messagesContainer';
    container.className = 'messages-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `alert alert-${type}`;
  toast.innerHTML = `<span>${message}</span><button onclick="this.parentElement.remove()" class="close-alert">&times;</button>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

// =====================
// Navbar Behavior
// =====================
(function initNavbar() {
  const navbar    = document.getElementById('mainNavbar');
  const hamburger = document.getElementById('hamburger');
  const navLinks  = document.getElementById('navLinks');
  const searchToggle = document.getElementById('searchToggle');
  const searchBar    = document.getElementById('searchBar');
  const searchClose  = document.getElementById('searchClose');

  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 10);
    }, { passive: true });
  }

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('mobile-open');
      hamburger.classList.toggle('open', isOpen);
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });
  }

  if (searchToggle && searchBar) {
    searchToggle.addEventListener('click', () => {
      searchBar.classList.toggle('open');
      if (searchBar.classList.contains('open')) {
        setTimeout(() => searchBar.querySelector('.search-input')?.focus(), 100);
      }
    });
    searchClose?.addEventListener('click', () => searchBar.classList.remove('open'));
  }

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-item.dropdown')) {
      document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('force-open'));
    }
  });
})();

// =====================
// Cart AJAX Operations
// =====================
(function initCartActions() {
  document.addEventListener('submit', async function(e) {
    const form = e.target;
    if (!form.classList.contains('ajax-cart-form')) return;
    e.preventDefault();

    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn?.innerHTML;
    if (btn) {
      btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
      btn.disabled = true;
    }

    try {
      const resp = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: new FormData(form),
      });
      const data = await resp.json();
      if (data.success) {
        showToast(data.message || 'Item added to cart!', 'success');
        updateCartBadge(data.total_items);
      } else {
        showToast(data.message || 'Could not add to cart.', 'error');
      }
    } catch (err) {
      showToast('Something went wrong. Please try again.', 'error');
    } finally {
      if (btn) { btn.innerHTML = originalText; btn.disabled = false; }
    }
  });

  function updateCartBadge(count) {
    let badge = document.getElementById('cartBadge');
    if (count > 0) {
      if (!badge) {
        const cartBtn = document.querySelector('[href*="/cart/"]');
        if (cartBtn) {
          badge = document.createElement('span');
          badge.id = 'cartBadge';
          badge.className = 'badge';
          cartBtn.appendChild(badge);
        }
      }
      if (badge) badge.textContent = count;
    } else if (badge) {
      badge.remove();
    }
  }
})();

// =====================
// Wishlist AJAX Toggle
// — uses event delegation so it works on every page
//   including dynamically loaded cards
// =====================
(function initWishlistAjax() {

  // Single delegated listener on the whole document
  document.addEventListener('submit', async function(e) {
    const form = e.target;

    // Only handle wishlist-form submissions
    if (!form.classList.contains('wishlist-form')) return;
    e.preventDefault();

    const btn = form.querySelector('.wishlist-btn');
    if (btn) btn.style.pointerEvents = 'none'; // prevent double-click

    try {
      const resp = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'X-Requested-With': 'XMLHttpRequest',
        },
      });

      if (!resp.ok) throw new Error('Server error');
      const data = await resp.json();

      // ── Update heart button state ──────────────────────
      if (btn) {
        if (data.in_wishlist) {
          btn.classList.add('active');
          btn.title = 'Remove from Wishlist';
        } else {
          btn.classList.remove('active');
          btn.title = 'Add to Wishlist';
        }
      }

      // ── Update wishlist badge in navbar ────────────────
      updateWishlistBadge(data.count);

      // ── If we are ON the wishlist page, remove the card ─
      // The wishlist page uses a different form class for removal,
      // so here we only handle the toggle from product cards.
      // If the item was removed (not in wishlist) and the page
      // is the wishlist page, remove the card from DOM.
      const isWishlistPage = window.location.pathname.includes('/wishlist/');
      if (isWishlistPage && !data.in_wishlist) {
        // Find the closest product-card or wishlist item and remove it
        const card = form.closest('.product-card') || form.closest('.wishlist-item-card');
        if (card) {
          card.style.transition = 'opacity 0.3s, transform 0.3s';
          card.style.opacity = '0';
          card.style.transform = 'scale(0.95)';
          setTimeout(() => {
            card.remove();
            checkEmptyWishlist();
          }, 300);
        }
      }

      showToast(
        data.in_wishlist ? 'Added to wishlist!' : 'Removed from wishlist.',
        'success'
      );

    } catch (err) {
      // Fallback: normal form submit if AJAX fails
      form.submit();
    } finally {
      if (btn) btn.style.pointerEvents = '';
    }
  });

  // ── Wishlist remove buttons (on wishlist page) ─────────
  // These use class="wishlist-remove-form"
  document.addEventListener('submit', async function(e) {
    const form = e.target;
    if (!form.classList.contains('wishlist-remove-form')) return;
    e.preventDefault();

    const card = form.closest('.product-card') || form.closest('.wishlist-item-card');

    try {
      const resp = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'X-Requested-With': 'XMLHttpRequest',
        },
      });

      if (!resp.ok) throw new Error();

      // Animate card out
      if (card) {
        card.style.transition = 'opacity 0.3s, transform 0.3s';
        card.style.opacity = '0';
        card.style.transform = 'scale(0.95)';
        setTimeout(() => {
          card.remove();
          checkEmptyWishlist();
          // Update badge
          const badge = document.getElementById('wishlistBadge');
          if (badge) {
            const current = parseInt(badge.textContent) || 0;
            const next = current - 1;
            if (next <= 0) badge.remove();
            else badge.textContent = next;
          }
        }, 300);
      }

      showToast('Removed from wishlist.', 'success');

    } catch (err) {
      if (card) form.submit();
    }
  });

  function updateWishlistBadge(count) {
    let badge = document.getElementById('wishlistBadge');
    if (count > 0) {
      if (!badge) {
        // Try to find the wishlist link in the navbar and append badge
        const wishlistLink = document.querySelector('a[href*="/wishlist/"]');
        if (wishlistLink) {
          badge = document.createElement('span');
          badge.id = 'wishlistBadge';
          badge.className = 'badge';
          wishlistLink.style.position = 'relative';
          wishlistLink.appendChild(badge);
        }
      }
      if (badge) badge.textContent = count;
    } else if (badge) {
      badge.remove();
    }
  }

  function checkEmptyWishlist() {
    // If wishlist page has no more cards, show empty state
    const grid = document.querySelector('.products-grid');
    if (!grid) return;
    const remaining = grid.querySelectorAll('.product-card');
    if (remaining.length === 0) {
      grid.outerHTML = `
        <div class="empty-state">
          <i class="fas fa-heart"></i>
          <h3>Your Wishlist is Empty</h3>
          <p>Save items you love to your wishlist and find them here anytime.</p>
          <a href="/products/" class="btn-primary">Discover Products</a>
        </div>`;
    }
  }

})();

// =====================
// Lazy Image Loading
// =====================
(function initLazyLoad() {
  if (!('IntersectionObserver' in window)) return;
  const imgObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) {
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
        }
        imgObserver.unobserve(img);
      }
    });
  }, { rootMargin: '200px' });
  document.querySelectorAll('img[data-src]').forEach(img => imgObserver.observe(img));
})();

// =====================
// Auto-dismiss Messages
// =====================
(function initMessages() {
  const container = document.getElementById('messagesContainer');
  if (container) {
    setTimeout(() => {
      container.style.transition = 'opacity 0.5s';
      container.style.opacity = '0';
      setTimeout(() => container.remove(), 500);
    }, 4500);
  }
})();

// =====================
// Mobile Menu Styles
// =====================
(function initMobileMenuStyles() {
  const style = document.createElement('style');
  style.textContent = `
    @media (max-width: 1024px) {
      .nav-links.mobile-open {
        display: flex !important;
        flex-direction: column;
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: white;
        z-index: 9999;
        padding: 80px 32px 32px;
        overflow-y: auto;
        gap: 0;
        animation: slideInLeft 0.3s ease;
      }
      @keyframes slideInLeft {
        from { transform: translateX(-100%); }
        to   { transform: translateX(0); }
      }
      .nav-links.mobile-open .nav-link {
        font-size: 22px;
        padding: 16px 0;
        border-bottom: 1px solid #e5e7eb;
      }
      .nav-links.mobile-open .dropdown-menu {
        display: block !important;
        position: static;
        box-shadow: none;
        border: none;
        border-radius: 0;
        padding-left: 16px;
        background: #f9f9f9;
        margin-bottom: 8px;
      }
      .nav-links.mobile-open .mega-menu {
        width: 100%;
        padding: 16px;
      }
      .nav-links.mobile-open .mega-menu-grid {
        grid-template-columns: 1fr;
        gap: 8px;
      }
    }
  `;
  document.head.appendChild(style);
})();

// =====================
// Session Activity Ping
// =====================
(function initSessionPing() {
  let lastPing = Date.now();
  const PING_INTERVAL = 60000;
  function ping() {
    const now = Date.now();
    if (now - lastPing > PING_INTERVAL) {
      lastPing = now;
      fetch(window.location.href, { method: 'HEAD', cache: 'no-cache' }).catch(() => {});
    }
  }
  ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'].forEach(ev => {
    document.addEventListener(ev, ping, { passive: true });
  });
})();

// =====================
// Prevent Double Submit
// =====================
(function initFormHelpers() {
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
      const submitBtn = form.querySelector('[type="submit"]');
      if (submitBtn && !submitBtn.dataset.allowDouble) {
        setTimeout(() => {
          submitBtn.disabled = true;
          if (!submitBtn.classList.contains('no-loading')) {
            submitBtn.dataset.original = submitBtn.innerHTML;
            submitBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Please wait...`;
          }
        }, 10);
      }
    });
  });
})();

// =====================
// Smooth Scroll
// =====================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const top = target.getBoundingClientRect().top + window.pageYOffset - 90;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});
