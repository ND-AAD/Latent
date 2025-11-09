# Latent

**Revealing Mathematical Truths in Ceramic Forms**

A desktop application for discovering natural mold decompositions in subdivision surface geometries, designed for slip-casting translucent porcelain light fixtures.

> *"The seams are not flaws to hide but truths to celebrate"*
> — Inspired by Peter Pincus

---

## What is Latent?

Latent analyzes subdivision surface (SubD) geometries to discover their inherent mathematical structure, revealing natural boundaries for creating slip-casting molds. Through multiple analytical "lenses" (curvature, spectral resonance, flow patterns), it finds decompositions that align with the form's mathematical coherences rather than imposing arbitrary divisions.

For translucent porcelain light fixtures, the mold seams become permanent visible inscriptions—a dialogue between mathematical truth, material physics, and artistic intent.

### Core Philosophy

**Lossless Mathematical Pipeline**: Maintains exact SubD limit surface evaluation throughout the entire process. Approximation occurs only once—at final G-code/STL export for 3D printing.

**Interactive Refinement**: Pin regions you like, re-analyze the rest with different lenses, merge/split as needed. The tool reveals; you decide.

**Three-Tier Constraints**:
- **Physical** (binary): Violations prevent casting (undercuts, air traps)
- **Manufacturing** (warnings): Make production harder but possible (thin walls, insufficient draft)
- **Mathematical** (documentation): Departures from discovered truth, celebrated as artistic choices

---

## Current Status

**Version**: 0.5.0 - **Phase 0 Complete!** 🎉
**Sprint**: 10-Day API Sprint (Days 1-2 Complete)
**Status**: ✅ C++ Core + Desktop Foundation Ready
**Next**: Day 3+ - Mathematical Lenses & Region Discovery

### ✅ Phase 0 Complete (Days 1-2)

**C++ Geometry Kernel (Day 1)**:
- OpenSubdiv 3.6.0 integration for exact limit surface evaluation
- Stam eigenanalysis for mathematically exact SubD evaluation
- Zero-copy pybind11 bindings with NumPy integration
- Derivative computation (1st and 2nd order) for curvature analysis
- Batch evaluation for high-performance sampling
- CMake build system with multi-platform support
- Comprehensive C++ and Python test suites

**Desktop Application Foundation (Day 2)**:
- Professional PyQt6 main window with dockable panels
- Multi-viewport system (Single, 2H, 2V, 4-Grid layouts)
- VTK 9.3.0 visualization with Rhino-compatible controls
- Advanced SubD display with smooth shading and region coloring
- Application state management with undo/redo (100-item history)
- Parametric region data structures (face_id, u, v)
- Edit mode system (Solid/Panel/Edge/Vertex)
- Complete menu system with keyboard shortcuts

**Rhino Bridge (Day 1)**:
- HTTP server in Grasshopper (port 8888)
- Control cage transfer (exact topology, not mesh!)
- Live sync with change detection
- Connection status monitoring

**Documentation (Day 2)**:
- Complete API reference (C++ and Python)
- Comprehensive build instructions (macOS/Linux)
- Phase 0 completion summary
- Performance benchmarks

**Test Coverage**:
- 35 total tests, 100% pass rate
- Integration tests: 2.4s execution (12x under budget)
- C++ unit tests: exact evaluation validated
- Python bindings: zero-copy arrays confirmed

### 🎯 Coming Next: Phase 1 (Days 3-5)

**Day 3**: Region Management & Interactive Editing
- Face/edge/vertex picking system
- Region list UI with pin/unpin functionality
- Region visualization with color-coded strength
- Interactive boundary editing

**Day 4**: Differential Lens (First Mathematical Lens!)
- Curvature analysis engine (Gaussian, Mean, Principal)
- Ridge/valley line extraction
- Differential decomposition algorithm
- First mathematical regions discovered!

**Day 5**: Spectral Lens (Second Mathematical Lens)
- Laplace-Beltrami operator
- Eigenfunction computation
- Nodal domain extraction
- Multi-lens comparison workflow

---

## Installation

### Prerequisites

