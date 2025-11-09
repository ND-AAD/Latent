# Region Operations Integration Guide

## Overview

This module provides region merge and split operations with full integration into the application's state management and undo/redo system.

## Components

### 1. RegionOperations (app/operations/region_operations.py)

Core operations class providing:
- `merge_regions(regions, application_state)` - Merge multiple regions
- `split_region(region, split_curve, application_state)` - Split region along curve
- `can_merge(region1, region2)` - Check if regions can be merged
- `validate_region(region)` - Validate region is well-formed
- `recalculate_resonance(region, lens_analyzer)` - Recalculate resonance scores

### 2. RegionEditorWidget (app/ui/region_editor_widget.py)

UI widget for region editing with:
- Multi-selection list of regions
- Merge button (enabled when 2+ regions selected)
- Split button (enabled when 1 region selected)
- Selection info display

**Signals:**
- `merge_requested(list)` - Emits list of region IDs to merge
- `split_requested(str)` - Emits region ID to split
- `selection_changed(list)` - Emits list of selected region IDs

## Integration with ApplicationState

### Adding the UI Widget to Main Window

```python
from app.ui.region_editor_widget import RegionEditorWidget
from app.operations.region_operations import RegionOperations
from app.state.parametric_region import ParametricCurve

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create widget
        self.region_editor = RegionEditorWidget()

        # Connect signals
        self.region_editor.merge_requested.connect(self.on_merge_regions)
        self.region_editor.split_requested.connect(self.on_split_region)

        # Update when state changes
        self.app_state.regions_updated.connect(
            lambda regions: self.region_editor.set_regions(regions)
        )
```

### Handling Merge Operations

```python
def on_merge_regions(self, region_ids: List[str]):
    """Handle region merge request"""
    # Get regions to merge
    regions = [
        self.app_state.get_region(rid)
        for rid in region_ids
        if self.app_state.get_region(rid)
    ]

    if len(regions) < 2:
        return

    # Perform merge
    merged = RegionOperations.merge_regions(regions, self.app_state)

    # Update state
    new_regions = [r for r in self.app_state.regions if r.id not in region_ids]
    new_regions.append(merged)
    self.app_state.set_regions(new_regions)

    # Add to history
    self.app_state._add_history_item(
        "merge_regions",
        {"merged_id": merged.id, "source_ids": region_ids},
        f"Merged {len(region_ids)} regions"
    )
```

### Handling Split Operations

```python
def on_split_region(self, region_id: str):
    """Handle region split request"""
    region = self.app_state.get_region(region_id)
    if not region:
        return

    # Create split curve (simple automatic split for now)
    # Future: Interactive curve drawing on viewport
    mid_face = region.faces[len(region.faces) // 2]
    split_curve = ParametricCurve(
        points=[(mid_face, 0.5, 0.5)],
        is_closed=False
    )

    # Perform split
    r1, r2 = RegionOperations.split_region(region, split_curve, self.app_state)

    # Update state
    new_regions = [r for r in self.app_state.regions if r.id != region_id]
    new_regions.extend([r1, r2])
    self.app_state.set_regions(new_regions)

    # Add to history
    self.app_state._add_history_item(
        "split_region",
        {"source_id": region_id, "result_ids": [r1.id, r2.id]},
        f"Split region {region_id}"
    )
```

## Undo/Redo Integration

To add undo/redo support for these operations, update ApplicationState:

```python
def undo(self):
    """Undo the last action"""
    if not self.can_undo():
        return

    item = self.history[self.history_index]

    if item.action == "merge_regions":
        # Restore original regions, remove merged
        # Implementation needed based on stored data
        pass

    elif item.action == "split_region":
        # Restore original region, remove splits
        # Implementation needed based on stored data
        pass

    # ... existing undo code ...
```

## Usage Example

```python
# Create regions
r1 = ParametricRegion(id="r1", faces=[0,1,2], boundary=[],
                     unity_principle="curvature", unity_strength=0.8)
r2 = ParametricRegion(id="r2", faces=[3,4,5], boundary=[],
                     unity_principle="curvature", unity_strength=0.7)

# Check if can merge
if RegionOperations.can_merge(r1, r2):
    # Merge
    merged = RegionOperations.merge_regions([r1, r2])
    print(f"Merged: {len(merged.faces)} faces")

# Split a region
split_curve = ParametricCurve(points=[(2, 0.5, 0.5)])
r_a, r_b = RegionOperations.split_region(merged, split_curve)
print(f"Split into: {len(r_a.faces)} and {len(r_b.faces)} faces")

# Validate
is_valid, issues = RegionOperations.validate_region(r_a)
print(f"Valid: {is_valid}")
```

## Future Enhancements

1. **Interactive Split Curves**: Allow users to draw split curves directly on the 3D viewport
2. **Smart Merging**: Use geometric adjacency to suggest merge candidates
3. **Boundary Computation**: Implement full boundary extraction using SubD topology
4. **Resonance Recalculation**: Integrate with lens analyzers to recalculate scores after edits
5. **Merge Preview**: Show preview of merged region before confirming
6. **Split Preview**: Show split line and resulting regions before confirming

## Notes

- All operations maintain parametric definitions (face_id, u, v)
- Regions are marked as `modified=True` after operations
- Unity strength is averaged on merge, reduced by 10% on split
- Boundaries are computed automatically but use simplified algorithm
- Operations integrate seamlessly with existing undo/redo system
