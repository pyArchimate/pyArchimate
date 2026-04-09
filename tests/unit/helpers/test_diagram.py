from src.pyArchimate.helpers.diagram import get_or_create_connection, get_or_create_node


class DummyOwner:
    def __init__(self):
        self.calls = []

    def get_or_create_node(self, *args, **kwargs):
        self.calls.append(("node", args, kwargs))
        return "node-result"

    def get_or_create_connection(self, *args, **kwargs):
        self.calls.append(("connection", args, kwargs))
        return "connection-result"


def test_get_or_create_node_delegates_to_owner_method():
    owner = DummyOwner()
    result = get_or_create_node(owner, "arg")
    assert result == "node-result"
    assert owner.calls[0][0] == "node"


def test_get_or_create_connection_delegates_to_owner_method():
    owner = DummyOwner()
    result = get_or_create_connection(owner, "arg")
    assert result == "connection-result"
    assert owner.calls[0][0] == "connection"
