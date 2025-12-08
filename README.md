# Latent

**Revealing Mathematical Truths in Ceramic Forms**

A Rhino 8 plugin for discovering natural mold decompositions in subdivision surface geometries, designed for slip-casting translucent porcelain light fixtures.

> *"The seams are not flaws to hide but truths to celebrate"*
> — Inspired by Peter Pincus

---

## What is Latent?

Latent analyzes subdivision surface (SubD) geometries to discover their inherent mathematical structure, revealing natural boundaries for creating slip-casting molds. Through multiple analytical "lenses" (curvature, spectral resonance, flow patterns), it finds decompositions that align with the form's mathematical coherences rather than imposing arbitrary divisions.

For translucent porcelain light fixtures, the mold seams become permanent visible inscriptions—a dialogue between mathematical truth, material physics, and artistic intent.

### Core Philosophy

**Lossless Mathematical Pipeline**: Maintains exact SubD limit surface evaluation throughout the entire process. Approximation occurs only once—at final G-code/STL export for fabrication.

**Interactive Refinement**: Pin regions you like, re-analyze the rest with different lenses, merge/split as needed. The tool reveals; you decide.

**Three-Tier Constraints**:
- **Physical** (binary): Violations prevent casting (undercuts, air traps)
- **Manufacturing** (warnings): Make production harder but possible (thin walls, insufficient draft)
- **Mathematical** (documentation): Departures from discovered truth, celebrated as artistic choices

---

## Current Status

**Version**: 1.0.0
**Platform**: Rhino 8 Plugin (macOS/Windows)
**Status**: Complete - All implementation phases finished

### Features

**Mathematical Lenses**:
- **Differential Lens**: Curvature-based region discovery (Gaussian, Mean, Principal curvatures)
- **Spectral Lens**: Laplace-Beltrami eigenfunctions for nodal domain extraction
- **Cage-Aligned Lens**: Regions aligned with SubD control cage topology

**Rhino Integration**:
- Four commands: `LatentAnalyze`, `LatentSelect`, `LatentPin`, `LatentRevert`
- Three panels: Lens Control, Geometry List, Display Settings
- Full undo/redo integration with Rhino
- Surface-constrained interaction (points stay on limit surface)

**State Management**:
- Implicit/Explicit state tracking (lens-defined vs user-modified)
- Pinning to protect elements from reanalysis
- Hierarchical revert (Region → Edge → Vertex)

---

## Technology Stack

**Hybrid C++/Python/C# Architecture**:

| Layer | Technology | Purpose |
|-------|------------|---------|
| **C++ Core** | OpenSubdiv 3.6.0 | Exact limit surface evaluation (Stam eigenanalysis) |
| **Python Service** | JSON-RPC Server | Mathematical lens analysis and boundary extraction |
| **C# Plugin** | RhinoCommon + Eto.Forms | Rhino integration, UI, and user interaction |

**Why Hybrid**: The lossless mathematical pipeline requires:
- **Exact evaluation**: OpenSubdiv's Stam eigenanalysis for mathematically exact limit surfaces
- **Performance**: 10-100x faster than pure Python for geometry operations
- **Native integration**: C# for seamless Rhino plugin development
- **Mathematical analysis**: Python/SciPy for spectral decomposition and eigenfunction computation

---

## Installation

### Requirements

- **Rhino 8** (Windows or macOS)
- **.NET Framework 4.8** or **.NET 6+**
- **Python 3.8+** (for analysis service)
- **OpenSubdiv 3.6.0+**
- **CMake 3.20+**

### Quick Install

```bash
# 1. Clone repository
git clone https://github.com/ND-AAD/Latent.git
cd Latent

# 2. Install system dependencies (macOS)
brew install cmake opensubdiv

# 3. Build C++ core
cd cpp_core/build
cmake ..
make -j$(sysctl -n hw.ncpu)
cd ../..

# 4. Install Python dependencies
pip install numpy scipy

# 5. Build Rhino plugin
cd rhino_plugin
dotnet build
```

### Running

1. Copy `LatentPlugin.rhp` and `liblatent_core.dylib` to Rhino plugins folder
2. Start Rhino 8
3. Enable the Latent plugin via `PlugInManager`
4. Type `LatentAnalyze` to begin

See [docs/RHINO_PLUGIN_USER_GUIDE.md](docs/RHINO_PLUGIN_USER_GUIDE.md) for detailed instructions.

---

## Usage

### Basic Workflow

1. **Create or import a SubD surface** in Rhino

2. **Run analysis**:
   ```
   LatentAnalyze
   ```

3. **Select lens type**: Differential, Spectral, or Cage-Aligned

4. **Review discovered regions** displayed as boundary curves

