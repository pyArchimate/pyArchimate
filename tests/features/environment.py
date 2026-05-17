"""Behave environment hooks for BDD test setup/teardown."""


def before_scenario(context, scenario):
    """Reset context before each scenario to prevent test pollution."""
    # Clear any model or element state from previous scenarios
    if hasattr(context, "model"):
        delattr(context, "model")
    if hasattr(context, "elements"):
        delattr(context, "elements")
    if hasattr(context, "elem"):
        delattr(context, "elem")
    if hasattr(context, "view"):
        delattr(context, "view")
    if hasattr(context, "temp_file"):
        delattr(context, "temp_file")
    if hasattr(context, "temp_path"):
        delattr(context, "temp_path")
    if hasattr(context, "imported_model"):
        delattr(context, "imported_model")
    if hasattr(context, "current_element"):
        delattr(context, "current_element")
