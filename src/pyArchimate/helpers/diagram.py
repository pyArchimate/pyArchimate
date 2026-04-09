"""Diagram helper wrappers exposed as module-level utilities."""


def get_or_create_node(owner, *args, **kwargs):
    """Delegate node creation to Model/View helper methods."""
    return owner.get_or_create_node(*args, **kwargs)


def get_or_create_connection(owner, *args, **kwargs):
    """Delegate connection creation to View helper methods."""
    return owner.get_or_create_connection(*args, **kwargs)


__all__ = ["get_or_create_node", "get_or_create_connection"]
