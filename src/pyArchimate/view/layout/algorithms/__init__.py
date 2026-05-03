"""Layout algorithms registry and factory."""

from .force_directed import ForceDirectedLayout

__all__ = ["get_algorithm", "list_algorithms", "register_algorithm"]

# Algorithm registry
_ALGORITHMS: dict = {}


def register_algorithm(name: str, algorithm_class: type) -> None:
    """Register a layout algorithm."""
    _ALGORITHMS[name] = algorithm_class


def get_algorithm(name: str) -> type:
    """Get a registered layout algorithm by name."""
    if name not in _ALGORITHMS:
        raise ValueError(f"Unknown algorithm: {name}")
    return _ALGORITHMS[name]


def list_algorithms() -> list:
    """List all registered algorithm names."""
    return list(_ALGORITHMS.keys())


# Register built-in algorithms
register_algorithm("force_directed", ForceDirectedLayout)
