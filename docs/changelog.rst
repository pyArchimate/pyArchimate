Changelog
=========

v1.3.0 (2026-05-01)
-------------------

**Major Release: Complete ArchiMate Notation Support (P3)**

This release adds comprehensive support for element hierarchy, visual styling, and junction type semantics with full round-trip XML preservation.

Element Hierarchy & Grouping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Parent-child relationships**: Organize elements into logical hierarchies with ``Model.add_child()``
- **Hierarchy queries**: Get parent, children, ancestors, descendants
- **Sibling queries**: Find elements with same parent via ``Model.get_siblings()``
- **Path-based queries**: Find elements by hierarchy path with wildcards ``Model.find_by_hierarchy_path()``
- **Automatic cycle detection**: Prevents invalid circular relationships
- **Maximum depth limit**: Prevents pathological nesting (default 5 levels)
- **Orphaning on deletion**: Children remain when parent is deleted

Visual Styling
~~~~~~~~~~~~~~

- **Color customization**: Set fill color and line color (hex or named colors)
- **Named color support**: Automatic conversion of 'red', 'blue', etc. to hex
- **Line width property**: Customize border width (pixels)
- **Transparency property**: Set opacity from 0.0 (transparent) to 1.0 (opaque)
- **Bulk styling**: Set multiple properties at once with ``Element.set_visual_style()``
- **Round-trip preservation**: All visual properties preserved in XML export/import

Junction Type Semantics
~~~~~~~~~~~~~~~~~~~~~~~

- **Junction validation**: AND, OR, XOR junction types for decision points
- **Type validation**: ``Element.set_junction_type()`` with validation
- **Semantic preservation**: Junction types preserved in round-trip export/import

Performance & Quality
~~~~~~~~~~~~~~~~~~~~~

- **677+ unit tests**: Comprehensive test coverage for all features
- **94% code coverage**: High coverage of new P3 code paths
- **<10ms query performance**: All queries <10ms even on 1000+ element models
- **Type safe**: Full mypy/pyright compliance
- **Zero breaking changes**: Fully backward compatible with v1.2.0

API Reference
~~~~~~~~~~~~~

- :doc:`hierarchy-styling-overview` - Overview of hierarchy, styling, and junction types
- :doc:`api/element` - Element class P3 API reference
- :doc:`api/model` - Model class P3 API reference
- :doc:`guides/element-hierarchy` - Hierarchy usage guide
- :doc:`guides/visual-styling` - Visual styling guide
- :doc:`guides/junction-types` - Junction type semantics

Documentation
~~~~~~~~~~~~~

- Comprehensive API documentation for all P3 methods
- User guides for hierarchy, styling, and junction types
- Working code examples for all features
- Quick reference card for fast lookup

v1.2.0 (2026-05-01)
-------------------

**ArchiMate v3.x Specification Compliance (P1+P2)**

- Complete ArchiMate v3.x specification compliance
- BusinessInteraction element support
- Influence strength round-trip preservation
- Relationship documentation preservation

v1.1.0 (2026-04-15)
-------------------

**SonarCloud Remediation**

- Resolved 18 open SonarCloud issues
- Code quality improvements
- Enhanced test coverage

v1.0.0 (2026-04-01)
-------------------

**Initial Release**

- Core ArchiMate model support
- XML import/export
- Basic element and relationship management
