"""
Tests for django.contrib.healthcheck.
"""

import json

from django.contrib.healthcheck import HealthCheckMiddleware
from django.core.exceptions import DisallowedHost
from django.http import HttpRequest, HttpResponse
from django.test import SimpleTestCase, override_settings


def get_response(request):
    """Simulate a view that calls get_host()."""
    # This will raise DisallowedHost if the host is not allowed
    request.get_host()
    return HttpResponse("Normal response")


class HealthCheckMiddlewareTest(SimpleTestCase):
    """Tests for HealthCheckMiddleware."""

    @override_settings(ALLOWED_HOSTS=["example.com"])
    def test_health_check_bypasses_allowed_hosts(self):
        """Health check should return 200 even with invalid Host header."""
        middleware = HealthCheckMiddleware(get_response)

        # Create request with invalid host that would normally be rejected
        request = HttpRequest()
        request.META = {"HTTP_HOST": "invalid-host.example.com"}
        request.path_info = "/-/health/"

        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")
        self.assertEqual(response["Content-Type"], "text/plain")

    @override_settings(ALLOWED_HOSTS=["example.com"])
    def test_non_health_check_validates_allowed_hosts(self):
        """Non-health check requests should still validate Host header."""
        middleware = HealthCheckMiddleware(get_response)

        # Create request with invalid host
        request = HttpRequest()
        request.META = {"HTTP_HOST": "invalid-host.example.com"}
        request.path_info = "/some/other/path/"

        with self.assertRaises(DisallowedHost):
            middleware(request)

    @override_settings(ALLOWED_HOSTS=["example.com"])
    def test_valid_host_normal_request(self):
        """Normal requests with valid host should proceed normally."""
        middleware = HealthCheckMiddleware(get_response)

        request = HttpRequest()
        request.META = {"HTTP_HOST": "example.com"}
        request.path_info = "/some/path/"

        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Normal response")

    @override_settings(HEALTHCHECK_URL="/custom-health/", ALLOWED_HOSTS=["example.com"])
    def test_custom_health_check_url(self):
        """Health check URL should be configurable via settings."""
        middleware = HealthCheckMiddleware(get_response)

        request = HttpRequest()
        request.META = {"HTTP_HOST": "invalid-host"}
        request.path_info = "/custom-health/"

        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")

    @override_settings(HEALTHCHECK_URL="/custom-health/", ALLOWED_HOSTS=["example.com"])
    def test_default_url_not_matched_when_custom_url_set(self):
        """Default URL should not work when custom URL is configured."""
        middleware = HealthCheckMiddleware(get_response)

        request = HttpRequest()
        request.META = {"HTTP_HOST": "invalid-host"}
        request.path_info = "/-/health/"

        with self.assertRaises(DisallowedHost):
            middleware(request)

    @override_settings(
        HEALTHCHECK_RESPONSE_TYPE="json", ALLOWED_HOSTS=["example.com"]
    )
    def test_json_response_type(self):
        """Health check should return JSON when configured."""
        middleware = HealthCheckMiddleware(get_response)

        request = HttpRequest()
        request.META = {"HTTP_HOST": "invalid-host"}
        request.path_info = "/-/health/"

        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content)
        self.assertEqual(data, {"status": "ok"})

    @override_settings(HEALTHCHECK_RESPONSE_TYPE="text", ALLOWED_HOSTS=["example.com"])
    def test_text_response_type(self):
        """Health check should return plain text by default."""
        middleware = HealthCheckMiddleware(get_response)

        request = HttpRequest()
        request.META = {"HTTP_HOST": "invalid-host"}
        request.path_info = "/-/health/"

        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertEqual(response.content, b"ok")

    @override_settings(ALLOWED_HOSTS=[])
    def test_health_check_with_empty_allowed_hosts(self):
        """Health check should work even when ALLOWED_HOSTS is empty."""
        middleware = HealthCheckMiddleware(get_response)

        request = HttpRequest()
        request.META = {"HTTP_HOST": "any-host"}
        request.path_info = "/-/health/"

        response = middleware(request)

        self.assertEqual(response.status_code, 200)

    @override_settings(ALLOWED_HOSTS=["*"])
    def test_health_check_with_wildcard_allowed_hosts(self):
        """Health check should work with wildcard ALLOWED_HOSTS."""
        middleware = HealthCheckMiddleware(get_response)

        request = HttpRequest()
        request.META = {"HTTP_HOST": "any-host.example.com"}
        request.path_info = "/-/health/"

        response = middleware(request)

        self.assertEqual(response.status_code, 200)

    @override_settings(ALLOWED_HOSTS=["example.com"])
    def test_health_check_no_host_header(self):
        """Health check should work even without Host header."""
        middleware = HealthCheckMiddleware(get_response)

        request = HttpRequest()
        request.META = {}
        request.path_info = "/-/health/"

        response = middleware(request)

        self.assertEqual(response.status_code, 200)

    @override_settings(ALLOWED_HOSTS=["example.com"])
    def test_health_check_exact_path_match(self):
        """Health check should only match exact path."""
        middleware = HealthCheckMiddleware(get_response)

        request = HttpRequest()
        request.META = {"HTTP_HOST": "example.com"}
        request.path_info = "/-/health/extra"

        # This should proceed normally since it's not an exact match
        response = middleware(request)

        self.assertEqual(response.content, b"Normal response")

    @override_settings(ALLOWED_HOSTS=["example.com"])
    def test_health_check_path_without_trailing_slash(self):
        """Health check path without trailing slash should not match."""
        middleware = HealthCheckMiddleware(get_response)

        request = HttpRequest()
        request.META = {"HTTP_HOST": "example.com"}
        request.path_info = "/-/health"

        # This should proceed normally since path doesn't match exactly
        response = middleware(request)

        self.assertEqual(response.content, b"Normal response")
