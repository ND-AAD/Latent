# Mold Workflow Architecture

Visual reference for complete end-to-end workflow.

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
├─────────────────────────────────────────────────────────────────┤
│  • SubD Model (from Rhino via HTTP bridge)                      │
│  • Analysis Results (regions from lenses)                        │
│  • Mold Parameters (draft angle, thickness, direction)          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MOLD WORKFLOW                                 │
│                   (MoldWorkflow class)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: CONSTRAINT VALIDATION                                   │
│  ├─ cpp_core.ConstraintValidator                                │
│  ├─ Check draft angles (min 0.5-2.0°)                           │
│  ├─ Check wall thickness (min 30-100mm)                         │
│  ├─ Detect undercuts                                             │
│  └─ Generate validation reports                                  │
│     ├─ Success → Continue                                        │
│     └─ Failure → Return error with details                       │
│                                                                  │
│  Step 2: NURBS SURFACE GENERATION                                │
│  ├─ cpp_core.NURBSMoldGenerator                                 │
│  ├─ Sample exact limit surface (50×50 grid)                     │
│  ├─ Fit analytical NURBS through samples                        │
│  ├─ Check fitting quality                                        │
│  │   ├─ Max deviation < 0.1mm ✓                                 │
│  │   └─ Max deviation > 0.1mm ⚠ (warn but continue)             │
│  └─ Generate NURBS for each region                              │
│                                                                  │
│  Step 3: DRAFT TRANSFORMATION                                    │
│  ├─ cpp_core.NURBSMoldGenerator.apply_draft_angle()            │
│  ├─ Extract parting line (region boundary)                      │
│  ├─ Apply angular transformation                                 │
│  │   └─ Perpendicular to demolding direction                    │
│  └─ Maintain mathematical exactness                             │
│                                                                  │
│  Step 4: EXPORT SERIALIZATION                                   │
│  ├─ app.export.NURBSSerializer                                  │
│  ├─ Extract control points, weights, knots                      │
│  ├─ Package metadata (draft, thickness, direction)              │
│  └─ Create JSON export structure                                │
│                                                                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                  MOLD GENERATION RESULT                          │
├─────────────────────────────────────────────────────────────────┤
│  • success: bool                                                 │
│  • nurbs_surfaces: List[OpenCASCADE surface]                    │
│  • constraint_reports: List[ValidationReport]                   │
│  • export_data: Dict (JSON-serializable)                        │
│  • error_message: str                                            │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT ACTIONS                              │
├─────────────────────────────────────────────────────────────────┤
│  Success:                                                        │
│  ├─ Send export_data to Rhino (HTTP POST)                       │
│  ├─ Show success notification                                    │
│  └─ Optional: Preview NURBS in viewport                         │
│                                                                  │
│  Failure:                                                        │
│  ├─ Display error_message to user                               │
│  ├─ Show constraint violation details                           │
│  └─ Highlight failed regions in viewport                        │
└─────────────────────────────────────────────────────────────────┘
```

## Component Dependencies

```
MoldWorkflow
├── Requires:
│   ├── cpp_core.SubDEvaluator
│   │   └── Initialized with SubD control cage
│   ├── cpp_core.NURBSMoldGenerator(evaluator)
│   │   └── NURBS fitting and draft operations
│   ├── cpp_core.ConstraintValidator(evaluator)
│   │   └── Physical constraint validation
│   └── app.export.NURBSSerializer
│       └── NURBS → JSON serialization
│
├── Inputs:
│   ├── List[ParametricRegion]
│   │   ├── id: str
│   │   ├── faces: List[int]
│   │   ├── boundary: List[ParametricCurve]
│   │   └── unity_principle: str
│   └── MoldParameters
│       ├── draft_angle: float (degrees)
│       ├── wall_thickness: float (mm)
│       └── demolding_direction: (x, y, z)
│
└── Outputs:
    └── MoldGenerationResult
        ├── success: bool
        ├── nurbs_surfaces: List[OCCT surface]
        ├── constraint_reports: List[report]
        ├── export_data: Dict
        └── error_message: str
```

## Execution Timeline

```
Time    Step                          Component                   Output
────────────────────────────────────────────────────────────────────────
0ms     Start workflow               MoldWorkflow.generate_molds()

50ms    Validate region 0            ConstraintValidator         Report 0
100ms   Validate region 1            ConstraintValidator         Report 1
150ms   ...                          ...                         ...
200ms   Validation complete          All regions ✓               Continue

