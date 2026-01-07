"""
Django health check app that bypasses ALLOWED_HOSTS validation.

This app provides a health check endpoint that can be accessed by load balancers
and internal monitoring systems without requiring the Host header to match
ALLOWED_HOSTS.
"""

__all__ = ["HealthCheckMiddleware"]

from django.contrib.healthcheck.middleware import HealthCheckMiddleware

default_app_config = "django.contrib.healthcheck.apps.HealthCheckConfig"