**System Requirements**:
- macOS 12+ or Linux (Ubuntu 20.04+, Debian 11+)
- Python 3.11+
- CMake 3.20+
- OpenSubdiv 3.6.0+
- Rhino 8+ for Mac/Windows (for live geometry sync)

**Quick Check**:
```bash
python3 --version   # >= 3.11
cmake --version     # >= 3.20
pkg-config --modversion opensubdiv  # >= 3.6.0
```

### Quick Install

```bash
# 1. Clone repository
git clone https://github.com/yourusername/latent.git
cd latent

# 2. Install system dependencies
# macOS:
brew install cmake opensubdiv

# Ubuntu 22.04+:
sudo apt-get install cmake libosd-dev pybind11-dev

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Build C++ core
cd cpp_core/build
cmake ..
make -j$(nproc)  # or make -j$(sysctl -n hw.ncpu) on macOS
cd ../..

# 6. Verify installation
python3 -c "import sys; sys.path.insert(0, 'cpp_core/build'); import cpp_core; print('✅ Installation successful!')"
```

### Detailed Installation

For complete build instructions including:
- Platform-specific dependencies
- OpenSubdiv installation from source
- Troubleshooting common issues
- Development workflow

See **[docs/BUILD_INSTRUCTIONS.md](docs/BUILD_INSTRUCTIONS.md)**

### Running Latent

**Quick Launch (Recommended):**
```bash
python3 launch.py
```

**Or with activation:**
```bash
source venv/bin/activate && python3 launch.py
```

The application will open with:
- Main window with 4 viewports (default layout)
- Menu system (File, Edit, Analysis, View, Help)
- Dockable panels (Regions, Analysis, Constraints)
- Status bar with Rhino connection status
- Test geometry menu for verification

---

## Usage

### Basic Workflow

1. **Load SubD from Rhino** (Week 3 bridge working)
   - Start Grasshopper HTTP server on port 8800
   - SubD automatically syncs to Latent

2. **Select Mathematical Lens** (Week 5 - in development)
   - Choose analysis method: Curvature, Spectral, Flow, or Topological
   - Click "Analyze" to discover natural regions

3. **Refine Regions** (Week 4-8)
   - Switch to Panel mode to select faces
   - Pin regions you like (locks from re-analysis)
   - Re-analyze unpinned regions with different lens
   - Merge/split regions as needed
   - Edit boundaries in Edge mode

4. **Validate Constraints** (Week 7)
   - Check for physical violations (undercuts, air traps)
   - Review manufacturing warnings
   - Address issues or accept calculated risks

5. **Generate Molds** (Week 8)
   - Apply draft angles
   - Create NURBS surfaces from parametric regions
   - Construct mold solids with registration features
   - Send back to Rhino for fabrication export

### Viewport Controls (Rhino-Compatible)

**Mouse Navigation:**
- **Right-drag** = Rotate/orbit view
- **Shift + Right-drag** = Pan view
- **Mouse wheel** = Zoom in/out
- **Left-click** = Select object

**Edit Modes:**
- **S** = Solid mode (view only)
- **P** = Panel mode (select faces)
- **E** = Edge mode (select edges)
- **V** = Vertex mode (select vertices)

**Keyboard Shortcuts:**
- **Cmd+Z / Cmd+Shift+Z** = Undo/Redo
- **Space** = Reset camera
- **Alt+1/2/3/4** = Switch viewport layouts
- **A** = Run analysis
- **P** = Pin selected region
- **G** = Generate molds

*See [reference/RhinoUI/](reference/RhinoUI/) for complete Rhino 8 control specifications*

---

## Architecture

### Technology Stack

**Hybrid C++/Python Architecture** (Phase 0 Complete):

**C++ Geometry Kernel:**
- OpenSubdiv 3.6.0 (exact limit surface evaluation via Stam eigenanalysis)
- pybind11 2.11.0+ (zero-copy Python bindings)
- CMake 3.20+ (build system)
- Metal backend support (macOS GPU acceleration)

**Python Application Layer:**
- Python 3.11+ for all application code
- PyQt6 6.9.1 (UI framework)
- VTK 9.3.0 (3D visualization)
- NumPy 2.0+ (array operations, zero-copy with C++)
- Requests 2.32.0 (Rhino HTTP bridge)

