# Ceramic Mold Analyzer - Developer Guide

**Version**: 0.5.0 (Phase 0 Complete)
**Last Updated**: November 10, 2025
**Target Audience**: Developers extending or contributing to the system

---

## Table of Contents

1. [Introduction](#introduction)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [C++ Core Development](#c-core-development)
5. [Python Layer Development](#python-layer-development)
6. [Adding New Features](#adding-new-features)
7. [Testing Guidelines](#testing-guidelines)
8. [Contributing Guidelines](#contributing-guidelines)
9. [Debugging and Troubleshooting](#debugging-and-troubleshooting)
10. [Performance Optimization](#performance-optimization)

---

## Introduction

The Ceramic Mold Analyzer is a hybrid C++/Python desktop application for discovering mathematical decompositions of subdivision surfaces to create slip-casting ceramic molds. This guide will help you understand the codebase and contribute effectively.

### Core Philosophy

**Lossless Until Fabrication**: The system maintains exact mathematical representation from input SubD through all analysis. Approximation occurs ONLY at the final G-code/STL export. See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

### Technology Stack

- **C++ Core**: OpenSubdiv 3.6+, OpenCASCADE 7.x, CMake, pybind11
- **Python Layer**: PyQt6 6.9.1, VTK 9.3.0, NumPy, SciPy, pytest
- **Build System**: CMake 3.20+, Python 3.11+
- **Version Control**: Git with feature branch workflow

---

## Development Setup

### Prerequisites

Before you begin, ensure you have:

1. **Python 3.11+** with virtual environment support
2. **CMake 3.20+** for C++ build configuration
3. **C++17 compiler** (GCC 9+, Clang 10+, or MSVC 2019+)
4. **OpenSubdiv 3.6+** for subdivision surface evaluation
5. **OpenCASCADE 7.x** for NURBS operations (optional but recommended)
6. **Git** for version control

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed installation instructions.

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/latent.git
cd latent

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-qt pytest-cov black flake8 mypy

# Build C++ core
cd cpp_core
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug ..  # Use Debug for development
make -j$(nproc)
cd ../..

# Verify installation
python3 -c "import cpp_core; print('C++ module OK')"
python3 launch.py  # Launch the application
```

### IDE Recommendations

#### For C++ Development

**Visual Studio Code**:
```json
// .vscode/settings.json
{
    "C_Cpp.default.configurationProvider": "ms-vscode.cmake-tools",
    "cmake.buildDirectory": "${workspaceFolder}/cpp_core/build",
    "C_Cpp.default.cppStandard": "c++17"
}
```

**CLion**: Open `cpp_core/CMakeLists.txt` as project root

**Xcode** (macOS):
```bash
cd cpp_core/build
cmake -G Xcode ..
open latent_cpp_core.xcodeproj
```

#### For Python Development

**VS Code**:
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true
}
```

**PyCharm**: Open project root, configure virtual environment interpreter

---

## Project Structure

### Directory Organization

```
Latent/                         # Project root
├── app/                        # Python application modules
│   ├── state/                 # State management
│   │   ├── app_state.py       # Central state manager
│   │   ├── edit_mode.py       # Edit mode management
│   │   ├── parametric_region.py # Region data structure
│   │   └── iteration_manager.py # Iteration tracking
│   ├── bridge/                # Rhino communication
│   │   └── rhino_bridge.py    # HTTP bridge client
│   ├── geometry/              # Geometry utilities
│   │   └── subd_display.py    # VTK display helpers
│   ├── ui/                    # User interface components
│   │   ├── viewport_3d.py     # 3D viewport widget
│   │   ├── viewport_layout.py # Multi-viewport manager
│   │   ├── region_list.py     # Region list UI
│   │   ├── edit_mode_toolbar.py # Edit mode selector
│   │   └── pickers/           # Sub-object pickers
│   ├── analysis/              # Analysis modules
│   │   ├── differential_decomposer.py # Curvature-based
│   │   └── spectral_decomposer.py     # Spectral analysis
│   ├── constraints/           # Constraint checking
│   │   └── constraint_manager.py # Validation logic
│   ├── workflow/              # High-level workflows
│   │   └── mold_workflow.py   # Mold generation
│   └── export/                # Export functionality
│       └── rhino_exporter.py  # Send to Rhino
├── cpp_core/                   # C++ geometry kernel
│   ├── geometry/              # Core geometry
│   │   ├── types.h            # Data structures
│   │   ├── subd_evaluator.h/cpp # OpenSubdiv wrapper
│   │   ├── nurbs_generator.h  # NURBS operations
│   │   ├── nurbs_fitting.cpp  # Surface fitting
│   │   ├── draft_transform.cpp # Draft angle transform
│   │   └── mold_solid.cpp     # Solid creation
│   ├── analysis/              # Mathematical analysis
│   │   └── curvature_analyzer.h/cpp # Curvature computation
│   ├── constraints/           # Validation
│   │   ├── constraint_validator.h # Validator interface
│   │   ├── undercut_detector.cpp  # Undercut detection
│   │   └── draft_checker.cpp      # Draft angle checking
│   ├── utils/                 # Utilities
│   │   └── mesh_mapping.cpp   # Display mesh creation
│   ├── python_bindings/       # pybind11 bindings
│   │   └── bindings.cpp       # Python interface
│   ├── tests/                 # Google Test unit tests
│   └── CMakeLists.txt         # Build configuration
├── tests/                      # Python tests
│   ├── test_app_state.py      # State management tests
│   ├── test_curvature.py      # Curvature analysis tests
│   ├── test_constraints.py    # Constraint tests
│   └── test_integration.py    # Integration tests
├── docs/                       # Documentation
│   ├── DEVELOPER_GUIDE.md     # This file
│   ├── ARCHITECTURE.md        # Architecture details
│   ├── API_REFERENCE.md       # API documentation
│   ├── BUILD_INSTRUCTIONS.md  # Build guide
│   └── reference/             # Specifications
├── rhino/                      # Grasshopper components
│   └── grasshopper_http_server_control_cage.py
├── main.py                     # Application entry point
├── launch.py                   # Quick launcher
├── setup.py                    # Python package setup
└── requirements.txt            # Python dependencies
```

### Module Responsibilities

| Module | Purpose | Language |
|--------|---------|----------|
| `cpp_core/geometry` | Exact SubD evaluation, NURBS operations | C++ |
| `cpp_core/analysis` | Mathematical analysis (curvature, etc.) | C++ |
| `cpp_core/constraints` | Validation and checking | C++ |
| `app/state` | Application state management | Python |
| `app/ui` | User interface components | Python |
| `app/analysis` | High-level analysis workflows | Python |
| `app/workflow` | Mold generation workflows | Python |
| `app/bridge` | Rhino communication | Python |

### Import Conventions

**Python imports always use `app/` prefix**:

```python
# Correct ✅
from app.state.app_state import ApplicationState
from app.ui.viewport_3d import Viewport3D
from app.bridge.rhino_bridge import RhinoBridge

# Wrong ❌
from ceramic_mold_analyzer.app.state.app_state import ApplicationState
```

**C++ module import**:

```python
# C++ module is named cpp_core
import cpp_core

# Access types
point = cpp_core.Point3D(1.0, 2.0, 3.0)
cage = cpp_core.SubDControlCage()
evaluator = cpp_core.SubDEvaluator()
```

---

## C++ Core Development

### OpenSubdiv Integration

The C++ core uses OpenSubdiv for exact limit surface evaluation. Key concepts:

**Subdivision Surface Evaluation**:
```cpp
#include "geometry/subd_evaluator.h"

// Create evaluator
SubDEvaluator evaluator;

// Build from control cage
SubDControlCage cage;
// ... populate cage with vertices and faces ...
bool success = evaluator.buildTopology(cage);

// Evaluate limit surface at parametric coordinate
int face_index = 0;
float u = 0.5f, v = 0.5f;
Point3D point = evaluator.evaluateLimit(face_index, u, v);

// Get normal
Vector3 normal = evaluator.evaluateNormal(face_index, u, v);

// Get derivatives
Vector3 du, dv;
evaluator.evaluateDerivatives(face_index, u, v, du, dv);
```

**Key Classes**:
- `SubDControlCage`: Control cage representation (vertices, faces, creases)
- `SubDEvaluator`: Wraps OpenSubdiv's TopologyRefiner for limit surface evaluation
- `TessellationResult`: Triangulated mesh for display (not used for analysis!)

### OpenCASCADE Usage

OpenCASCADE is used for NURBS operations and Boolean operations:

**NURBS Surface Fitting**:
```cpp
#include "geometry/nurbs_generator.h"

// Sample points from limit surface
std::vector<Point3D> points;
std::vector<Vector3 normals;
for (auto [u, v] : sample_grid) {
    points.push_back(evaluator.evaluateLimit(face, u, v));
    normals.push_back(evaluator.evaluateNormal(face, u, v));
}

// Fit NURBS surface
NURBSGenerator generator;
auto surface = generator.fitSurface(points, normals, u_degree, v_degree);
```

**Draft Angle Transformation**:
```cpp
#include "geometry/draft_transform.h"

// Apply draft angle to NURBS surface
DraftTransform transform;
Vector3 parting_direction(0, 0, 1);  // +Z
float draft_angle_degrees = 3.0f;
auto drafted_surface = transform.applyDraft(
    surface, parting_direction, draft_angle_degrees
);
```

### pybind11 Bindings

All C++ classes are exposed to Python via pybind11. To add a new class:

**In `cpp_core/python_bindings/bindings.cpp`**:
```cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "geometry/your_new_class.h"

namespace py = pybind11;

PYBIND11_MODULE(cpp_core, m) {
    // ... existing bindings ...

    // Add your new class
    py::class_<YourNewClass>(m, "YourNewClass")
        .def(py::init<>())
        .def("method_name", &YourNewClass::methodName)
        .def_readwrite("property", &YourNewClass::property);
}
```

**NumPy integration** (zero-copy):
```cpp
#include <pybind11/numpy.h>

// Return NumPy array without copying
py::array_t<float> getVertices() {
    return py::array_t<float>(
        {vertex_count, 3},           // Shape
        {3 * sizeof(float), sizeof(float)},  // Strides
        vertices.data(),             // Data pointer
        py::cast(*this)              // Owner (prevents deallocation)
    );
}
```

### Building and Testing C++

**Build commands**:
```bash
cd cpp_core/build

# Debug build (with symbols)
cmake -DCMAKE_BUILD_TYPE=Debug ..
make -j$(nproc)

# Release build (optimized)
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)

# Build with tests
cmake -DBUILD_TESTS=ON ..
make -j$(nproc)
```

**Run C++ tests**:
```bash
# Google Test unit tests
cd cpp_core/build
ctest --output-on-failure

# Or run individual test executable
./tests/test_subd_evaluator
./tests/test_curvature
```

**Debugging with GDB**:
```bash
cd cpp_core/build
gdb ./tests/test_subd_evaluator
(gdb) break SubDEvaluator::evaluateLimit
(gdb) run
(gdb) backtrace
```

---

## Python Layer Development

### UI Framework (PyQt6)

The application uses PyQt6 for the user interface. Key patterns:

**Creating a new widget**:
```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal

class MyWidget(QWidget):
    # Define signals
    button_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout()
        self.button = QPushButton("Click Me")
        layout.addWidget(self.button)
        self.setLayout(layout)

    def _connect_signals(self):
        self.button.clicked.connect(self._on_button_clicked)

    def _on_button_clicked(self):
        self.button_clicked.emit("Button was clicked!")
```

**Using VTK for 3D visualization**:
```python
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtkmodules.vtkRenderingCore as vtk_render

class MyViewport(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create VTK widget
        self.vtk_widget = QVTKRenderWindowInteractor(self)

        # Setup renderer
        self.renderer = vtk_render.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)

        # Add actors
        actor = self._create_geometry_actor()
        self.renderer.AddActor(actor)

    def _create_geometry_actor(self):
        # Create VTK pipeline
        # ...
        return actor
```

### State Management

**ALWAYS go through ApplicationState** for state changes:

```python
from app.state.app_state import ApplicationState

class MyFeature:
    def __init__(self, state: ApplicationState):
        self.state = state

        # Connect to state signals
        self.state.regions_updated.connect(self._on_regions_updated)
        self.state.state_changed.connect(self._on_state_changed)

    def modify_region(self, region_id: str):
        # Correct ✅ - goes through state manager
        self.state.set_region_pinned(region_id, True)

        # Wrong ❌ - bypasses signals and history
        # region.pinned = True

    def _on_regions_updated(self, regions):
        # React to state changes
        print(f"Regions updated: {len(regions)} regions")
```

**State management principles**:
1. All state modifications go through `ApplicationState`
2. Use signals for reactive updates
3. State changes automatically add to undo/redo history
4. Never modify data structures directly

### Analysis Modules

Analysis modules process geometry and discover regions:

```python
from typing import List
from app.state.parametric_region import ParametricRegion
import cpp_core

class MyAnalysisModule:
    """Custom analysis module for region discovery"""

    def analyze(self, evaluator: cpp_core.SubDEvaluator) -> List[ParametricRegion]:
        """
        Analyze geometry and discover regions.

        Args:
            evaluator: SubD evaluator with loaded geometry

        Returns:
            List of discovered parametric regions
        """
        regions = []

        # Query exact limit surface
        for face_idx in range(evaluator.getFaceCount()):
            # Sample the surface
            for u in np.linspace(0, 1, 10):
                for v in np.linspace(0, 1, 10):
                    point = evaluator.evaluateLimit(face_idx, u, v)
                    normal = evaluator.evaluateNormal(face_idx, u, v)

                    # Analyze curvature
                    k1, k2 = self._compute_principal_curvatures(evaluator, face_idx, u, v)

                    # Classify region based on analysis
                    # ...

        return regions

    def _compute_principal_curvatures(self, evaluator, face_idx, u, v):
        # Use C++ curvature analyzer
        analyzer = cpp_core.CurvatureAnalyzer()
        result = analyzer.analyzeCurvature(evaluator, face_idx, u, v)
        return result.k1, result.k2
```

### Testing with pytest

Write tests for all Python modules:

```python
# tests/test_my_feature.py
import pytest
from app.state.app_state import ApplicationState
from app.my_module import MyFeature

@pytest.fixture
def app_state():
    """Fixture providing clean ApplicationState"""
    return ApplicationState()

@pytest.fixture
def my_feature(app_state):
    """Fixture providing MyFeature instance"""
    return MyFeature(app_state)

def test_basic_functionality(my_feature):
    """Test basic feature works"""
    result = my_feature.do_something()
    assert result is not None

def test_state_integration(my_feature, app_state):
    """Test integration with application state"""
    my_feature.modify_region("region-1")

    # Verify state was updated
    assert app_state.get_region("region-1").pinned is True

    # Verify history was added
    assert len(app_state.history) > 0
```

**Run tests**:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_my_feature.py

# Run tests matching pattern
pytest -k "test_curvature"
```

---

## Adding New Features

### Creating a New Mathematical Lens

A "lens" is a mathematical analysis method that discovers regions. To add a new lens:

#### 1. Define the C++ Analysis (if needed)

If your lens requires intensive computation, implement in C++:

```cpp
// cpp_core/analysis/my_lens_analyzer.h
#pragma once
#include "geometry/subd_evaluator.h"

namespace latent {

struct MyLensResult {
    float metric;
    std::vector<int> regions;
};

class MyLensAnalyzer {
public:
    MyLensResult analyze(const SubDEvaluator& evaluator, int face_index, float u, float v);
};

}  // namespace latent
```

```cpp
// cpp_core/analysis/my_lens_analyzer.cpp
#include "my_lens_analyzer.h"

namespace latent {

MyLensResult MyLensAnalyzer::analyze(const SubDEvaluator& evaluator, int face_index, float u, float v) {
    MyLensResult result;

    // Evaluate limit surface
    Point3D point = evaluator.evaluateLimit(face_index, u, v);
    Vector3 normal = evaluator.evaluateNormal(face_index, u, v);

    // Compute your metric
    result.metric = compute_my_metric(point, normal);

    return result;
}

}  // namespace latent
```

Add Python bindings in `cpp_core/python_bindings/bindings.cpp`:

```cpp
py::class_<MyLensAnalyzer>(m, "MyLensAnalyzer")
    .def(py::init<>())
    .def("analyze", &MyLensAnalyzer::analyze);

py::class_<MyLensResult>(m, "MyLensResult")
    .def_readonly("metric", &MyLensResult::metric)
    .def_readonly("regions", &MyLensResult::regions);
```

#### 2. Create Python Decomposer

```python
# app/analysis/my_lens_decomposer.py
from typing import List
import numpy as np
import cpp_core
from app.state.parametric_region import ParametricRegion

class MyLensDecomposer:
    """
    My custom lens for region discovery.

    This lens discovers regions based on [your metric].
    """

    def __init__(self):
        self.analyzer = cpp_core.MyLensAnalyzer()

    def decompose(self, evaluator: cpp_core.SubDEvaluator,
                  target_regions: int = 4) -> List[ParametricRegion]:
        """
        Decompose SubD into regions using my lens.

        Args:
            evaluator: SubD evaluator with loaded geometry
            target_regions: Desired number of regions

        Returns:
            List of discovered parametric regions
        """
        regions = []

        # Sample the surface and compute metrics
        metrics = self._compute_metrics(evaluator)

        # Cluster into regions
        region_assignments = self._cluster_regions(metrics, target_regions)

        # Convert to ParametricRegion objects
        for region_id in range(target_regions):
            region = self._create_region(region_id, region_assignments, evaluator)
            regions.append(region)

        return regions

    def _compute_metrics(self, evaluator):
        """Compute lens metric across surface"""
        # Implementation
        pass

    def _cluster_regions(self, metrics, target_regions):
        """Cluster surface into regions"""
        # Use sklearn, scipy, or custom clustering
        pass

    def _create_region(self, region_id, assignments, evaluator):
        """Create ParametricRegion from assignments"""
        region = ParametricRegion()
        region.id = f"my-lens-region-{region_id}"
        region.name = f"My Lens Region {region_id + 1}"
        region.lens_type = "MyLens"

        # Add parametric coordinates
        # region.add_point(face_idx, u, v)

        return region
```

#### 3. Register in UI

Add to analysis panel in `app/ui/analysis_panel.py`:

```python
# Add to lens combo box
self.lens_combo.addItem("My Lens", "MyLens")

# Handle lens selection
def _on_analyze_clicked(self):
    lens_type = self.lens_combo.currentData()

    if lens_type == "MyLens":
        from app.analysis.my_lens_decomposer import MyLensDecomposer
        decomposer = MyLensDecomposer()
        regions = decomposer.decompose(self.evaluator, target_regions=4)
        self.state.set_regions(regions)
```

#### 4. Write Tests

```python
# tests/test_my_lens.py
import pytest
import cpp_core
from app.analysis.my_lens_decomposer import MyLensDecomposer

def test_my_lens_basic():
    """Test basic lens functionality"""
    decomposer = MyLensDecomposer()

    # Create test geometry
    evaluator = create_test_subd()

    # Decompose
    regions = decomposer.decompose(evaluator, target_regions=4)

    # Verify
    assert len(regions) == 4
    assert all(r.lens_type == "MyLens" for r in regions)

def test_my_lens_metric():
    """Test metric computation"""
    analyzer = cpp_core.MyLensAnalyzer()
    evaluator = create_test_subd()

    result = analyzer.analyze(evaluator, 0, 0.5, 0.5)
    assert result.metric > 0
```

### Extending Constraint Validators

To add a new constraint check:

#### 1. C++ Implementation

```cpp
// cpp_core/constraints/my_constraint_checker.h
#pragma once
#include "constraint_validator.h"

namespace latent {

class MyConstraintChecker {
public:
    ConstraintReport checkConstraint(
        const SubDEvaluator& evaluator,
        const ParametricRegion& region,
        float threshold
    );
};

}  // namespace latent
```

#### 2. Python Integration

```python
# app/constraints/constraint_manager.py
from app.constraints.my_constraint import MyConstraintChecker

class ConstraintManager:
    def check_all_constraints(self, evaluator, regions):
        results = []

        # Add your constraint check
        for region in regions:
            result = self.my_checker.checkConstraint(evaluator, region, threshold)
            results.append(result)

        return results
```

### Adding UI Components

To add a new UI panel:

```python
# app/ui/my_panel.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal

class MyPanel(QWidget):
    """Custom panel for my feature"""

    # Signals
    value_changed = pyqtSignal(float)

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("My Panel")
        layout.addWidget(self.label)
        self.setLayout(layout)

    def _connect_signals(self):
        # Connect to application state
        self.state.state_changed.connect(self._update_display)

    def _update_display(self):
        # Update UI based on state
        pass
```

Add to main window in `main.py`:

```python
from app.ui.my_panel import MyPanel

# In MainWindow.__init__
self.my_panel = MyPanel(self.state)
self.right_dock.addWidget(self.my_panel)
```

---

## Testing Guidelines

### Test Organization

```
tests/
├── test_app_state.py          # State management tests
├── test_curvature.py          # Curvature analysis tests
├── test_constraints.py        # Constraint validation tests
├── test_differential.py       # Differential lens tests
├── test_spectral.py           # Spectral lens tests
├── test_nurbs.py              # NURBS generation tests
├── test_integration.py        # Integration tests
└── fixtures/
    ├── test_geometry.py       # Geometry fixtures
    └── test_data.py           # Test data fixtures
```

### Writing Good Tests

**Unit tests** - Test individual functions/classes:
```python
def test_region_creation():
    """Test parametric region creation"""
    region = ParametricRegion()
    region.id = "test-region"
    region.name = "Test Region"

    assert region.id == "test-region"
    assert region.name == "Test Region"
    assert len(region.parametric_coords) == 0
```

**Integration tests** - Test component interaction:
```python
def test_analysis_workflow(app_state):
    """Test complete analysis workflow"""
    # Load geometry
    evaluator = load_test_geometry()
    app_state.set_subd_geometry(evaluator)

    # Run analysis
    decomposer = DifferentialDecomposer()
    regions = decomposer.decompose(evaluator)
    app_state.set_regions(regions)

    # Verify results
    assert len(app_state.regions) > 0
    assert app_state.regions[0].lens_type == "Differential"
```

**Fixtures** for reusable test data:
```python
@pytest.fixture
def test_cube_subd():
    """Fixture providing cube SubD for testing"""
    cage = cpp_core.SubDControlCage()

    # Define cube vertices
    vertices = [
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
    ]

    for v in vertices:
        cage.vertices.append(cpp_core.Point3D(v[0], v[1], v[2]))

    # Define cube faces
    cage.faces = [
        [0, 1, 2, 3], [4, 5, 6, 7],  # Top, bottom
        [0, 1, 5, 4], [2, 3, 7, 6],  # Front, back
        [0, 3, 7, 4], [1, 2, 6, 5]   # Left, right
    ]

    evaluator = cpp_core.SubDEvaluator()
    evaluator.buildTopology(cage)

    return evaluator
```

### Test Coverage

Aim for high test coverage:

```bash
# Generate coverage report
pytest --cov=app --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

Target coverage:
- **Core functionality**: 90%+ coverage
- **UI components**: 70%+ coverage (harder to test)
- **Integration workflows**: 80%+ coverage

---

## Contributing Guidelines

### Code Style

#### Python Style

Follow **PEP 8** with these specifics:

```python
# Use 4 spaces for indentation
# Line length: 100 characters (not 79)
# Use double quotes for strings

# Good class naming
class MyClass:
    """Docstring describing the class."""

    def my_method(self, arg1: str, arg2: int) -> bool:
        """
        Method docstring.

        Args:
            arg1: Description of arg1
            arg2: Description of arg2

        Returns:
            Description of return value
        """
        return True

# Use type hints
def process_regions(regions: List[ParametricRegion]) -> Dict[str, Any]:
    pass

# Format with black
# Check with flake8
```

Run formatters:
```bash
# Format code
black app/ tests/

# Check style
flake8 app/ tests/

# Type checking
mypy app/
```

#### C++ Style

Follow **Google C++ Style Guide** with these specifics:

```cpp
// Use 4 spaces for indentation
// Use camelCase for methods, snake_case for variables
// Use PascalCase for classes

class MyClass {
public:
    MyClass();

    // Method documentation
    /**
     * @brief Process the geometry
     * @param evaluator SubD evaluator
     * @return Processing result
     */
    Result processGeometry(const SubDEvaluator& evaluator);

private:
    int vertex_count_;  // Member variables end with underscore
    std::vector<Point3D> points_;
};

// Use const references for large objects
void processData(const std::vector<Point3D>& points);

// Use smart pointers
std::unique_ptr<MyClass> obj = std::make_unique<MyClass>();
```

Format with clang-format:
```bash
cd cpp_core
clang-format -i geometry/*.cpp geometry/*.h
```

### Git Workflow

Use **feature branch workflow**:

```bash
# Create feature branch
git checkout -b feature/my-new-lens

# Make changes and commit
git add app/analysis/my_lens.py
git commit -m "feat: Add My Lens analyzer

- Implement metric computation
- Add clustering algorithm
- Add tests with 90% coverage
"

# Push to remote
git push origin feature/my-new-lens

# Create pull request on GitHub
```

**Commit message format**:
```
<type>: <short summary>

<detailed description>

<breaking changes if any>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Pull Request Process

1. **Before submitting**:
   - Run all tests: `pytest`
   - Check code style: `black . && flake8`
   - Build C++ code: `cd cpp_core/build && make`
   - Update documentation if needed

2. **PR description should include**:
   - What problem does this solve?
   - What changes were made?
   - How was it tested?
   - Screenshots (for UI changes)

3. **Code review checklist**:
   - Tests pass and coverage is adequate
   - Code follows style guidelines
   - Documentation is updated
   - No breaking changes (or clearly documented)
   - Performance implications considered

4. **After approval**:
   - Squash commits if needed
   - Merge to main branch
   - Delete feature branch

### Documentation Standards

**Document all public APIs**:

```python
def analyze_curvature(evaluator: cpp_core.SubDEvaluator,
                     threshold: float = 0.1) -> List[Region]:
    """
    Analyze surface curvature and discover regions.

    Uses principal curvature analysis to identify regions of similar
    curvature characteristics. Regions are bounded by curvature
    discontinuities exceeding the threshold.

    Args:
        evaluator: SubD evaluator with loaded geometry
        threshold: Curvature difference threshold (radians)

    Returns:
        List of discovered regions with curvature data

    Raises:
        ValueError: If threshold is negative
        RuntimeError: If evaluator has no geometry

    Example:
        >>> evaluator = load_geometry_from_rhino()
        >>> regions = analyze_curvature(evaluator, threshold=0.2)
        >>> print(f"Found {len(regions)} regions")
    """
    pass
```

**Update docs when**:
- Adding new features
- Changing APIs
- Adding dependencies
- Modifying build process

---

## Debugging and Troubleshooting

### Python Debugging

**Using pdb**:
```python
import pdb

def my_function():
    x = compute_something()
    pdb.set_trace()  # Breakpoint here
    y = process(x)
    return y
```

**Using VS Code debugger**:
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "Launch Application",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/launch.py",
            "console": "integratedTerminal"
        }
    ]
}
```

### C++ Debugging

**Using GDB**:
```bash
cd cpp_core/build
gdb --args python3 ../../main.py

(gdb) break SubDEvaluator::evaluateLimit
(gdb) run
(gdb) backtrace
(gdb) print variable_name
(gdb) continue
```

**Using LLDB** (macOS):
```bash
lldb -- python3 main.py
(lldb) breakpoint set -n SubDEvaluator::evaluateLimit
(lldb) run
(lldb) bt
(lldb) frame variable
```

### Common Issues

**Issue: C++ module import fails**
```
ImportError: No module named 'cpp_core'
```

Solution:
```bash
# Ensure build completed
cd cpp_core/build
make

# Check module was built
ls *.so  # Linux: cpp_core.*.so
ls *.dylib  # macOS: cpp_core.*.so

# Add to PYTHONPATH
export PYTHONPATH=/path/to/latent/cpp_core/build:$PYTHONPATH
python3 -c "import cpp_core; print('OK')"
```

**Issue: VTK rendering issues**
```
QVTKRenderWindowInteractor: Could not find QtGui application
```

Solution: Use `launch.py` instead of `main.py` directly, or set:
```bash
export QT_QPA_PLATFORM_PLUGIN_PATH=$(python -c "import PyQt6; print(PyQt6.__path__[0])")/Qt6/plugins
```

**Issue: OpenSubdiv not found**
```
CMake Error: OpenSubdiv not found!
```

Solution:
```bash
# macOS
brew install opensubdiv

# Linux
sudo apt-get install libosd-dev

# Or specify path
cmake -DCMAKE_PREFIX_PATH=/path/to/opensubdiv ..
```

---

## Performance Optimization

### Profiling Python Code

**Using cProfile**:
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
decomposer.decompose(evaluator)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

**Using line_profiler**:
```bash
pip install line_profiler

# Add @profile decorator to function
@profile
def my_function():
    pass

# Run profiler
kernprof -l -v script.py
```

### Profiling C++ Code

**Using Valgrind** (Linux):
```bash
valgrind --tool=callgrind ./test_subd_evaluator
kcachegrind callgrind.out.*
```

**Using Instruments** (macOS):
```bash
instruments -t "Time Profiler" ./test_subd_evaluator
```

### Optimization Tips

1. **Use C++ for heavy computation**: Move expensive operations to C++
2. **Batch operations**: Process multiple points in one C++ call
3. **Cache results**: Store expensive computations
4. **Use NumPy**: Vectorize operations when possible
5. **Profile first**: Measure before optimizing

**Example - Batch evaluation**:
```cpp
// Instead of many individual calls:
for (int i = 0; i < 1000; i++) {
    Point3D p = evaluator.evaluateLimit(face, u[i], v[i]);
}

// Batch evaluate:
std::vector<Point3D> evaluateMany(
    int face_index,
    const std::vector<float>& u_coords,
    const std::vector<float>& v_coords
) {
    std::vector<Point3D> results;
    results.reserve(u_coords.size());

    for (size_t i = 0; i < u_coords.size(); i++) {
        results.push_back(evaluateLimit(face_index, u_coords[i], v_coords[i]));
    }

    return results;
}
```

---

## Resources

### Internal Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture details
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
- [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) - Build setup guide
- [CLAUDE.md](../CLAUDE.md) - Project overview and principles

### External Resources

**OpenSubdiv**:
- [OpenSubdiv Documentation](https://graphics.pixar.com/opensubdiv/docs/intro.html)
- [Catmull-Clark Subdivision](https://en.wikipedia.org/wiki/Catmull%E2%80%93Clark_subdivision_surface)

**OpenCASCADE**:
- [OpenCASCADE Documentation](https://dev.opencascade.org/doc)
- [NURBS Overview](https://en.wikipedia.org/wiki/Non-uniform_rational_B-spline)

**PyQt6**:
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Qt6 Documentation](https://doc.qt.io/qt-6/)

**VTK**:
- [VTK User Guide](https://vtk.org/documentation/)
- [VTK Examples](https://examples.vtk.org/)

**pybind11**:
- [pybind11 Documentation](https://pybind11.readthedocs.io/)

---

## Getting Help

1. **Check existing documentation** in `docs/`
2. **Search issues** on GitHub
3. **Ask in discussions** on GitHub Discussions
4. **File a bug report** with reproducible example

---

**Last Updated**: November 10, 2025
**Version**: 0.5.0
