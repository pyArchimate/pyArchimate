"""Smoke test for auto-layout feature. Run from repo root: poetry run python examples/smoke_test.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pyArchimate.pyArchimate import Model
from src.pyArchimate.view.layout import apply_layout, LayoutConfig

FIXTURE = Path(__file__).parent.parent / "tests/fixtures/test1.archimate"
OUT_DIR = Path(__file__).parent

m = Model("smoke")
m.read(str(FIXTURE))

v = m.views[0]
print(f"View: {v.name}, nodes: {len(v.nodes)}, connections: {len(v.conns)}")

result = apply_layout(v)
print(f"Algorithm: {result.algorithm_used}")
print(f"Success:   {result.success}")
print(f"Time:      {result.layout_time_ms:.0f}ms")
print(f"Elements:  {result.elements_processed}, Connections: {result.connections_processed}")
print(f"Metrics:   {result.quality_metrics}")

out = OUT_DIR / "smoke_test.svg"
v.to_svg(str(out))
print(f"SVG written -> {out}")

result2 = apply_layout(v, LayoutConfig(algorithm="hierarchical"))
print(f"\nHierarchical: success={result2.success}, time={result2.layout_time_ms:.0f}ms")
out2 = OUT_DIR / "smoke_test_hierarchical.svg"
v.to_svg(str(out2))
print(f"SVG written -> {out2}")
