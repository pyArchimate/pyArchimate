from src.pyArchimate.helpers.properties import (
    check_invalid_conn,
    check_invalid_nodes,
    embed_props,
    expand_props,
)


class DummyModel:
    def embed_props(self, remove_props=False):
        return ("embed", remove_props)

    def expand_props(self, clean_doc=True):
        return ("expand", clean_doc)

    def check_invalid_conn(self):
        return ["conn"]

    def check_invalid_nodes(self):
        return ["node"]


def test_embed_props_delegates_to_model():
    model = DummyModel()
    assert embed_props(model, remove_props=True) == ("embed", True)


def test_expand_props_delegates_to_model():
    model = DummyModel()
    assert expand_props(model, clean_doc=False) == ("expand", False)


def test_check_invalid_conn_delegates_to_model():
    model = DummyModel()
    assert check_invalid_conn(model) == ["conn"]


def test_check_invalid_nodes_delegates_to_model():
    model = DummyModel()
    assert check_invalid_nodes(model) == ["node"]
