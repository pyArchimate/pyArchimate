# Public API Contract: Feature 014

**Purpose**: Enumerate the public symbols that MUST remain importable with unchanged signatures
after the complexity refactoring. FR-002 prohibits any public API change.

**Scope**: The 8 files with SonarCloud `S3776` violations.

---

## `src/pyArchimate/model.py`

Public classes and functions that must not change signature or be removed:

`Model`, `add`, `add_child`, `add_profile`, `add_relationship`, `check_connection`,
`check_invalid_conn`, `check_invalid_nodes`, `conns`, `default_color`, `default_theme`,
`elements`, `embed_props`, `expand_props`, `filter_elements`, `filter_relationships`,
`filter_views`, `find_by_hierarchy_path`, `find_elements`, `find_relationships`, `find_views`,
`get_ancestors`, `get_children`, `get_depth`, `get_descendants`, `get_elements_by_viewpoint`,
`get_leaf_elements`, `get_or_create_element`, `get_or_create_relationship`, `get_or_create_view`,
`get_parent`, `get_profile`, `get_root_elements`, `get_siblings`, `get_viewpoints`,
`get_views_by_viewpoint`, `merge`, `nodes`, `profiles`, `prop`, `props`, `read`, `relationships`,
`remove_child`, `remove_prop`, `type`, `uuid`, `views`, `write`

---

## `src/pyArchimate/view/__init__.py`

Public classes and functions that must not change signature or be removed:

`Connection`, `Node`, `Point`, `Position`, `Profile`, `View`,
`access_type`, `add`, `add_bendpoint`, `add_connection`, `concept`, `conns`, `cx`, `cy`,
`default_color`, `del_bendpoint`, `delete`, `desc`, `dist`, `distribute_connections`, `duplicate`,
`fill_color`, `get_all_bendpoints`, `get_bendpoint`, `get_obj_pos`, `get_or_create_connection`,
`get_or_create_node`, `get_point_pos`, `getnodes`, `h`, `in_conns`, `influence_strength`,
`is_directed`, `is_inside`, `l_shape`, `model`, `move`, `name`, `nodes`, `out_conns`,
`primary_viewpoint`, `prop`, `props`, `ref`, `remove_all_bendpoints`, `remove_folder`,
`remove_prop`, `resize`, `rx`, `ry`, `s_shape`, `set_bendpoint`, `set_primary_viewpoint`,
`source`, `target`, `to_svg`, `type`, `uuid`, `view`, `w`, `x`, `y`

---

## `src/pyArchimate/view/layout/__init__.py`

Public functions that must not change signature or be removed:

`apply_format`, `apply_layout`, `auto_layout`, `auto_route`, `undo_layout`

---

## `src/pyArchimate/view/layout/layout_engine.py`

Public functions that must not change signature or be removed:

`apply_node_positions`, `assign_grid_cells`, `get_layer_priority`

---

## `src/pyArchimate/view/layout/export/svg_export.py`

Public class and functions that must not change signature or be removed:

`SVGExportService`, `add_nested_nodes`, `to_svg`, `transform_number`, `visit`

---

## `src/pyArchimate/view/layout/routing/segment_separation.py`

Public functions that must not change signature or be removed:

`detect_collinear_overlaps`, `displace_collinear_segments`, `remove_uturn_waypoints`

---

## `src/pyArchimate/readers/archimateReader.py`

Public functions that must not change signature or be removed:

`archimate_reader`

---

## `src/pyArchimate/readers/archiReader.py`

Public functions that must not change signature or be removed:

`archi_reader`

---

## Verification

After each file is refactored, run:

```bash
python3 -c "from pyArchimate.view.layout import apply_format, apply_layout, auto_layout, auto_route, undo_layout; print('OK')"
```

(Repeat for each file.) Any `ImportError` or `AttributeError` is a contract violation.
