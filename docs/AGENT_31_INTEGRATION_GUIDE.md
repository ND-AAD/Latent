# Agent 31: Analysis Panel Integration Guide

## Quick Integration

### 1. Import the Panel
```python
from app.ui.analysis_panel import AnalysisPanel
```

### 2. Create and Add to UI
```python
# In your main window or parent widget
self.analysis_panel = AnalysisPanel()
layout.addWidget(self.analysis_panel)
```

### 3. Connect Signals
```python
# Listen for analysis requests
self.analysis_panel.analysis_requested.connect(self.run_analysis)

# Listen for lens changes
self.analysis_panel.lens_changed.connect(self.on_lens_changed)

# Listen for curvature type changes
self.analysis_panel.curvature_type_changed.connect(self.update_visualization)
```

### 4. Update with Curvature Data
```python
# After computing curvature
curvature_values = compute_curvature(subd_mesh)
self.analysis_panel.set_curvature_data(curvature_values, "mean")
```

---

## Complete Example

```python
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from app.ui.analysis_panel import AnalysisPanel
from app.geometry.curvature import MeshCurvatureEstimator
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout()
        central.setLayout(layout)

        # Create analysis panel
        self.analysis_panel = AnalysisPanel()
        layout.addWidget(self.analysis_panel)

        # Connect signals
        self.analysis_panel.analysis_requested.connect(self.run_analysis)
        self.analysis_panel.curvature_type_changed.connect(self.update_curvature_type)

        # Enable analysis when geometry is loaded
        self.analysis_panel.enable_analysis(True)

    def run_analysis(self, lens_type: str):
        """Handle analysis request"""
        print(f"Running {lens_type} analysis...")

        if lens_type == "Curvature":
            self.run_curvature_analysis()
        elif lens_type == "Spectral":
            self.run_spectral_analysis()
        # ... other lenses

    def run_curvature_analysis(self):
        """Run curvature analysis on loaded geometry"""
        # Show analyzing state
        self.analysis_panel.set_analyzing(True)

        # Get current mesh
        vertices, faces = self.get_current_mesh()

        # Compute curvature
        estimator = MeshCurvatureEstimator(vertices, faces)
        curvatures = estimator.compute_all_face_curvatures()

        # Get selected curvature type
        curv_type = self.analysis_panel.get_curvature_type()

        # Extract values
        if curv_type == "mean":
            values = np.array([c.mean for c in curvatures.values()])
        elif curv_type == "gaussian":
            values = np.array([c.gaussian for c in curvatures.values()])
        elif curv_type == "k1":
            values = np.array([c.principal_min for c in curvatures.values()])
        elif curv_type == "k2":
            values = np.array([c.principal_max for c in curvatures.values()])

        # Update panel with data
        self.analysis_panel.set_curvature_data(values, curv_type)

        # Apply visualization
        self.apply_curvature_visualization(values, curv_type)

        # Complete
        self.analysis_panel.set_analysis_complete(len(curvatures))

    def update_curvature_type(self, curv_type: str):
        """Handle curvature type change"""
        print(f"Switching to {curv_type} curvature")

        # Recompute and update visualization
        self.run_curvature_analysis()

    def apply_curvature_visualization(self, values: np.ndarray, curv_type: str):
        """Apply color mapping to 3D visualization"""
        colormap = self.analysis_panel.get_colormap()
        curv_range = self.analysis_panel.get_curvature_range()
        auto_range = self.analysis_panel.is_auto_range()

        if auto_range:
            vmin, vmax = values.min(), values.max()
        else:
            vmin, vmax = curv_range

        # Apply to VTK mesh
        # ... (implementation depends on your VTK setup)
        print(f"Applying {colormap} colormap with range [{vmin:.2f}, {vmax:.2f}]")

    def get_current_mesh(self):
        """Get current mesh vertices and faces"""
        # ... (return from your mesh data structure)
        pass
```

---

## Signal Reference

### analysis_requested(str)
**When**: User clicks "Analyze" button
**Payload**: Lens type ("Flow", "Spectral", "Curvature", "Topological")
**Action**: Run the corresponding analysis

```python
def on_analysis_requested(lens_type: str):
    if lens_type == "Curvature":
        # Compute curvature and update panel
        pass
```

### lens_changed(str)
**When**: User selects a different lens
**Payload**: New lens type
**Action**: Show/hide relevant controls, clear previous results

```python
def on_lens_changed(lens_type: str):
    if lens_type == "Curvature":
        # Show curvature visualization
        pass
    else:
        # Hide curvature visualization
        self.analysis_panel.clear_curvature_data()
```

### curvature_type_changed(str)
**When**: User changes curvature type (Mean/Gaussian/K1/K2)
**Payload**: Curvature type ("mean", "gaussian", "k1", "k2")
**Action**: Recompute and update visualization

```python
def on_curvature_type_changed(curv_type: str):
    # Extract different curvature values
    if curv_type == "mean":
        values = [c.mean for c in self.curvatures.values()]
    # ... update visualization
```

---

## Method Reference