**Why Hybrid**: The v5.0 specification requires capabilities that pure Python cannot provide:
- **Exact evaluation**: OpenSubdiv's Stam eigenanalysis for mathematically exact limit surfaces
- **Performance**: 10-100x faster than pure Python for geometry operations
- **Derivatives**: First and second derivative computation for curvature analysis
- **Lossless representation**: No mesh approximation in the analysis pipeline

This is NOT an optimization - it's a **fundamental architectural requirement** for the lossless mathematical pipeline.

### Project Structure

```
latent/
├── main.py                      (1200 lines) - Main window application
├── launch.py                    (60 lines)   - Qt plugin auto-config launcher
├── setup.py                     (156 lines)  - Python package build
├── requirements.txt             (15 lines)   - Python dependencies
├── CLAUDE.md                                 - AI collaboration guide
├── README.md                                 - This file
│
├── app/                         (~4800 lines Python)
│   ├── state/
│   │   ├── app_state.py         (600 lines)  - Centralized state management
│   │   ├── parametric_region.py (87 lines)   - Region definition (face_id, u, v)
│   │   └── edit_mode.py         (120 lines)  - Edit mode management
│   │
│   ├── ui/
│   │   ├── viewport_base.py     (250 lines)  - Base viewport class
│   │   ├── subd_viewport.py     (400 lines)  - SubD-specific viewport
│   │   ├── viewport_layout.py   (500 lines)  - Multi-viewport manager
│   │   ├── region_list_widget.py (350 lines) - Region sidebar
│   │   ├── analysis_panel.py    (200 lines)  - Analysis controls
│   │   ├── constraint_panel.py  (120 lines)  - Constraint panel
│   │   └── ...                               - Additional UI components
│   │
│   ├── geometry/
│   │   ├── subd_display.py      (350 lines)  - VTK mesh utilities
│   │   ├── curvature.py         (150 lines)  - Curvature computation
│   │   └── test_meshes.py       (200 lines)  - Test geometry
│   │
│   ├── bridge/
│   │   ├── rhino_bridge.py      (200 lines)  - Base bridge class
│   │   ├── subd_fetcher.py      (120 lines)  - Fetch control cage
│   │   ├── live_bridge.py       (150 lines)  - Live sync manager
│   │   └── geometry_receiver.py (80 lines)   - Parse geometry JSON
│   │
│   └── analysis/                             - Mathematical lenses (Day 4+)
│       └── differential_decomposition.py     - Curvature-based (upcoming)
│
├── cpp_core/                    (~1000 lines C++)
│   ├── CMakeLists.txt           (135 lines)  - Build configuration
│   ├── BUILD.md                 (371 lines)  - Build documentation
│   ├── INTEGRATION.md           (372 lines)  - Integration guide
│   │
│   ├── geometry/
│   │   ├── types.h              (60 lines)   - Point3D, SubDControlCage, etc.
│   │   ├── subd_evaluator.h     (176 lines)  - Evaluator interface
│   │   └── subd_evaluator.cpp   (756 lines)  - OpenSubdiv integration
│   │
│   └── python_bindings/
│       ├── bindings.cpp         (446 lines)  - pybind11 bindings
│       └── test_bindings.py     (200 lines)  - Python binding tests
│
├── rhino/                                    - Grasshopper components
│   └── grasshopper_http_server_control_cage.py  (GH component)
│
├── tests/                       (~820 lines)
│   ├── README.md                (131 lines)  - Testing documentation
│   ├── run_all_tests.sh         (48 lines)   - Test runner
│   ├── test_day1_integration.py (320 lines)  - Integration tests
│   └── test_*.py                (~300 lines)  - Various test suites
│
└── docs/
    ├── PHASE_0_COMPLETE.md                   - Phase 0 summary
    ├── API_REFERENCE.md                      - Complete API docs
    ├── BUILD_INSTRUCTIONS.md                 - Build guide
    ├── PROJECT_STATUS.md                     - Project status
    └── RHINO_BRIDGE_SETUP.md                 - Bridge setup
```

**Total**: ~8,700 lines of code (Phase 0 Complete)

---

## Mathematical Lenses

### 1. Differential Decomposition (Week 5 - In Development)
Discovers regions based on curvature behavior. Ridge and valley lines become natural boundaries.

