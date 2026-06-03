'use strict';

// =====================
// CSRF Token
// =====================
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function getCSRFToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta && meta.getAttribute('content')) return meta.getAttribute('content');
  const fromCookie = getCookie('csrftoken');
  if (fromCookie) return fromCookie;
  const hidden = document.querySelector('input[name="csrfmiddlewaretoken"]');
  if (hidden) return hidden.value;
  return '';
}

// =====================
// Toast Notifications
// =====================
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
  toast.innerHTML = `<span>${message}</span>
    <button onclick="this.parentElement.remove()" class="close-alert">&times;</button>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

// =====================
// Navbar
// =====================
(function initNavbar() {
  const navbar       = document.getElementById('mainNavbar');
  const hamburger    = document.getElementById('hamburger');
  const navLinks     = document.getElementById('navLinks');
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
})();

// =====================
// Cart AJAX
// =====================
(function initCartActions() {
  document.addEventListener('submit', async function (e) {
    const form = e.target;
    if (!form.classList.contains('ajax-cart-form')) return;
    e.preventDefault();

    const btn = form.querySelector('button[type="submit"]');
    const originalHTML = btn?.innerHTML;
    if (btn) { btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'; btn.disabled = true; }

    try {
      const resp = await fetch(form.action, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRFToken(), 'X-Requested-With': 'XMLHttpRequest' },
        body: new FormData(form),
      });
      const data = await resp.json();
      if (data.success) {
        showToast(data.message || 'Item added to cart!', 'success');
        updateCartBadge(data.total_items);
      } else {
        showToast(data.message || 'Could not add to cart.', 'error');
      }
    } catch { showToast('Something went wrong.', 'error'); }
    finally { if (btn) { btn.innerHTML = originalHTML; btn.disabled = false; } }
  });

  function updateCartBadge(count) {
    let badge = document.getElementById('cartBadge');
    if (count > 0) {
      if (!badge) {
        const link = document.querySelector('a[href*="/cart/"]');
        if (link) { badge = document.createElement('span'); badge.id = 'cartBadge'; badge.className = 'badge'; link.appendChild(badge); }
      }
      if (badge) badge.textContent = count;
    } else if (badge) badge.remove();
  }
})();

// =====================
// Cart Page — updateCartItem (global)
// =====================
async function updateCartItem(itemId, qty) {
  try {
    const resp = await fetch(`/cart/update/${itemId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCSRFToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: `quantity=${qty}`,
    });
    const data = await resp.json();
    if (data.success) {
      if (qty <= 0) {
        document.getElementById(`cartItem-${itemId}`)?.remove();
      } else {
        const qtyEl = document.getElementById(`qty-${itemId}`);
        if (qtyEl) qtyEl.textContent = qty;
      }
      const el = (id) => document.getElementById(id);
      if (el('summarySubtotal')) el('summarySubtotal').textContent = Math.round(data.subtotal) + ' kr';
      if (el('summaryShipping')) el('summaryShipping').textContent = Math.round(data.shipping) + ' kr';
      if (el('summaryTotal'))    el('summaryTotal').textContent    = Math.round(data.total)    + ' kr';
      if (el('cartBadge'))       el('cartBadge').textContent       = data.total_items;
      if (data.total_items === 0) location.reload();
    } else {
      showToast(data.message || 'Could not update quantity.', 'error');
    }
  } catch { showToast('Something went wrong.', 'error'); }
}

