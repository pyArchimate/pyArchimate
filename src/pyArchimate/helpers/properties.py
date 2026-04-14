"""Property and validation helper wrappers for Model instances."""


def embed_props(model, remove_props=False):
    """Delegate property embedding to the model implementation."""
    return model.embed_props(remove_props=remove_props)


def expand_props(model, clean_doc=True):
    """Delegate property expansion to the model implementation."""
    return model.expand_props(clean_doc=clean_doc)


def check_invalid_conn(model):
    """Delegate invalid relationship checks to the model implementation."""
    return model.check_invalid_conn()


def check_invalid_nodes(model):
    """Delegate orphan node checks to the model implementation."""
    return model.check_invalid_nodes()


__all__ = ["embed_props", "expand_props", "check_invalid_conn", "check_invalid_nodes"]
