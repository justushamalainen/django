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

    if os.environ.get("DJORM_DUMP_BAILS"):
        import atexit
        from djorm_django.patches import state as _djorm_state

        def _dump_bails():
            items = sorted(
                _djorm_state.fallback_reasons.items(), key=lambda kv: -kv[1]
            )
            print("\n=== djorm bail histogram ===")
            for reason, n in items:
                print(f"  {n:>8d}  {reason}")
            print(f"  --- total bails: {_djorm_state.fallback_calls} ---")

        atexit.register(_dump_bails)
