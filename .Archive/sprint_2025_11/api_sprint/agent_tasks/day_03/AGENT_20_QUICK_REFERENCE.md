# Agent 20 Quick Reference - SubDEdgePicker

## One-Line Summary
Advanced edge picker with tubular rendering, adjacency tracking, and multi-select for SubD Edge Mode.

---

## Quick Start

```python
from app.ui.pickers import SubDEdgePicker

# Create picker
picker = SubDEdgePicker(renderer, render_window)

# Setup for mesh
picker.setup_edge_extraction(subd_polydata)

# Pick edge
edge_id = picker.pick(screen_x, screen_y, add_to_selection=shift_held)

# Get selection
selected = picker.get_selected_edges()  # List[int]

# Cleanup
picker.cleanup()
```

---

## Key Features

| Feature | Implementation |
|---------|---------------|
| **Edge Extraction** | Extracts all edges from triangulated mesh |
| **Adjacency Map** | Tracks which triangles share each edge |
| **Boundary Detection** | Edges with 1 adjacent triangle = boundary |
| **Internal Detection** | Edges with 2+ adjacent triangles = internal |
| **Cyan Guide** | All edges shown as cyan tubes (0.0, 1.0, 1.0) |
| **Yellow Highlight** | Selected edges only as yellow tubes (1.0, 1.0, 0.0) |
| **Multi-Select** | Shift+Click to add/remove from selection |
| **Tolerance** | 0.01 screen space, 0.1 world space |

---

## Data Structures

### EdgeInfo
```python
edge_info.vertices           # Tuple[int, int] - sorted
edge_info.edge_id           # int
edge_info.adjacent_triangles # List[int]
edge_info.is_boundary       # bool
```

### SubDEdgePicker
```python
picker.edges                # Dict[int, EdgeInfo]
picker.edge_map            # Dict[Tuple[int,int], int]
picker.selected_edge_ids   # Set[int]
picker.guide_actor         # Cyan tubes (all edges)
picker.highlight_actor     # Yellow tubes (selected)
```

---

## Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `setup_edge_extraction(polydata)` | None | Extract edges from mesh |
| `pick(x, y, add_to_selection)` | Optional[int] | Pick edge at screen coords |
| `get_selected_edges()` | List[int] | Get selected edge IDs |
| `get_boundary_edges()` | List[int] | Get boundary edge IDs |
| `get_internal_edges()` | List[int] | Get internal edge IDs |
| `get_edge_info(edge_id)` | Optional[EdgeInfo] | Get edge information |
| `clear_selection()` | None | Clear all selections |
| `cleanup()` | None | Remove actors from renderer |

---

## Signals

```python
picker.edge_picked.connect(lambda eid: ...)           # int
picker.position_picked.connect(lambda x,y,z: ...)     # float, float, float
picker.selection_changed.connect(lambda edges: ...)   # List[int]
```

---

## Visual Appearance

```
Cyan Guide Tubes (all edges):
  Color: (0.0, 1.0, 1.0) cyan
  Opacity: 0.5
  Radius: 0.01
  Sides: 8

Yellow Highlight Tubes (selected only):
  Color: (1.0, 1.0, 0.0) yellow
  Opacity: 1.0
  Radius: 0.02
  Sides: 12
```

---

## Example Output

```
Extracting edges from mesh...
✅ Extracted 12 edges (4 boundary, 8 internal)
✅ Created edge polydata: 8 points, 12 lines
✅ Edge guide visualization created (cyan tubes)

Picked edge 5 (2, 7) at position (0.5, 0.3, 0.2)
➕ Added edge 5 to selection
Highlighting 1 selected edges: [5]
✅ Highlight updated

Picked edge 3 (1, 4) at position (0.2, 0.5, 0.1)
➕ Added edge 3 to selection
Highlighting 2 selected edges: [3, 5]
✅ Highlight updated

Selection cleared
```

---

## Integration Pattern

```python
# Setup
edge_picker = SubDEdgePicker(renderer, render_window)
edge_picker.setup_edge_extraction(mesh_polydata)

# Connect to edit manager
edge_picker.selection_changed.connect(
    lambda edges: edit_manager.update_edges(set(edges))
)

# Handle mouse clicks
def on_left_click(x, y):
    if current_mode == EditMode.EDGE:
        shift = modifiers & Qt.ShiftModifier
        edge_picker.pick(x, y, add_to_selection=shift)
```

---

## Testing

```bash
# Run structural tests (11 tests)
python -m pytest tests/test_edge_picker_structure.py -v

# All tests should pass ✅
```

---

## Files

```
app/ui/pickers/edge_picker.py        # 374 lines
tests/test_edge_picker_structure.py  # 201 lines
tests/test_edge_picker.py            # 415 lines
```

---

## Status

✅ **COMPLETE** - All success criteria met, all tests passing

---

## Quick Links

- **Implementation**: `/home/user/Latent/app/ui/pickers/edge_picker.py`
- **Tests**: `/home/user/Latent/tests/test_edge_picker_structure.py`
- **Integration Notes**: `AGENT_20_INTEGRATION_NOTES.md`
- **Completion Summary**: `AGENT_20_COMPLETION_SUMMARY.md`
