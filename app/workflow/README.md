# Mold Generation Workflow

Complete end-to-end workflow orchestration for ceramic mold generation.

## Overview

The `MoldWorkflow` class orchestrates the complete pipeline:

1. **Constraint Validation** - Verify draft angles and wall thickness
2. **NURBS Generation** - Fit exact surfaces from SubD limit
3. **Draft Transformation** - Apply demolding angles
4. **Export Serialization** - Package for Rhino import

## Usage

```python
from app.workflow.mold_generator import MoldWorkflow
from app.ui.mold_params_dialog import MoldParameters
from app.state.parametric_region import ParametricRegion
import cpp_core

# Initialize with SubD evaluator
cage = cpp_core.SubDControlCage()
# ... populate cage ...

evaluator = cpp_core.SubDEvaluator()
evaluator.initialize(cage)

# Create workflow
workflow = MoldWorkflow(evaluator)

# Define regions
regions = [
    ParametricRegion(
        id="region_0",
        faces=[0, 1, 2, 3],
        unity_principle="Curvature",
        unity_strength=0.9
    ),
    ParametricRegion(
        id="region_1",
        faces=[4, 5, 6, 7],
        unity_principle="Spectral",
        unity_strength=0.85
    )
]

# Set parameters
params = MoldParameters(
    draft_angle=2.0,          # degrees
    wall_thickness=40.0,       # mm
    demolding_direction=(0, 0, 1)  # +Z
)

# Generate molds
result = workflow.generate_molds(regions, params)

if result.success:
    print(f"Generated {len(result.nurbs_surfaces)} molds")
    print(f"Export data ready: {len(result.export_data['molds'])} surfaces")

    # Send to Rhino
    # bridge.send_molds(result.export_data)
else:
    print(f"Error: {result.error_message}")
    # Show constraint violations
    for report in result.constraint_reports:
        if report.has_errors():
            print(f"Region failed validation")
```

## Workflow Steps

### 1. Constraint Validation

Each region is validated against physical constraints:

- **Draft angles**: Minimum angle for demolding
- **Wall thickness**: Adequate plaster thickness
- **Undercuts**: No geometry blocking mold removal

If any region fails validation, the workflow stops and returns error details.

### 2. NURBS Surface Generation

For each valid region:

1. Sample exact limit surface at high density (50×50 grid)
2. Fit analytical NURBS surface through samples
3. Check fitting quality (max deviation < 0.1mm typical)
4. Warn if quality threshold exceeded

**Quality Metrics**:
- Max deviation: Should be < 0.1mm for precision work
- RMS error: Typically < 0.05mm

### 3. Draft Angle Application

Transform each NURBS surface:

1. Extract parting line (region boundary)
2. Apply angular transformation perpendicular to demolding direction
3. Maintain mathematical exactness throughout

Draft angles typically 0.5-2.0° for ceramic work.

### 4. Export Serialization

Package all molds for Rhino:

```json
{
  "type": "ceramic_mold_set",
  "version": "1.0",
  "molds": [
    {
      "degree_u": 3,
      "degree_v": 3,
      "control_points": [[x, y, z], ...],
      "weights": [w_0, w_1, ...],
      "knots_u": [u_0, u_1, ...],
      "knots_v": [v_0, v_1, ...],
      "region_id": "region_0"
    }
  ],
  "metadata": {
    "draft_angle": 2.0,
    "wall_thickness": 40.0,
    "demolding_direction": [0, 0, 1]
  },
  "timestamp": "2025-11-09T12:34:56"
}
```

## Result Structure

```python
@dataclass
class MoldGenerationResult:
    success: bool                    # Overall workflow success
    nurbs_surfaces: List             # Generated OpenCASCADE surfaces
    constraint_reports: List         # Validation results per region
    export_data: Dict                # JSON-serializable export package
    error_message: str = ""          # Error details if failed
```

## Error Handling

The workflow handles errors gracefully:

**Constraint Violations**:
```python
if not result.success:
    if "constraint violations" in result.error_message:
        # Region failed draft/thickness checks
        for report in result.constraint_reports:
            if report.has_errors():
                # Show which constraints failed
                print(report.get_error_summary())
```

**NURBS Fitting Issues**:
```python
# Warnings printed to console
# Workflow continues with lower quality fit
# User can inspect quality metrics
```

**Unexpected Errors**:
```python
if not result.success:
    print(f"Workflow error: {result.error_message}")
    # Exception caught and reported
    # No partial results returned
```

## Performance

**Typical Performance** (for standard vessel decomposition):

- 4-6 regions
- Validation: 50-100ms total
- NURBS fitting: 200-400ms per region
- Draft application: 100-200ms per region
- Serialization: 50-100ms total
- **Total: 1.5-3.0 seconds**

**Memory Usage**:
- ~10MB per mold (NURBS surface data)
- ~5MB for export package
- Total: 50-70MB for typical decomposition

## Integration

**Dependencies**:
- `cpp_core.SubDEvaluator` - Exact limit surface evaluation
- `cpp_core.NURBSMoldGenerator` - NURBS fitting and draft
- `cpp_core.ConstraintValidator` - Physical constraint checks
- `app.export.nurbs_serializer.NURBSSerializer` - Rhino export format
- `app.ui.mold_params_dialog.MoldParameters` - User parameters

**Used By**:
- Agent 56: Progress dialog (UI integration)
- Agent 57: Export tests (validation)
- UI actions: "Generate Molds" button

## Testing

Run workflow tests:

```bash
pytest tests/test_mold_workflow.py -v
```

**Test Coverage**:
- ✓ Successful workflow execution
- ✓ Constraint validation failure handling
- ✓ Exception handling
- ✓ Quality warning generation
- ✓ Export data structure validation
- ✓ Result dataclass functionality

**Integration Tests**:
- Full workflow with real geometry (requires cpp_core)
- Round-trip to Rhino and back
- Multi-region decomposition validation

## Architecture Notes

**Lossless Until Fabrication**:
- Regions defined in exact parameter space
- NURBS surfaces are analytical (not discretized)
- Only approximation is final G-code export
- Mathematical truth preserved throughout

**Progress Reporting**:
- Each step prints status to console
- Quality warnings highlight potential issues
- Comprehensive error messages for debugging

**Extensibility**:
- Easy to add new validation constraints
- Quality thresholds configurable
- Metadata can include arbitrary data
- Export format versioned for compatibility

## See Also

- `app/export/nurbs_serializer.py` - NURBS export implementation
- `app/ui/mold_params_dialog.py` - Parameter configuration UI
- `app/state/parametric_region.py` - Region definition
- `cpp_core/mold/nurbs_generator.*` - C++ NURBS implementation
- `cpp_core/constraints/validator.*` - C++ constraint validation
