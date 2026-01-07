"""
Tests for django.contrib.healthcheck.checks.
"""

from django.contrib.healthcheck.checks import W001, W002, check_healthcheck_middleware
from django.test import SimpleTestCase, override_settings


class HealthCheckChecksTest(SimpleTestCase):
    """Tests for health check system checks."""

    @override_settings(
        MIDDLEWARE=[
            "django.contrib.healthcheck.HealthCheckMiddleware",
            "django.middleware.security.SecurityMiddleware",
            "django.middleware.common.CommonMiddleware",
        ]
    )
    def test_middleware_first_position_no_warnings(self):
        """No warnings when middleware is in first position."""
        errors = check_healthcheck_middleware(None)
        self.assertEqual(errors, [])

    @override_settings(
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.healthcheck.HealthCheckMiddleware",
            "django.middleware.common.CommonMiddleware",
        ]
    )
    def test_middleware_after_security_middleware(self):
        """Warning when middleware comes after SecurityMiddleware."""
        errors = check_healthcheck_middleware(None)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "healthcheck.W001")

    @override_settings(
        MIDDLEWARE=[
            "django.middleware.common.CommonMiddleware",
            "django.contrib.healthcheck.HealthCheckMiddleware",
        ]
    )
    def test_middleware_after_common_middleware(self):
        """Warning when middleware comes after CommonMiddleware."""
        errors = check_healthcheck_middleware(None)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "healthcheck.W001")

    @override_settings(
        MIDDLEWARE=[
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.healthcheck.HealthCheckMiddleware",
        ]
    )
    def test_middleware_after_csrf_middleware(self):
        """Warning when middleware comes after CsrfViewMiddleware."""
        errors = check_healthcheck_middleware(None)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "healthcheck.W001")

    @override_settings(
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.middleware.common.CommonMiddleware",
        ]
    )
    def test_middleware_not_present(self):
        """Warning when middleware is not in MIDDLEWARE."""
        errors = check_healthcheck_middleware(None)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "healthcheck.W002")

    @override_settings(
        MIDDLEWARE=[
            "some.other.Middleware",
            "django.contrib.healthcheck.HealthCheckMiddleware",
            "django.middleware.security.SecurityMiddleware",
        ]
    )
    def test_middleware_after_unrelated_middleware(self):
        """No warning when middleware comes after unrelated middleware."""
        errors = check_healthcheck_middleware(None)
        self.assertEqual(errors, [])

    @override_settings(MIDDLEWARE=[])
    def test_empty_middleware(self):
        """Warning when MIDDLEWARE is empty."""
        errors = check_healthcheck_middleware(None)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "healthcheck.W002")

    @override_settings(
        MIDDLEWARE=[
            "django.contrib.healthcheck.HealthCheckMiddleware",
        ]
    )
    def test_middleware_only_health_check(self):
        """No warnings when only health check middleware is configured."""
        errors = check_healthcheck_middleware(None)
        self.assertEqual(errors, [])
