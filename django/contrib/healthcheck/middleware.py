"""
Health check middleware that bypasses ALLOWED_HOSTS validation.

This middleware intercepts health check requests early in the request cycle,
before any code that would trigger ALLOWED_HOSTS validation (such as
CommonMiddleware, SecurityMiddleware, or CsrfViewMiddleware calling
request.get_host()).

This is essential for load balancers and internal monitoring systems that
may not send the expected Host header but still need to verify the application
is running.
"""

from django.conf import settings
from django.http import HttpResponse, JsonResponse


class HealthCheckMiddleware:
    """
    Middleware that provides a health check endpoint bypassing ALLOWED_HOSTS.

    This middleware should be placed at the top of the MIDDLEWARE setting,
    before any middleware that might call request.get_host() (such as
    CommonMiddleware or SecurityMiddleware).

    The middleware checks the request path against HEALTHCHECK_URL (default:
    "/-/health/") and returns a response immediately without triggering
    host validation.

    Settings:
        HEALTHCHECK_URL: The URL path for the health check endpoint.
            Default: "/-/health/"
        HEALTHCHECK_RESPONSE_TYPE: Response format, either "text" or "json".
            Default: "text"

    Example configuration in settings.py:

        MIDDLEWARE = [
            "django.contrib.healthcheck.HealthCheckMiddleware",
            # ... other middleware
        ]

        HEALTHCHECK_URL = "/-/health/"  # Optional, this is the default
        HEALTHCHECK_RESPONSE_TYPE = "json"  # Optional, default is "text"
    """

    # Default health check URL path
    DEFAULT_URL = "/-/health/"

    def __init__(self, get_response):
        self.get_response = get_response
        # Cache settings at initialization time for performance
        self.healthcheck_url = getattr(settings, "HEALTHCHECK_URL", self.DEFAULT_URL)
        self.response_type = getattr(settings, "HEALTHCHECK_RESPONSE_TYPE", "text")

    def __call__(self, request):
        # Check if this is a health check request
        # IMPORTANT: We use request.path_info directly to avoid any processing
        # that might trigger ALLOWED_HOSTS validation via get_host()
        if request.path_info == self.healthcheck_url:
            return self.get_health_response()

        # Not a health check request, proceed with normal request processing
        return self.get_response(request)

    def get_health_response(self):
        """
        Return a health check response.

        Returns either a plain text or JSON response depending on the
        HEALTHCHECK_RESPONSE_TYPE setting.
        """
        if self.response_type == "json":
            return JsonResponse({"status": "ok"})
        else:
            return HttpResponse("ok", content_type="text/plain")
