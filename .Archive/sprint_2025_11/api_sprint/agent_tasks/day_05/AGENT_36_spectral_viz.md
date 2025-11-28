# Agent 36: Spectral Visualization

**Day**: 5
**Phase**: Phase 1a - Mathematical Analysis
**Duration**: 3-4 hours
**Estimated Cost**: $4-6 (60K tokens, Sonnet)

---

## Mission

Implement VTK visualization for eigenfunction values, nodal lines, and spectral decomposition results.

---

## Context

You are creating visualization tools for the Spectral Lens. Users need to see:
- Eigenfunction values mapped as colors on the surface
- Nodal lines (zero-crossings) as prominent curves
- Multiple eigenmodes simultaneously
- Interactive eigenmode selection

**Dependencies**:
- Agent 35: SpectralDecomposer (eigenfunction data)
- Day 2: VTK viewport system
- Day 3: Region visualization (color management)

---

## Deliverables

**Files to Create**:
1. `app/ui/spectral_viz_widget.py` (interactive controls)
2. `app/geometry/spectral_renderer.py` (VTK rendering)
3. `tests/test_spectral_viz.py` (tests)

---

## Requirements

### 1. Spectral Renderer (VTK Integration)

```python
# app/geometry/spectral_renderer.py

import vtk
import numpy as np
from typing import Optional
from app.analysis.spectral_decomposition import EigenMode


class SpectralRenderer:
    """
    VTK renderer for eigenfunction visualization.

    Displays:
    - Eigenfunction values as color map
    - Nodal lines (zero crossings) as tubes
    - Multiple modes with transparency blend
    """

    def __init__(self, renderer: vtk.vtkRenderer):
        self.renderer = renderer

        # Actors
        self.surface_actor: Optional[vtk.vtkActor] = None
        self.nodal_line_actor: Optional[vtk.vtkActor] = None

        # Color maps
        self.colormap = 'coolwarm'  # Diverging: blue-white-red

    def render_eigenfunction(self,
                            mesh: 'TessellationResult',
                            mode: EigenMode,
                            show_nodal_lines: bool = True):
        """
        Render eigenfunction as colored surface.

        Args:
            mesh: Tessellated mesh from SubDEvaluator
            mode: EigenMode to visualize
            show_nodal_lines: Draw zero-crossing curves
        """
        # Create polydata
        polydata = self._mesh_to_polydata(mesh)

        # Add eigenfunction as scalar field
        scalars = vtk.vtkFloatArray()
        scalars.SetName("eigenfunction")
        for value in mode.eigenfunction:
            scalars.InsertNextValue(value)

        polydata.GetPointData().SetScalars(scalars)

        # Mapper with color map
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.SetScalarRange(mode.eigenfunction.min(),
                             mode.eigenfunction.max())

        # Use diverging color map
        lut = self._create_colormap_lut(self.colormap)
        mapper.SetLookupTable(lut)

        # Surface actor
        if self.surface_actor:
            self.renderer.RemoveActor(self.surface_actor)

        self.surface_actor = vtk.vtkActor()
        self.surface_actor.SetMapper(mapper)
        self.renderer.AddActor(self.surface_actor)

        # Nodal lines
        if show_nodal_lines:
            self._render_nodal_lines(polydata, mode.eigenfunction)

    def _render_nodal_lines(self,
                           polydata: vtk.vtkPolyData,
                           eigenfunction: np.ndarray):
        """
        Extract and render zero-crossing contours.
        """
        # Contour filter at value=0
        contour = vtk.vtkContourFilter()
        contour.SetInputData(polydata)
        contour.SetValue(0, 0.0)  # Contour at zero
        contour.Update()

        # Tube filter for thick lines
        tubes = vtk.vtkTubeFilter()
        tubes.SetInputConnection(contour.GetOutputPort())
        tubes.SetRadius(0.01)
        tubes.SetNumberOfSides(8)
        tubes.Update()

        # Mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tubes.GetOutputPort())

        if self.nodal_line_actor:
            self.renderer.RemoveActor(self.nodal_line_actor)

        self.nodal_line_actor = vtk.vtkActor()
        self.nodal_line_actor.SetMapper(mapper)
        self.nodal_line_actor.GetProperty().SetColor(0, 0, 0)  # Black
        self.nodal_line_actor.GetProperty().SetLineWidth(3)

        self.renderer.AddActor(self.nodal_line_actor)

    def _create_colormap_lut(self, name: str) -> vtk.vtkLookupTable:
        """
        Create VTK lookup table for color mapping.

        'coolwarm': Blue (negative) → White (zero) → Red (positive)
        """
        lut = vtk.vtkLookupTable()
        lut.SetNumberOfColors(256)

        if name == 'coolwarm':
            for i in range(256):
                t = i / 255.0
                # Diverging: blue to white to red
                if t < 0.5:
                    # Blue to white
                    s = 2 * t
                    r, g, b = s, s, 1.0
                else:
                    # White to red
                    s = 2 * (t - 0.5)
                    r, g, b = 1.0, 1.0 - s, 1.0 - s

                lut.SetTableValue(i, r, g, b, 1.0)

        lut.Build()
        return lut

    def _mesh_to_polydata(self, mesh) -> vtk.vtkPolyData:
        """Convert TessellationResult to vtkPolyData."""
        points = vtk.vtkPoints()
        for v in mesh.vertices:
            points.InsertNextPoint(v[0], v[1], v[2])

        triangles = vtk.vtkCellArray()
        for tri in mesh.triangles:
            triangle = vtk.vtkTriangle()
            triangle.GetPointIds().SetId(0, tri[0])
            triangle.GetPointIds().SetId(1, tri[1])
            triangle.GetPointIds().SetId(2, tri[2])
            triangles.InsertNextCell(triangle)

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetPolys(triangles)

        return polydata

    def clear(self):
        """Remove all spectral visualization actors."""
        if self.surface_actor:
            self.renderer.RemoveActor(self.surface_actor)
            self.surface_actor = None
        if self.nodal_line_actor:
            self.renderer.RemoveActor(self.nodal_line_actor)
            self.nodal_line_actor = None
```

