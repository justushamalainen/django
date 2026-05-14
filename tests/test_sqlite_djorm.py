"""Settings used to run Django's own test suite with djorm enabled.

Identical to ``test_sqlite`` except that the djorm monkey-patches are
installed at module import time.  Use via::

    DJORM_ENABLED=1 python tests/runtests.py --settings=test_sqlite_djorm <labels>
"""

import os

# Reuse the stock SQLite settings.
from test_sqlite import *  # noqa: F401, F403

# Install the patches before Django finishes setting up so the wrappers are
# in place by the time tests start importing models.
if os.environ.get("DJORM_ENABLED", "1").strip().lower() in ("1", "true", "yes", "on"):
    import djorm_django

    djorm_django.install_patches(enabled=True)
