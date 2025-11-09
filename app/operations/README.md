# Region Operations Module

**Agent 37 - Day 5: Region Merge/Split Tools**

## Overview

This module provides tools for manipulating parametric regions through merge and split operations while maintaining the lossless parametric representation principle.

## Quick Start

```python
from app.operations import RegionOperations
from app.state.parametric_region import ParametricRegion, ParametricCurve

# Merge regions
merged = RegionOperations.merge_regions([region1, region2])

# Split region
split_curve = ParametricCurve(points=[(5, 0.5, 0.5)])
r1, r2 = RegionOperations.split_region(region, split_curve)

# Validate region
is_valid, issues = RegionOperations.validate_region(region)
```

## Files

- **region_operations.py** - Core operations (merge, split, validate)
- **INTEGRATION.md** - Integration guide with examples
- **demo_operations.py** - Interactive demonstration script
- **README.md** - This file

## Features

### Merge Operations
- Combine multiple regions into one
- Preserve pinned status
- Average unity strength
- Deduplicate overlapping faces
- Compute merged boundaries

### Split Operations
- Divide region along parametric curve
- Classify faces relative to split line
- Maintain region attributes
- Apply 10% resonance penalty for manual edits

### Validation
- Check for empty regions
- Validate unity strength range [0.0, 1.0]
- Detect duplicate faces
- Ensure well-formed regions

## Testing

Run the test suite:
```bash
pytest tests/test_region_operations.py -v
```

Run the demonstration:
```bash
python app/operations/demo_operations.py
```

## Integration

See `INTEGRATION.md` for complete integration guide with ApplicationState and UI.

Quick integration with UI:

```python
from app.ui.region_editor_widget import RegionEditorWidget

# Create widget
editor = RegionEditorWidget()

# Connect signals
editor.merge_requested.connect(self.handle_merge)
editor.split_requested.connect(self.handle_split)

# Update regions
editor.set_regions(app_state.regions)
```

## Parametric Preservation

All operations maintain parametric representation:
- Regions defined by face indices
- Boundaries as ParametricCurves in (face_id, u, v) space
- No conversion to mesh
- Lossless until fabrication export

## Success Criteria

✅ Merge combines face sets correctly
✅ Split divides regions
✅ Parametric definitions maintained
✅ UI signals work
✅ Tests pass (22/22)

## Next Steps

For subsequent agents:
1. Integrate RegionEditorWidget into main window
2. Add undo/redo support for merge/split operations
3. Implement interactive split curve drawing on viewport
4. Connect to lens analyzers for resonance recalculation
5. Enhance boundary computation with full SubD topology

## License

Part of the Ceramic Mold Analyzer project.