---

### 2. Interactive Widget

```python
# app/ui/spectral_viz_widget.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QSlider, QLabel, QCheckBox, QPushButton,
                             QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List
from app.analysis.spectral_decomposition import EigenMode


class SpectralVizWidget(QWidget):
    """
    Interactive controls for spectral visualization.

    Signals:
        mode_changed: Emitted when user selects different eigenmode
        nodal_lines_toggled: Emitted when nodal line visibility changes
    """

    mode_changed = pyqtSignal(int)  # mode_index
    nodal_lines_toggled = pyqtSignal(bool)  # show_lines

    def __init__(self, parent=None):
        super().__init__(parent)

        self.modes: List[EigenMode] = []
        self.current_mode_idx = 0

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Spectral Analysis")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Mode selector
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Eigenmode:"))

        self.mode_combo = QComboBox()
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_combo)

        layout.addLayout(mode_layout)

        # Eigenvalue display
        self.eigenvalue_label = QLabel("λ = 0.000")
        self.eigenvalue_label.setStyleSheet("color: #666; font-family: monospace;")
        layout.addWidget(self.eigenvalue_label)

        # Mode slider (alternative to combo)
        self.mode_slider = QSlider(Qt.Orientation.Horizontal)
        self.mode_slider.setMinimum(0)
        self.mode_slider.setMaximum(9)
        self.mode_slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.mode_slider)

        # Nodal lines checkbox
        self.nodal_check = QCheckBox("Show Nodal Lines")
        self.nodal_check.setChecked(True)
        self.nodal_check.toggled.connect(self.nodal_lines_toggled.emit)
        layout.addWidget(self.nodal_check)

        # Extract regions button
        self.extract_btn = QPushButton("Extract Regions from Mode")
        layout.addWidget(self.extract_btn)

        layout.addStretch()

    def set_modes(self, modes: List[EigenMode]):
        """
        Update available eigenmodes.
        """
        self.modes = modes

        # Update combo box
        self.mode_combo.clear()
        for i, mode in enumerate(modes):
            label = f"Mode {i}: λ={mode.eigenvalue:.4f}"
            if mode.multiplicity > 1:
                label += f" (×{mode.multiplicity})"
            self.mode_combo.addItem(label)

        # Update slider range
        self.mode_slider.setMaximum(len(modes) - 1)

        # Select first non-trivial mode (skip mode 0 = constant)
        if len(modes) > 1:
            self.set_current_mode(1)

    def set_current_mode(self, index: int):
        """Select eigenmode by index."""
        if 0 <= index < len(self.modes):
            self.current_mode_idx = index
            self.mode_combo.setCurrentIndex(index)
            self.mode_slider.setValue(index)

            # Update eigenvalue display
            eigenvalue = self.modes[index].eigenvalue
            self.eigenvalue_label.setText(f"λ = {eigenvalue:.6f}")

    def _on_mode_changed(self, index: int):
        self.current_mode_idx = index
        self.mode_slider.blockSignals(True)
        self.mode_slider.setValue(index)
        self.mode_slider.blockSignals(False)

        if index < len(self.modes):
            eigenvalue = self.modes[index].eigenvalue
            self.eigenvalue_label.setText(f"λ = {eigenvalue:.6f}")

        self.mode_changed.emit(index)

    def _on_slider_changed(self, value: int):
        self.mode_combo.blockSignals(True)
        self.mode_combo.setCurrentIndex(value)
        self.mode_combo.blockSignals(False)

        self._on_mode_changed(value)
```