// =====================
// Wishlist AJAX
// event delegation on document
// run on all pages detail, list, wishlist
// =====================
(function initWishlistAjax() {

  document.addEventListener('submit', async function (e) {
    const form = e.target;
    if (!form.classList.contains('wishlist-form')) return;
    e.preventDefault();

    const btn = form.querySelector('.wishlist-btn');

    if (btn) btn.style.pointerEvents = 'none';

    try {
      const resp = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken(),
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json',
        },
      });

      // redirect handling (e.g. if user is not authenticated)
      if (resp.redirected) {
        window.location.href = resp.url;
        return;
      }

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();

      // ── Update heart button ───────────────────────────
      // Update all buttons with the same product ID (could be multiple on page)
      const productId = form.action.match(/\/wishlist\/toggle\/(\d+)\//)?.[1];
      if (productId) {
        document.querySelectorAll(
          `form[action*="/wishlist/toggle/${productId}/"] .wishlist-btn`
        ).forEach(heartBtn => {
          heartBtn.classList.toggle('active', data.in_wishlist);
          heartBtn.title = data.in_wishlist ? 'Remove from Wishlist' : 'Add to Wishlist';
        });
      }

      // ── Update wishlist badge in navbar ─────────────
      updateWishlistBadge(data.count);

      // ── If we are on the wishlist page and the item was removed ─
      if (!data.in_wishlist && window.location.pathname.startsWith('/wishlist/')) {
        const card = form.closest('.product-card') || form.closest('.wishlist-item-card');
        if (card) {
          animateRemove(card, () => {
            refreshWishlistPage(data.count);
          });
        }
      }

      showToast(
        data.in_wishlist ? 'Added to wishlist!' : 'Removed from wishlist.',
        'success'
      );

    } catch (err) {
      console.error('Wishlist error:', err);
      // Fallback: submit the form normally (non-AJAX)
      form.submit();
    } finally {
      if (btn) btn.style.pointerEvents = '';
    }
  });

  // ─────────────────────────────────────────────────
  function animateRemove(el, callback) {
    el.style.transition = 'opacity 0.3s, transform 0.3s';
    el.style.opacity    = '0';
    el.style.transform  = 'scale(0.92)';
    setTimeout(() => {
      el.remove();
      if (callback) callback();
    }, 320);
  }

  function updateWishlistBadge(count) {
    let badge = document.getElementById('wishlistBadge');
    if (count > 0) {
      if (!badge) {
        const link = document.querySelector('a[href*="/wishlist/"]');
        if (link) {
          badge = document.createElement('span');
          badge.id = 'wishlistBadge';
          badge.className = 'badge';
          link.style.position = 'relative';
          link.appendChild(badge);
        }
      }
      if (badge) badge.textContent = count;
    } else if (badge) {
      badge.remove();
    }
  }

  function refreshWishlistPage(count) {
    // Update wishlist count in header  
    const countEl = document.getElementById('wishlistCount');
    if (countEl) countEl.textContent = count;

    // Update modal count
    const mc = document.getElementById('modalCount');
    if (mc) mc.textContent = count;

    // If the list is empty — display empty state
    const grid = document.getElementById('wishlistGrid');
    if (!grid) return;
    const remaining = grid.querySelectorAll('.product-card').length;
    if (remaining === 0) {
      grid.outerHTML = `
        <div class="empty-state">
          <i class="fas fa-heart"></i>
          <h3>Your Wishlist is Empty</h3>
          <p>Save items you love to your wishlist and find them here anytime.</p>
          <a href="/products/" class="btn-primary">Discover Products</a>
        </div>`;
      // Hide the Clear button
      const clearBtn = document.getElementById('clearWishlistBtn');
      if (clearBtn) clearBtn.style.display = 'none';
    }
  }

})();

// =====================
// Lazy Image Loading
// =====================
(function () {
  if (!('IntersectionObserver' in window)) return;
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) { img.src = img.dataset.src; img.removeAttribute('data-src'); }
        obs.unobserve(img);
      }
    });
  }, { rootMargin: '200px' });
  document.querySelectorAll('img[data-src]').forEach(img => obs.observe(img));
})();

// =====================
// Auto-dismiss Messages
// =====================
(function () {
  const c = document.getElementById('messagesContainer');
  if (c) {
    setTimeout(() => {
      c.style.transition = 'opacity 0.5s';
      c.style.opacity = '0';
      setTimeout(() => c.remove(), 500);
    }, 4500);
  }
})();

// =====================
// Mobile Menu
// =====================
(function () {
  const s = document.createElement('style');
  s.textContent = `
    @media (max-width:1024px){
      .nav-links.mobile-open{display:flex!important;flex-direction:column;position:fixed;
        top:0;left:0;right:0;bottom:0;background:#fff;z-index:9999;
        padding:80px 32px 32px;overflow-y:auto;gap:0;animation:slideInLeft .3s ease;}
      @keyframes slideInLeft{from{transform:translateX(-100%)}to{transform:translateX(0)}}
      .nav-links.mobile-open .nav-link{font-size:22px;padding:16px 0;border-bottom:1px solid #e5e7eb;}
      .nav-links.mobile-open .dropdown-menu{display:block!important;position:static;
        box-shadow:none;border:none;border-radius:0;padding-left:16px;background:#f9f9f9;}
      .nav-links.mobile-open .mega-menu{width:100%;padding:16px;}
      .nav-links.mobile-open .mega-menu-grid{grid-template-columns:1fr;gap:8px;}
    }`;
  document.head.appendChild(s);
})();

// =====================
// Session Ping
// =====================
(function () {
  let lastPing = Date.now();
  function ping() {
    if (Date.now() - lastPing > 60000) {
      lastPing = Date.now();
      fetch(window.location.href, { method: 'HEAD', cache: 'no-cache' }).catch(() => {});
    }
  }
  ['mousemove','keydown','click','scroll','touchstart'].forEach(ev =>
    document.addEventListener(ev, ping, { passive: true })
  );
})();

// =====================
// Prevent Double Submit
// =====================

document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', function () {
    const btn = form.querySelector('[type="submit"]');
    if (btn && !btn.dataset.allowDouble) {
      setTimeout(() => {
        btn.disabled = true;
        if (!btn.classList.contains('no-loading')) {
          btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Please wait...';
        }
      }, 10);
    }
  });
});

// =====================
// Smooth Scroll
// =====================
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      window.scrollTo({
        top: target.getBoundingClientRect().top + window.pageYOffset - 90,
        behavior: 'smooth',
      });
    }
  });
});