### set_curvature_data(data, curvature_type)
Update panel with new curvature data
```python
panel.set_curvature_data(mean_curvatures, "mean")
```

### clear_curvature_data()
Clear all curvature data and reset histogram
```python
panel.clear_curvature_data()
```

### get_curvature_type() -> str
Get selected curvature type
```python
curv_type = panel.get_curvature_type()  # "mean", "gaussian", "k1", "k2"
```

### get_colormap() -> str
Get selected colormap
```python
colormap = panel.get_colormap()  # "coolwarm", "viridis", etc.
```

### get_curvature_range() -> (float, float)
Get min/max range for color mapping
```python
vmin, vmax = panel.get_curvature_range()
```

### is_auto_range() -> bool
Check if auto-range is enabled
```python
if panel.is_auto_range():
    vmin, vmax = data.min(), data.max()
else:
    vmin, vmax = panel.get_curvature_range()
```

### enable_analysis(enabled)
Enable/disable the Analyze button
```python
panel.enable_analysis(True)  # Enable when geometry loaded
panel.enable_analysis(False)  # Disable when no geometry
```

### set_analyzing(is_analyzing)
Show/hide progress indicator
```python
panel.set_analyzing(True)   # Show "Analyzing..."
# ... do work ...
panel.set_analyzing(False)  # Hide progress
```

### set_analysis_complete(num_regions)
Show completion message
```python
panel.set_analysis_complete(5)  # "Found 5 regions"
```

---

## Workflow Example

### Complete Analysis Workflow
```python
def run_complete_analysis(self):
    # 1. Set analyzing state
    self.panel.set_analyzing(True)

    # 2. Get user preferences
    curv_type = self.panel.get_curvature_type()
    colormap = self.panel.get_colormap()

    # 3. Compute curvature
    curvatures = self.compute_curvature(self.mesh)

    # 4. Extract values
    if curv_type == "mean":
        values = np.array([c.mean for c in curvatures])
    elif curv_type == "gaussian":
        values = np.array([c.gaussian for c in curvatures])
    # ... etc

    # 5. Update panel (shows histogram)
    self.panel.set_curvature_data(values, curv_type)

    # 6. Apply visualization
    self.apply_colormap(values, colormap)

    # 7. Complete
    self.panel.set_analysis_complete(len(curvatures))
```

---

## Best Practices

### 1. Always Check if Data Exists
```python
if self.panel.curvature_data is not None:
    # Safe to export or process
    pass
```

### 2. Use Auto-Range by Default
```python
# Auto-range is checked by default
# Only use manual range for specific cases
if self.panel.is_auto_range():
    # Compute from data
else:
    # Use user-specified range
```

### 3. Clear Data on Geometry Change
```python
def load_new_geometry(self, new_mesh):
    self.panel.clear_curvature_data()
    self.mesh = new_mesh
    self.panel.enable_analysis(True)
```

### 4. Handle Errors Gracefully
```python
try:
    curvatures = compute_curvature(mesh)
    self.panel.set_curvature_data(curvatures, "mean")
except Exception as e:
    self.panel.set_analysis_failed(str(e))
```

---

## Testing Your Integration

### Manual Test Checklist
1. [ ] Panel appears in UI
2. [ ] Curvature lens selected by default
3. [ ] Curvature controls visible
4. [ ] Can select different curvature types
5. [ ] Histogram updates with data
6. [ ] Can change colormap
7. [ ] Can toggle auto-range
8. [ ] Can export to CSV
9. [ ] Switching lenses hides curvature controls
10. [ ] Analyze button triggers analysis

### Code Test
```python
# Create panel
panel = AnalysisPanel()

# Set test data
data = np.random.normal(1.0, 0.1, 100)
panel.set_curvature_data(data, "mean")

# Verify
assert panel.curvature_data is not None
assert panel.get_curvature_type() == "mean"
assert panel.export_btn.isEnabled()
```

---

## Troubleshooting

### Issue: Histogram not displaying
**Solution**: Check that matplotlib is installed
```bash
pip install matplotlib
```

### Issue: Export button disabled
**Solution**: Ensure you've called `set_curvature_data()` first
```python
panel.set_curvature_data(data, "mean")  # Enables export
```

### Issue: Curvature controls not visible
**Solution**: Check that Curvature lens is selected
```python
# Programmatically select Curvature lens
button = panel.lens_buttons.button(2)  # Curvature is index 2
button.setChecked(True)
panel._on_lens_changed(2)
```

---

## Next Steps

After integrating the Analysis Panel:

1. **Connect to VTK Visualization** (Agent 29 task)
   - Use `get_colormap()` and `get_curvature_range()`
   - Apply to VTK scalar field

2. **Implement Differential Lens** (Agent 32 task)
   - Use curvature data for ridge/valley detection
   - Listen to `analysis_requested` signal

3. **Add More Lenses** (Future agents)
   - Spectral, Flow, Topological
   - Follow same pattern with lens-specific controls

---

**For questions or issues, refer to**: `/home/user/Latent/docs/AGENT_31_COMPLETION_SUMMARY.md`