---

## Testing

```python
# tests/test_spectral_viz.py

import pytest
import numpy as np
from PyQt6.QtWidgets import QApplication
from app.ui.spectral_viz_widget import SpectralVizWidget
from app.analysis.spectral_decomposition import EigenMode


@pytest.fixture(scope='session')
def qapp():
    """PyQt application for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestSpectralVizWidget:
    """Test spectral visualization widget."""

    def test_widget_creation(self, qapp):
        """Test widget initializes correctly."""
        widget = SpectralVizWidget()

        assert widget.mode_combo is not None
        assert widget.mode_slider is not None
        assert widget.nodal_check.isChecked()

    def test_set_modes(self, qapp):
        """Test setting eigenmodes."""
        widget = SpectralVizWidget()

        # Create fake modes
        modes = [
            EigenMode(eigenvalue=0.0, eigenfunction=np.zeros(100), index=0),
            EigenMode(eigenvalue=2.0, eigenfunction=np.random.randn(100), index=1),
            EigenMode(eigenvalue=6.0, eigenfunction=np.random.randn(100), index=2),
        ]

        widget.set_modes(modes)

        assert widget.mode_combo.count() == 3
        assert widget.mode_slider.maximum() == 2
        assert widget.current_mode_idx == 1  # Should skip mode 0

    def test_mode_selection(self, qapp):
        """Test mode selection emits signal."""
        widget = SpectralVizWidget()

        modes = [
            EigenMode(eigenvalue=0.0, eigenfunction=np.zeros(100), index=0),
            EigenMode(eigenvalue=2.0, eigenfunction=np.random.randn(100), index=1),
        ]
        widget.set_modes(modes)

        # Connect signal
        received_index = []
        widget.mode_changed.connect(lambda i: received_index.append(i))

        # Change mode
        widget.set_current_mode(1)

        assert len(received_index) > 0
        assert received_index[-1] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## Success Criteria

- [ ] SpectralRenderer renders eigenfunction colors
- [ ] Nodal lines extracted as zero-contours
- [ ] Color map diverging (blue-white-red)
- [ ] SpectralVizWidget has mode selector
- [ ] Mode slider and combo box synchronized
- [ ] Eigenvalue displayed correctly
- [ ] Nodal line toggle functional
- [ ] Tests pass

---

## Integration Notes

**Used by**: Main UI for spectral analysis display
**Uses**: Agent 35 (eigenfunction data), Day 2 VTK system

---

**Ready to begin!**
