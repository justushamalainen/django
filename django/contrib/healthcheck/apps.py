from django.apps import AppConfig
from django.contrib.healthcheck.checks import check_healthcheck_middleware
from django.core import checks
from django.utils.translation import gettext_lazy as _


class HealthCheckConfig(AppConfig):
    name = "django.contrib.healthcheck"
    verbose_name = _("Health Check")

    def ready(self):
        checks.register(check_healthcheck_middleware, checks.Tags.security)
