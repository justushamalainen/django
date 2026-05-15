"""Settings used to run Django's own test suite with djorm enabled.

Identical to ``test_sqlite`` except that the djorm monkey-patches are
installed at module import time.  Use via::

    DJORM_ENABLED=1 python tests/runtests.py --settings=test_sqlite_djorm <labels>
"""

import os

# Reuse the stock SQLite settings.
from test_sqlite import *  # noqa: F401, F403

# Django 6.1's test source expects BigAutoField as the default; without
# this, ``models.W042`` (auto-created PK type) shows up in every
# system-check round and several model_inheritance tests trip on it.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Install the patches before Django finishes setting up so the wrappers are
# in place by the time tests start importing models.
if os.environ.get("DJORM_ENABLED", "1").strip().lower() in ("1", "true", "yes", "on"):
    import djorm_django

    djorm_django.install_patches(enabled=True)
