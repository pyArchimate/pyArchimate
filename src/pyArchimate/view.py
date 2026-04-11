"""Modern facade for View/Node/Connection/Profile using legacy implementations.

This keeps a dedicated module path (`pyArchimate.view`) while reusing the
battle-tested legacy logic. A later phase can replace these shims with pure
modern implementations without changing import paths.
"""

try:
    from ._legacy import View as _LegacyView, Node as _LegacyNode, Connection as _LegacyConnection, Profile as _LegacyProfile
except ImportError:  # fallback for direct import style
    from _legacy import View as _LegacyView, Node as _LegacyNode, Connection as _LegacyConnection, Profile as _LegacyProfile

# Simple aliases for now; they inherit all behavior from legacy classes.
class View(_LegacyView):
    pass


class Node(_LegacyNode):
    pass


class Connection(_LegacyConnection):
    pass


class Profile(_LegacyProfile):
    pass


# Expose to legacy module so isinstance checks across modules stay compatible.
try:
    import src.pyArchimate._legacy as _legacy_module  # type: ignore
except Exception:
    try:
        import _legacy as _legacy_module  # type: ignore
    except Exception:
        _legacy_module = None

if _legacy_module:
    _legacy_module.View = View
    _legacy_module.Node = Node
    _legacy_module.Connection = Connection
    _legacy_module.Profile = Profile

__all__ = ["View", "Node", "Connection", "Profile"]
