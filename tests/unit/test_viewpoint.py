"""Unit tests for Viewpoint entity and registry."""
from src.pyArchimate.viewpoint import Viewpoint
from src.pyArchimate.viewpoint_registry import STANDARD_VIEWPOINTS, get_viewpoint


def test_viewpoint_entity_creation():
    vp = Viewpoint(id='stakeholder', name='Stakeholder Viewpoint',
                   description='Shows stakeholder concerns')
    assert vp.id == 'stakeholder'
    assert vp.name == 'Stakeholder Viewpoint'
    assert vp.description == 'Shows stakeholder concerns'


def test_viewpoint_registry():
    assert len(STANDARD_VIEWPOINTS) == 13
    ids = [v.id for v in STANDARD_VIEWPOINTS]
    for slug in ['stakeholder', 'capability', 'organization', 'actor',
                 'technology', 'physical', 'service', 'implementation',
                 'migration', 'strategy', 'business', 'application',
                 'infrastructure']:
        assert slug in ids


def test_get_viewpoint_by_slug():
    vp = get_viewpoint('stakeholder')
    assert vp.id == 'stakeholder'


def test_get_viewpoint_unknown_returns_none():
    assert get_viewpoint('nonexistent') is None
