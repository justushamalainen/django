"""
System checks for the healthcheck app.
"""

from django.conf import settings
from django.core.checks import Warning

W001 = Warning(
    "HealthCheckMiddleware should be the first middleware in MIDDLEWARE "
    "to ensure the health check endpoint bypasses ALLOWED_HOSTS validation.",
    hint=(
        "Move 'django.contrib.healthcheck.HealthCheckMiddleware' to the "
        "beginning of your MIDDLEWARE setting."
    ),
    id="healthcheck.W001",
)

W002 = Warning(
    "HealthCheckMiddleware is not in MIDDLEWARE. The health check app "
    "requires the middleware to function.",
    hint=(
        "Add 'django.contrib.healthcheck.HealthCheckMiddleware' to the "
        "beginning of your MIDDLEWARE setting."
    ),
    id="healthcheck.W002",
)


def check_healthcheck_middleware(app_configs, **kwargs):
    """
    Check that HealthCheckMiddleware is properly configured.

    The middleware must be:
    1. Present in MIDDLEWARE
    2. Placed before any middleware that might call request.get_host()
    """
    errors = []
    middleware = getattr(settings, "MIDDLEWARE", [])

    middleware_path = "django.contrib.healthcheck.HealthCheckMiddleware"

    if middleware_path not in middleware:
        errors.append(W002)
    elif middleware.index(middleware_path) != 0:
        # Check if any middleware that calls get_host() comes before our middleware
        host_calling_middleware = {
            "django.middleware.common.CommonMiddleware",
            "django.middleware.security.SecurityMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
        }
        our_position = middleware.index(middleware_path)

        for mw in middleware[:our_position]:
            if mw in host_calling_middleware:
                errors.append(W001)
                break

    return errors