**Best for**: Organic forms with clear feature lines

### 2. Spectral Decomposition (Future)
Uses Laplace-Beltrami eigenfunctions (vibration modes) to find nodal domains.

**Best for**: Forms with rotational or reflective symmetries

### 3. Flow Decomposition (Future)
Geodesic drainage basins—where would water flow on this surface?

**Best for**: Complex topologies, forms with multiple openings

### 4. Topological Decomposition (Future)
Morse function critical points and flow patterns.

**Best for**: Forms with distinct topological features

Each lens reveals different aspects of the form's inherent mathematical structure. The "right" decomposition depends on which truth you want the seams to inscribe.

---

## Development Timeline

**10-Day API Sprint** (Current Mode):

**Days 1-2 (Complete)** ✅: C++ Core + Desktop Foundation (Phase 0)
**Days 3-5 (Next)**: Mathematical Lenses (Differential, Spectral)
**Days 6-7**: Constraint Validation + Region Editing
**Days 8-9**: NURBS Generation + Mold Export
**Day 10**: Documentation + Polish

**Sprint Budget**: $1000 API credits
**Spent**: ~$10 (Days 1-2)
**Remaining**: ~$990

**Target**: MVP with two working mathematical lenses by Day 5

See [docs/reference/api_sprint/](docs/reference/api_sprint/) for complete sprint documentation.

---

## Design Constraints

### The Fabrication Commandments

Based on comprehensive slip-casting research:

**Physical (Must Obey)**:
1. No undercuts that prevent demolding
2. All cavity surfaces must be slip-accessible
3. Air must have escape paths
4. No trapped volumes

**Manufacturing (Should Obey)**:
4. Minimum 0.5° draft on vertical surfaces
5. Wall thickness 3-6mm for translucent porcelain
6. Wall thickness variation <25%
7. Plaster walls 1.5-2 inches thick
8. Registration keys 1/4 inch from model edge
9. Seam gap <0.05 inches (1.27mm)

**Mathematical (Document)**:
10. Acknowledge when mathematical truth is negotiated

See [reference/SlipCasting_Ceramics_Technical_Reference.md](reference/SlipCasting_Ceramics_Technical_Reference.md) for complete fabrication specifications.

---

## Documentation

**Phase 0 Documentation** (NEW):
- [docs/PHASE_0_COMPLETE.md](docs/PHASE_0_COMPLETE.md) - Phase 0 summary, integration guide
- [docs/API_REFERENCE.md](docs/API_REFERENCE.md) - Complete C++ and Python API documentation
- [docs/BUILD_INSTRUCTIONS.md](docs/BUILD_INSTRUCTIONS.md) - Build guide (macOS/Linux)

**Project Documentation**:
- [CLAUDE.md](CLAUDE.md) - AI collaboration guidance, architectural principles
- [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) - Current completion status
- [docs/RHINO_BRIDGE_SETUP.md](docs/RHINO_BRIDGE_SETUP.md) - Rhino/Grasshopper connection setup

**Sprint Documentation**:
- [docs/reference/api_sprint/](docs/reference/api_sprint/) - 10-day sprint details, agent tasks

---

## Contributing

This is currently a personal research/art project. Feedback, suggestions, and mathematical insights welcome via GitHub Issues.

---

## License

TBD - Project in active development

---

## Acknowledgments

**Inspired by:**
- Peter Pincus (ceramic artist, "seams as truth" philosophy)
- Jos Stam (exact SubD evaluation mathematics)
- McNeel Rhino team (SubD implementation excellence)

**Built with:**
- PyQt6 (UI framework)
- VTK (visualization toolkit)
- rhino3dm (geometry kernel)
- NumPy/SciPy (scientific computing)

---

## Contact

**Artist/Developer**: Nick Duch
**Background**: 20+ years ceramics, furniture design, architecture (licensed), recent CS/additive manufacturing
**Project**: Combining traditional slip-casting with computational geometry for translucent porcelain light fixtures

---

*Latent: (adjective) existing but not yet developed or manifest; hidden or concealed.*

Every form contains mathematical truths waiting to be revealed. This tool helps you see them.