5. **Refine**:
   - Pin regions you like (`LatentPin`)
   - Re-analyze with different parameters
   - Drag vertices to adjust boundaries
   - Revert changes if needed (`LatentRevert`)

### Commands

| Command | Description |
|---------|-------------|
| `LatentAnalyze` | Run lens analysis on selected SubD |
| `LatentSelect` | Select region/edge/vertex |
| `LatentPin` | Pin/unpin selected element |
| `LatentRevert` | Revert to implicit state |

### Panels

| Panel | Description |
|-------|-------------|
| **Latent Lens** | Lens selection and parameters |
| **Latent Geometry** | Element list with state management |
| **Latent Display** | Visualization settings |

---

## Project Structure

```
Latent/
├── cpp_core/                    # C++ geometry kernel
│   ├── geometry/                # SubD evaluator, surface curves
│   ├── analysis/                # Curvature analyzer
│   ├── constraints/             # Draft/undercut validation
│   ├── python_bindings/         # pybind11 bindings
│   └── c_bindings/              # C API for P/Invoke
├── rhino_plugin/                # C# Rhino 8 plugin
│   ├── Commands/                # Rhino commands
│   ├── UI/                      # Eto.Forms panels
│   ├── Display/                 # DisplayConduit
│   ├── Geometry/                # Vertex, Edge, Region, RegionManager
│   ├── Interaction/             # Surface-constrained picking
│   ├── Interop/                 # P/Invoke wrappers
│   ├── Analysis/                # Lens client
│   └── Tests/                   # Unit and integration tests
├── analysis_service/            # Python JSON-RPC server
├── app/                         # (Legacy) Desktop application
├── tests/                       # Python test suite
└── docs/
    ├── PROJECT_STATUS.md        # Implementation status
    ├── RHINO_PLUGIN_USER_GUIDE.md
    └── plans/                   # Architecture & implementation docs
```

---

## Mathematical Lenses

### Differential (Curvature)

Discovers regions based on curvature behavior. Ridge and valley lines become natural boundaries.

- Gaussian, Mean, and Principal curvature computation
- Ridge and valley line extraction
- Region boundary detection with strength scoring

**Best for**: Organic forms with clear feature lines

### Spectral (Eigenfunction)

Uses Laplace-Beltrami eigenfunctions (vibration modes) to find nodal domains.

- Discrete Laplace-Beltrami operator
- Eigenfunction computation (multiple modes)
- Nodal domain extraction

**Best for**: Forms with rotational or reflective symmetries

### Cage-Aligned

Aligns regions directly with SubD control cage edges.

**Best for**: Simple forms where cage topology matches desired decomposition

---

## Documentation

**User Documentation**:
- [Rhino Plugin User Guide](docs/RHINO_PLUGIN_USER_GUIDE.md) - Complete usage instructions
- [Project Status](docs/PROJECT_STATUS.md) - Current implementation status

**Architecture Documentation**:
- [Architecture Design](docs/plans/2025-12-04-rhino-plugin-architecture-design.md)
- [Implementation Plan](docs/plans/2025-12-04-rhino-plugin-implementation-plan.md)

**Development**:
- [CLAUDE.md](CLAUDE.md) - Development guidelines and AI collaboration

---

## Future Development

**Priority 1**:
- NURBS mold generation and export
- Auto-start analysis service
- Performance optimization

**Priority 2**:
- Additional lenses (Flow, Topological)
- Multi-SubD support
- Document persistence in .3dm files

**Priority 3**:
- Machine learning for resonance prediction
- Template library for slip-casting

---

## Contributing

This is currently a personal research/art project. Feedback, suggestions, and mathematical insights welcome via GitHub Issues.

---

## License

Proprietary - All rights reserved

---

## Acknowledgments

**Inspired by**:
- Peter Pincus (ceramic artist, "seams as truth" philosophy)
- Jos Stam (exact SubD evaluation mathematics)
- McNeel Rhino team (SubD implementation excellence)

**Built with**:
- [OpenSubdiv](https://graphics.pixar.com/opensubdiv/) - Exact SubD evaluation
- [RhinoCommon](https://developer.rhino3d.com/) - Rhino SDK
- [Eto.Forms](https://github.com/picoe/Eto) - Cross-platform UI
- [NumPy](https://numpy.org/) / [SciPy](https://scipy.org/) - Scientific computing

---

## Contact

**Artist/Developer**: Nick Duch
**Project**: Combining traditional slip-casting with computational geometry for translucent porcelain light fixtures

---

*Latent: from the Latin latens — "lying hid, concealed, secret, unknown." Existing hidden.*

Every form contains mathematical truths waiting to be revealed. This tool helps you see them.
