from src.pyArchimate.constants import RGBA


def test_rgba_color_setter():
    rgb = RGBA()
    rgb.color = '#1A2B3C'
    assert rgb.r == 0x1A
    assert rgb.g == 0x2B
    assert rgb.b == 0x3C


def test_rgba_color_setter_none_is_noop():
    rgb = RGBA(r=10, g=20, b=30)
    rgb.color = None
    assert rgb.r == 10
    assert rgb.g == 20
    assert rgb.b == 30
