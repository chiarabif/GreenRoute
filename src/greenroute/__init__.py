import sys

if sys.version_info[:2] >= (3, 8):
    from importlib.metadata import PackageNotFoundError, version
else:
    from importlib_metadata import PackageNotFoundError, version

try:
    dist_name = "GreenRoute"
    __version__ = version(dist_name)
except PackageNotFoundError:
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

# ── Auto-import all functions ──────────────────────────────────────────────────
from greenroute.FUNCTIONS.models    import *
from greenroute.FUNCTIONS.builder   import build_route, build_step, build_material
from greenroute.FUNCTIONS.cleaner   import *
from greenroute.FUNCTIONS.loader    import *
from greenroute.FUNCTIONS.main      import *
from greenroute.FUNCTIONS.metrics   import *
from greenroute.FUNCTIONS.validator import *
from greenroute.SMILES.SMILES       import *