400ms   Generate NURBS for region 0  NURBSMoldGenerator         Surface 0
800ms   Generate NURBS for region 1  NURBSMoldGenerator         Surface 1
1200ms  ...                          ...                         ...
1500ms  NURBS generation complete    All surfaces ✓              Continue

1600ms  Apply draft to surface 0     NURBSMoldGenerator         Drafted 0
1700ms  Apply draft to surface 1     NURBSMoldGenerator         Drafted 1
1800ms  ...                          ...                         ...
1900ms  Draft application complete   All surfaces ✓              Continue

1950ms  Serialize mold set           NURBSSerializer            JSON data
2000ms  Export package ready         Complete ✓                  Return

────────────────────────────────────────────────────────────────────────
Total: ~2.0 seconds (4-6 regions)
```

## Error Handling Flow

```
Try:
    Validate regions
    ├─ Region has errors?
    │   ├─ YES → Return MoldGenerationResult(
    │   │         success=False,
    │   │         error_message="constraint violations")
    │   └─ NO → Continue

    Generate NURBS
    ├─ Quality check
    │   ├─ Deviation > 0.1mm? → Print warning, continue
    │   └─ Deviation ≤ 0.1mm → Continue

    Apply draft
    └─ Transform each surface

    Serialize export
    └─ Package all data

    Return MoldGenerationResult(success=True, ...)

Except Exception as e:
    Return MoldGenerationResult(
        success=False,
        error_message=str(e))
```

## Quality Metrics

### NURBS Fitting Quality

```
Quality Check:
├── Max Deviation: < 0.1mm (excellent)
│                  0.1-0.5mm (acceptable, warn)
│                  > 0.5mm (poor, but continue)
├── RMS Error: < 0.05mm typical
└── Mean Deviation: < 0.03mm typical
```

### Constraint Validation

```
Draft Angle:
├── Minimum: 0.5° (rigid plaster molds)
├── Recommended: 2.0° (standard)
└── Generous: 3-5° (easy demolding)

Wall Thickness:
├── Minimum: 30mm (small pieces)
├── Standard: 40mm (1.5-2 inches)
└── Heavy: 50-100mm (large vessels)

Undercuts:
├── Detected: Faces perpendicular or opposing demolding
└── Action: Fail validation, require region adjustment
```

## Memory Profile

```
Component                        Memory Usage
─────────────────────────────────────────────
SubDEvaluator                    ~5MB
NURBSMoldGenerator              ~2MB
ConstraintValidator             ~1MB
NURBS Surface (each)            ~10MB
Export Package                  ~5MB
─────────────────────────────────────────────
Total (6 regions):              ~70MB
```

## Integration Points

### UI Integration

```python
# In main window action handler
def on_generate_molds(self):
    # 1. Show parameter dialog
    dialog = MoldParametersDialog(self)
    if not dialog.exec():
        return  # User cancelled

    params = dialog.get_parameters()

    # 2. Create workflow
    workflow = MoldWorkflow(self.state.evaluator)

    # 3. Execute (optionally with progress dialog)
    result = workflow.generate_molds(
        self.state.regions,
        params
    )

    # 4. Handle result
    if result.success:
        self.bridge.post_molds(result.export_data)
        QMessageBox.information(self, "Success",
            f"Generated {len(result.nurbs_surfaces)} molds")
    else:
        QMessageBox.warning(self, "Error",
            result.error_message)
```

### Bridge Integration

```python
# In RhinoBridge
def post_molds(self, export_data: Dict):
    """Send NURBS molds to Grasshopper."""
    response = requests.post(
        f"{self.base_url}/molds",
        json=export_data
    )

    if response.status_code == 200:
        print("✓ Molds sent to Rhino")
    else:
        raise RuntimeError(f"Failed to send molds: {response.text}")
```

### Progress Reporting

```python
# Future: Add callbacks for progress updates
class MoldWorkflow:
    def __init__(self, evaluator, progress_callback=None):
        self.progress_callback = progress_callback

    def generate_molds(self, regions, params):
        # Report progress
        if self.progress_callback:
            self.progress_callback("Validating constraints...", 0.0)

        # ... validation ...

        if self.progress_callback:
            self.progress_callback("Generating NURBS...", 0.25)

        # ... etc ...
```

## See Also

- `/home/user/Latent/app/workflow/README.md` - Complete documentation
- `/home/user/Latent/app/workflow/example_usage.py` - Usage examples
- `/home/user/Latent/tests/test_mold_workflow.py` - Test suite
- Day 6 (Agent 46): ConstraintValidator implementation
- Day 7 (Agent 51): NURBSMoldGenerator implementation
- Agent 52: NURBSSerializer implementation
- Agent 54: MoldParameters dialog
