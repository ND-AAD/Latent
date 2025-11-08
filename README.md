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

**Version**: 0.4.0 (Week 4 of 10 Complete - ~40% MVP)
**Status**: ✅ Foundation Complete, Selection System Working
**Next**: Week 5 - First Mathematical Lens (Differential Decomposition)

### ✅ Working Features

**Foundation (Week 1)**:
- Professional PyQt6 desktop application
- Centralized state management with undo/redo (100-item history)
- Signal/slot architecture for reactive UI
- Complete menu system with keyboard shortcuts

**3D Visualization (Week 1)**:
- VTK 9.3.0 integration with PyQt6
- Rhino-compatible viewport controls (right-drag orbit, shift+right pan, wheel zoom)
- SubD control net rendering
- Test geometry visualization (cubes, spheres, tori)
- Region coloring system (per-face color assignment)

**Multi-Viewport System (Week 2)**:
- Four layout modes: Single, Two Horizontal, Two Vertical, Four Grid
- Independent cameras per viewport
- Standard view presets (Top, Front, Right, Perspective, Isometric)
- Active viewport tracking with visual indicators
- Menu integration with keyboard shortcuts (Alt+1/2/3/4)

**Rhino HTTP Bridge (Week 3)**:
- Live bidirectional communication with Rhino/Grasshopper
- Geometry transfer via HTTP (port 8800)
- Connection status monitoring
- Automatic update detection (2-second polling)
- Change detection to prevent duplicate updates

**Edit Mode & Selection System (Week 4)**:
- Four edit modes: Solid (view-only), Panel (face selection), Edge, Vertex
- Complete VTK picking system for all element types
- Multi-select with Shift+Click (add/remove from selection)
- Unified yellow highlighting for visual feedback
- Face, edge, and vertex selection all functional

### 🚧 In Development

**Week 5 (Current)**: Differential Decomposition
- Curvature-based region discovery
- Ridge/valley line extraction
- First working mathematical lens

**Week 6**: Iteration Management
- Design snapshot system
- Switch between alternative decompositions
- Thumbnail generation

**Week 7**: Constraint Validation
- Physical constraint checking (undercuts, air traps, slip access)
- Manufacturing warnings (draft angles, wall thickness)
- Mathematical tension documentation

**Week 8-10**: NURBS Generation & Polish
- Draft angle application
- NURBS surface fitting
- Mold solid construction
- Export to fabrication

---

## Installation

### Prerequisites
- macOS 12+ (Monterey or later)
- Python 3.11+
- Rhino 8+ for Mac (for live geometry sync)

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/latent.git
cd latent
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Running Latent

**Quick Launch (Recommended):**
```bash
python3 launch.py
```

**Or with one command:**
```bash
source venv/bin/activate && python3 launch.py
```

The application will open with the main window showing:
- 3D viewport (left panel) with VTK rendering
- Mathematical lens selector (Flow/Spectral/Curvature/Topological)
- Discovered regions list with pin/unpin controls
- Constraint validation panel
- Generate/Send buttons for mold creation

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

**Current (Pure Python - Weeks 1-7):**
- Python 3.12 for all code
- PyQt6 6.9.1 (UI framework)
- VTK 9.3.0 (3D visualization)
- NumPy 1.26.2 / SciPy 1.11.4 (numerical computing)
- rhino3dm 8.17.0 (exact SubD representation)

**Future (Hybrid - Week 8+ if needed):**
- C++ geometry kernel (OpenCASCADE for NURBS)
- OpenSubdiv (GPU-accelerated SubD evaluation)
- pybind11 bindings
- Metal backend for Apple Silicon optimization

**Decision Point**: Week 8 performance profiling will determine if hybrid architecture is needed. Staying pure Python while velocity and performance remain adequate.

### Project Structure

```
latent/
├── main.py                     # Application entry point
├── launch.py                   # Qt plugin auto-config launcher
├── requirements.txt            # All dependencies
├── CLAUDE.md                   # AI collaboration guide
├── README.md                   # This file
│
├── app/                        # Application code
│   ├── state/
│   │   ├── app_state.py        # Centralized state management
│   │   └── edit_mode.py        # Edit mode & selection tracking
│   ├── bridge/
│   │   └── rhino_bridge.py     # HTTP communication with Rhino
│   ├── geometry/
│   │   ├── subd_display.py     # SubD visualization helpers
│   │   └── curvature.py        # Curvature computation
│   ├── analysis/               # Mathematical decomposition engines
│   │   └── differential_decomposition.py  # Curvature-based (Week 5)
│   ├── constraints/            # Validation system (Week 7)
│   └── ui/
│       ├── viewport_3d.py      # VTK 3D viewport
│       ├── viewport_layout.py  # Multi-viewport manager
│       ├── region_list.py      # Region management UI
│       ├── constraint_panel.py # Validation display
│       ├── edit_mode_toolbar.py # Edit mode selector
│       └── picker.py           # VTK picking system
│
├── rhino/                      # Grasshopper components
│   ├── grasshopper_server_control.py  # Main HTTP server
│   └── grasshopper_manual_push.py     # Manual geometry push
│
├── tests/                      # Unit tests (to be added)
│
└── docs/                       # Documentation
    ├── IMPLEMENTATION_ROADMAP.md
    ├── PROJECT_STATUS.md
    └── RHINO_BRIDGE_SETUP.md
```

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

**Weeks 1-4 (Complete)**: Foundation, Visualization, Multi-Viewport, HTTP Bridge, Edit Modes
**Week 5 (Current)**: Differential Decomposition
**Week 6**: Iteration Management
**Week 7**: Constraint Validation
**Week 8**: NURBS Generation
**Week 9**: Additional Lenses
**Week 10**: Polish & Testing

**Target MVP**: 6 weeks remaining (Week 5 of 10)

See [docs/IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md) for detailed week-by-week plan.

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

- [CLAUDE.md](CLAUDE.md) - AI collaboration guidance, architectural principles
- [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) - Current completion status, priorities
- [docs/IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md) - Week-by-week implementation plan
- [docs/RHINO_BRIDGE_SETUP.md](docs/RHINO_BRIDGE_SETUP.md) - Rhino/Grasshopper connection setup

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
