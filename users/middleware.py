"""
Middleware for auto-logout after inactivity and session security.
"""

from django.conf import settings
from django.contrib.auth import logout
from django.utils import timezone
from django.shortcuts import redirect
import time


class AutoLogoutMiddleware:
    """
    Automatically logout users after SESSION_COOKIE_AGE seconds of inactivity.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            current_time = time.time()

            if last_activity:
                elapsed = current_time - last_activity
                if elapsed > settings.SESSION_COOKIE_AGE:
                    logout(request)
                    request.session['session_expired'] = True
                    return redirect(f"{settings.LOGIN_URL}?next={request.path}")

            request.session['last_activity'] = current_time

        response = self.get_response(request)
        return response


class SessionSecurityMiddleware:
    """
    Add security headers and enforce secure session handling.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

        return response
