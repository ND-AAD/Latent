# Subdivision Surface Ceramic Mold Generation System
## Technical Specification & Implementation Framework
### Version 5.0 - Parametric Region Architecture with Hybrid Rendering Pipeline
### Date: January 2025

---

## DOCUMENT OVERVIEW

This specification defines a computational system for generating slip-casting molds from subdivision surfaces through parametric region discovery. Version 5.0 clarifies the mathematical-display duality, establishes the parametric region architecture, and details the hybrid C++/Python implementation strategy with OpenSubdiv and VTK/Qt3D rendering.

**Key Architectural Decisions in v5.0:**
- Parametric regions as topological relationships, not geometric entities
- Mathematical operations on limit surfaces, display via tessellation
- Hybrid OpenSubdiv (C++) + VTK/Qt3D rendering pipeline
- Pressure-based negotiation for pinned regions
- Selection operates on mathematical entities, not display geometry
- Additional lenses for thermal and flow analysis

---

## 1. PROJECT VISION

### 1.1 Core Philosophy

Every form contains natural mathematical coherences that can be discovered through multiple analytical lenses. The system reveals rather than imposes, discovering regions that express the form's inherent structure. Mold segmentation becomes a dialogue between mathematical understanding, physical constraints, and material reality. Visible seams in translucent porcelain become permanent inscriptions of this negotiation.

**The Mathematical-Display Duality:**
Mathematical operations maintain perfect fidelity on limit surfaces. Display uses adaptive tessellation - smooth enough for aesthetic judgment but accepting that GPUs require triangles. This is the industry standard approach, proven by Rhino, Blender, and all professional CAD systems.

### 1.2 Primary Objectives

1. **Discover natural coherent regions** through mathematical lens analysis on limit surfaces
2. **Maintain mathematical fidelity** for all operations and selections
3. **Enable selective refinement** via region pinning with pressure-based negotiation
4. **Provide smooth visual feedback** through adaptive tessellation
5. **Generate manufacturable molds** respecting ceramic slip-casting physics
6. **Document the dialogue** between mathematics, material, and making

### 1.3 Target Use Case

Professional/artist creating translucent porcelain light fixtures using:
- **Design**: SubD modeling in Rhino 8+
- **Analysis**: Standalone desktop application with parametric region discovery
- **Fabrication**: 3D-printed formwork → plaster molds → slip-casting
- **Material**: Translucent porcelain (3-4mm walls, visible seams as design feature)
- **Philosophy**: Seam lines as geometric annotations revealing mathematical structure

---

## 2. SYSTEM ARCHITECTURE

### 2.1 Overview: Parametric Region Architecture

```
┌────────────────────────────────────────────────────────────┐
│  MATHEMATICAL LAYER (Exact)                                │
│  ┌────────────────────────────────────────────────────────┐│
│  │  Parametric Region Definitions                         ││
│  │  • Topological face sets                              ││
│  │  • Parametric boundaries (u,v curves)                 ││
│  │  • Generation metadata (lens used, parameters)        ││
│  │  • Constraint parameters                              ││
│  └────────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────┐│
│  │  SubD Limit Surface (Ground Truth)                     ││
│  │  • Control cage from Rhino                            ││
│  │  • Exact evaluation via OpenSubdiv                     ││
│  │  • Never approximated during analysis                 ││
│  └────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│  COMPUTATION LAYER (C++ Performance Core)                  │
│  ┌────────────────────────────────────────────────────────┐│
│  │  OpenSubdiv Integration                                ││
│  │  • Exact limit surface evaluation                      ││
│  │  • Adaptive tessellation for display                   ││
│  │  • GPU acceleration (Metal on macOS)                   ││
│  └────────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────┐│
│  │  Mathematical Analysis Engines                         ││
│  │  • Spectral (Laplace-Beltrami eigenfunctions)         ││
│  │  • Flow (geodesic drainage paths)                     ││
│  │  • Curvature (mean and Gaussian analysis)             ││
│  │  • Morse (critical point theory)                      ││
│  │  • Thermal Gradient (NEW: heat equation)              ││
│  │  • Slip Flow Dynamics (NEW: laminar flow)             ││
│  └────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────┐
│  DISPLAY LAYER (Tessellated Approximation)                 │
│  ┌────────────────────────────────────────────────────────┐│
│  │  Adaptive Tessellation                                 ││
│  │  • Level 3-4 for smooth working display               ││
│  │  • Level 5-6 for presentation                         ││
│  │  • Silhouette enhancement                             ││
│  │  • Exact boundary curve evaluation                    ││
│  └────────────────────────────────────────────────────────┘│
│  ┌────────────────────────────────────────────────────────┐│
│  │  Rendering Pipeline (Choose One)                       ││
│  │  • VTK with PyQt6 integration                         ││
│  │  • Qt3D native Qt rendering                           ││
│  │  • Custom OpenGL/Metal                                ││
│  └────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────┘
```

### 2.2 Parametric Region Definition

```python
class ParametricRegion:
    """
    A region exists as relationships and parameters,
    not explicit geometry. Geometry is generated on-demand.
    """
    # Topological definition
    face_indices: Set[int]  # Which SubD faces belong to this region
    edge_graph: Graph  # Adjacency relationships
    
    # Parametric space (the abstract manifold)
    parameter_domain: Domain2D  # (u,v) space [0,1] x [0,1]
    boundary_params: List[ParametricCurve]  # Boundaries in UV space
    
    # Procedural generation rules
    generation_method: MathematicalLens  # How this region was discovered
    lens_parameters: Dict  # Specific parameters used
    resonance_score: float  # How well this region fits the mathematical analysis
    
    # Physical constraints
    draft_angle: float
    minimum_thickness: float
    demolding_direction: Vector3
    
    # State
    is_pinned: bool  # Locked against modification
    pin_timestamp: datetime  # When pinned
    
    def to_nurbs(self, subd_surface: SubDSurface) -> NurbsSurface:
        """Generate NURBS patch on-demand from parametric definition"""
        pass
        
    def to_mesh(self, subd_surface: SubDSurface, level: int) -> Mesh:
        """Generate display mesh at requested subdivision level"""
        pass
```

### 2.3 C++/Python Hybrid Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Python Layer (UI and Orchestration)                        │
│  • PyQt6 UI framework                                       │
│  • State management                                         │
│  • User interaction                                         │
│  • Rhino communication                                      │
│  • File I/O                                                │
└─────────────────────────────────────────────────────────────┘
                              ↕ pybind11
┌─────────────────────────────────────────────────────────────┐
│  C++ Performance Core                                        │
│  • OpenSubdiv: SubD evaluation and tessellation            │
│  • OpenCASCADE: NURBS operations and Boolean ops           │
│  • Mathematical analysis algorithms                         │
│  • Constraint validation                                    │
│  • Mesh generation for display                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. MATHEMATICAL LENSES

### 3.1 Core Lenses (Existing)

#### 3.1.1 Spectral Lens (Laplace-Beltrami Eigenfunctions)
- Reveals natural vibration modes of the surface
- Regions form at eigenfunction nodal lines
- Produces aesthetically balanced decompositions
- May generate non-convex regions requiring convexity post-processing

#### 3.1.2 Flow Lens (Geodesic Drainage)
- Simulates water flow across the surface
- Regions form watersheds between drainage basins
- Natural for vessels and containers
- Augmented with viscous flow corrections for slip behavior

#### 3.1.3 Curvature Lens (Differential Geometry)
- Analyzes mean and Gaussian curvature
- Regions form at curvature discontinuities
- Excellent for mechanical forms
- Natural alignment with structural features

#### 3.1.4 Morse Lens (Critical Point Theory)
- Identifies topological features
- Regions connect critical points
- Reveals form's topological skeleton
- Best for complex organic shapes

### 3.2 New Lenses (v5.0 Additions)

#### 3.2.1 Thermal Gradient Lens
```python
class ThermalGradientLens:
    """
    Prevents cracking from differential cooling during firing.
    Segments based on thermal mass and cooling rates.
    """
    def analyze(self, manifold: ManifoldStructure, 
                wall_thickness: ScalarField) -> List[ParametricRegion]:
        # Thermal mass distribution
        thermal_mass = wall_thickness * manifold.area_element
        
        # Solve heat equation: ∂T/∂t = α∇²T
        thermal_diffusivity = self.ceramic_properties.diffusivity / thermal_mass
        cooling_rate = self.compute_cooling_rate(thermal_diffusivity)
        
        # Find boundaries where cooling rate changes rapidly
        # These natural boundaries prevent stress concentration
        gradient_magnitude = np.gradient(cooling_rate)
        boundaries = self.extract_level_sets(gradient_magnitude, threshold=0.2)
        
        # Regions have uniform thermal behavior
        return self.boundaries_to_regions(boundaries)
```

#### 3.2.2 Slip Flow Dynamics Lens
```python
class SlipFlowLens:
    """
    Simulates ceramic slip flow for even mold filling.
    Reynolds number < 100 ensures laminar flow.
    """
    def analyze(self, manifold: ManifoldStructure,
                gravity_direction: Vector3,
                pour_points: List[Point]) -> List[ParametricRegion]:
        # Project gravity onto manifold
        gravity_field = self.project_onto_manifold(gravity_direction, manifold)
        
        # Solve potential flow with viscous corrections
        # ∇²φ = 0 where φ is velocity potential
        velocity_potential = self.solve_laplace(
            source=pour_points,
            gravity_bias=gravity_field,
            viscosity=self.slip_properties.viscosity
        )
        
        # Extract streamlines and separatrices
        streamlines = self.compute_streamlines(velocity_potential)
        separatrices = self.find_separatrices(streamlines)
        
        # Natural mold divisions at flow boundaries
        return self.separatrices_to_regions(separatrices)
```

### 3.3 Lens Combination Strategy

```python
class MultiLensAnalyzer:
    def compute_resonance_scores(self, surface: SubDSurface) -> Dict:
        """
        Run all lenses and score how well each fits the form
        """
        scores = {}
        for lens in self.available_lenses:
            regions = lens.analyze(surface)
            # Score based on:
            # - Region convexity
            # - Size uniformity  
            # - Boundary smoothness
            # - Constraint satisfaction
            scores[lens] = self.evaluate_decomposition_quality(regions)
        
        return scores
```

---

## 4. REGION DISCOVERY AND MANIPULATION

### 4.1 Pinning System with Pressure Model

```python
class PressureNegotiation:
    """
    Pinned regions are absolutely immutable.
    Unpinned regions flow like fluid around pinned obstacles.
    """
    def apply_edit_pressure(self, 
                           edited_region: ParametricRegion,
                           pinned_regions: Set[ParametricRegion],
                           all_regions: List[ParametricRegion]) -> None:
        # Create pressure field from edit
        pressure_source = self.compute_edit_pressure(edited_region.boundary_change)
        
        # Pinned regions create infinite resistance (Dirichlet boundary)
        obstacles = [r.boundary_params for r in pinned_regions]
        
        # Solve pressure diffusion: ∇²P = 0
        pressure_field = self.solve_laplace(
            source=pressure_source,
            dirichlet_boundaries=obstacles  # Immovable
        )
        
        # Unpinned regions adapt to pressure gradient
        for region in all_regions:
            if not region.is_pinned:
                gradient = np.gradient(pressure_field)
                region.adapt_boundary(gradient, timestep=0.1)
```

### 4.2 Selection System

```python
class SelectionMapper:
    """
    Maps display interactions to mathematical entities.
    User selects mathematical truth, not display tessellation.
    """
    def __init__(self):
        # Maintain genealogy from tessellation
        self.triangle_to_face: Dict[int, int] = {}  # Display → SubD face
        self.triangle_to_region: Dict[int, int] = {}  # Display → Region
        self.display_edge_to_boundary: Dict[int, int] = {}  # Display → Boundary
    
    def select_at_screen_point(self, x: int, y: int) -> MathematicalEntity:
        # Ray cast hits display mesh
        hit_triangle = self.ray_cast_to_display_mesh(x, y)
        
        # Map back to mathematical entity
        if self.selection_mode == 'region':
            region_id = self.triangle_to_region[hit_triangle]
            return self.parametric_regions[region_id]
            
        elif self.selection_mode == 'boundary':
            # Find nearest parametric boundary
            hit_point_3d = self.unproject_to_surface(x, y)
            return self.find_nearest_parametric_boundary(hit_point_3d)
            
        elif self.selection_mode == 'control_vertex':
            # Select from original SubD cage
            return self.find_nearest_control_vertex(x, y)
```

---

## 5. RENDERING PIPELINE

### 5.1 The Standard Reality

**No renderer directly displays SubD surfaces.** All rendering requires tessellation to triangles. This is not a limitation but standard practice across all 3D software.

```
SubD Surface → OpenSubdiv → Triangle Mesh → Renderer (VTK/Qt3D/OpenGL) → Display
(Mathematical)  (Evaluate)   (Tessellated)    (Rasterize)              (Pixels)
```

### 5.2 Display Quality Management

```python
class AdaptiveDisplayManager:
    """
    Ensures smooth visual feedback for aesthetic decisions
    while maintaining performance.
    """
    def compute_subdivision_level(self, context: ViewContext) -> int:
        base_level = 3  # ~10-40K triangles
        
        # Increase for close examination
        if context.camera_distance < 5:
            level = 5  # ~160-640K triangles
        elif context.camera_distance < 20:
            level = 4  # ~40-160K triangles
        else:
            level = 3
            
        # Extra refinement at silhouettes (most visible)
        if context.viewing_angle_shallow:
            level += 1
            
        # Guarantee smooth boundaries (evaluated exactly)
        self.boundary_samples_per_edge = 32
        
        return level
    
    def evaluate_exact_boundaries(self, boundaries: List[ParametricBoundary]):
        """
        Boundaries are evaluated on limit surface, not approximated
        """
        exact_curves = []
        for boundary in boundaries:
            points = []
            for t in np.linspace(0, 1, 128):
                face, u, v = boundary.evaluate(t)
                # Exact limit surface evaluation
                point_3d = self.opensubdiv.evaluate_limit_point(
                    self.subd_surface, face, u, v
                )
                points.append(point_3d)
            exact_curves.append(points)
        return exact_curves
```

### 5.3 Rendering Implementation

```cpp
// C++ Module: subd_evaluator.cpp
#include <opensubdiv/far/topologyRefiner.h>
#include <pybind11/numpy.h>

class SubDEvaluator {
public:
    // Return numpy arrays to Python for display
    py::array_t<float> tessellate(const SubDSurface& surface, 
                                  int level,
                                  bool adaptive = false) {
        // Create OpenSubdiv refiner
        Far::TopologyRefiner* refiner = create_refiner(surface);
        
        if (adaptive) {
            // Refine more at silhouettes and focus areas
            refiner->RefineAdaptive(level);
        } else {
            refiner->RefineUniform(level);
        }
        
        // Get tessellated vertices
        int num_verts = refiner->GetNumVertices(level);
        std::vector<float> vertices(num_verts * 3);
        
        // Evaluate limit surface
        evaluate_limit_surface(refiner, vertices);
        
        // Return to Python as numpy array
        return py::array_t<float>({num_verts, 3}, vertices.data());
    }
    
    // Exact evaluation for boundaries
    Point3D evaluate_limit_point(const SubDSurface& surface,
                                int face_index, 
                                float u, float v) {
        // Use Stam's method for exact evaluation
        return evaluate_catmull_clark_limit(surface, face_index, u, v);
    }
};
```

---

## 6. CONSTRAINT SYSTEM

### 6.1 Three-Tier Validation Hierarchy

```python
class ConstraintValidator:
    """
    Constraints as negotiation, not binary pass/fail.
    Mathematical tensions become aesthetic features.
    """
    
    def validate(self, region: ParametricRegion) -> ConstraintReport:
        report = ConstraintReport()
        
        # Tier 1: Physical Constraints (Must Fix)
        undercuts = self.check_undercuts(region)
        if undercuts.severity > 0.15:  # 15% undercut
            report.add_error("Physical impossibility", undercuts)
        
        # Tier 2: Manufacturing Challenges (Negotiable)
        thin_walls = self.check_wall_thickness(region)
        if thin_walls.min_thickness < 2.5:  # mm
            report.add_warning("Challenging but possible", thin_walls)
        
        # Tier 3: Mathematical Tensions (Aesthetic Features)
        symmetry_break = self.check_symmetry_violation(region)
        if symmetry_break.detected:
            report.add_feature("Intentional asymmetry", symmetry_break)
            
        return report
```

### 6.2 Dance Zone Documentation

```python
class DanceZoneRecorder:
    """
    Document negotiations between mathematical ideals and material constraints.
    These stories become part of the artwork's provenance.
    """
    
    def document_resolution(self, 
                          region: ParametricRegion,
                          constraints: List[Constraint],
                          resolution: Resolution) -> DanceZone:
        zone = DanceZone(
            location=region.id,
            conflicting_constraints=constraints,
            resolution_strategy=resolution.method,
            alternative_resolutions=self.compute_alternatives(constraints),
            aesthetic_interpretation=resolution.artistic_rationale,
            timestamp=datetime.now()
        )
        
        # This becomes part of the piece's permanent record
        self.artwork_provenance.add_dance_zone(zone)
        return zone
```

---

## 7. IMPLEMENTATION ROADMAP

### 7.1 Phase 0: Core Validation (2-3 weeks)
**Objective**: Prove OpenSubdiv integration and parametric approach

- [ ] C++ module with OpenSubdiv for SubD evaluation
- [ ] Basic parametric region structure
- [ ] Single mathematical lens (Spectral)
- [ ] Export to NURBS patches
- [ ] Basic VTK display of tessellated mesh

### 7.2 Phase 1: Interactive Foundation (2-3 months)
**Objective**: Validate user interaction model

- [ ] PyQt6 UI with viewport
- [ ] Real-time tessellation with C++ module
- [ ] Region selection system (mathematical entities)
- [ ] Basic pinning (binary lock/unlock)
- [ ] Boundary editing with pressure model
- [ ] 2-3 mathematical lenses
- [ ] Simple constraint checking

### 7.3 Phase 2: Complete Pipeline (6-8 months)
**Objective**: Production-ready system

- [ ] All 6 mathematical lenses
- [ ] Thermal gradient analysis
- [ ] Slip flow simulation
- [ ] Complete constraint negotiation
- [ ] Dance zone documentation
- [ ] Rhino bidirectional sync
- [ ] Mold generation with registration
- [ ] Multi-viewport display
- [ ] Parametric space viewport

### 7.4 Phase 3: Intelligence Layer (Ongoing)
**Objective**: Learn from usage patterns

- [ ] Pattern recognition in aesthetic choices
- [ ] Suggested decompositions by form type
- [ ] Automated dance zone resolutions
- [ ] Collaborative features
- [ ] Machine learning integration

---

## 8. TECHNICAL SPECIFICATIONS

### 8.1 Performance Requirements

- SubD evaluation: <5ms for 500K vertices (GPU-accelerated)
- Display update: 30+ FPS at subdivision level 4
- Region analysis: <500ms for spectral decomposition
- Boundary editing: Real-time preview (<16ms response)
- Memory: <2GB for typical 200-region decomposition

### 8.2 Data Structures

```python
@dataclass
class ProjectState:
    # Immutable ground truth
    subd_surface: SubDSurface  # From Rhino
    
    # Parametric decomposition
    regions: List[ParametricRegion]
    boundaries: List[ParametricBoundary]
    
    # Analysis cache
    lens_results: Dict[MathematicalLens, LensAnalysis]
    resonance_scores: Dict[MathematicalLens, float]
    
    # Interaction state
    pinned_regions: Set[int]
    selected_entities: List[MathematicalEntity]
    
    # Display cache (regenerated as needed)
    display_mesh: Optional[TriangleMesh]
    subdivision_level: int
    
    # History for undo/redo
    history: List[ProjectState]
    history_index: int
```

### 8.3 File Formats

- **Input**: .3dm (Rhino SubD)
- **Project**: .json (parametric definitions) + .3dm (geometry reference)
- **Export**: 
  - .3dm (NURBS patches for molds)
  - .stl (for 3D printing)
  - .json (dance zone documentation)

---

## 9. KEY INSIGHTS AND PRINCIPLES

### 9.1 The Parametric Advantage
Regions exist as mathematical relationships, not geometry. This enables:
- Lossless editing (no accumulation of numerical error)
- Resolution independence (same definition, different detail levels)
- Clean topology (boundaries guaranteed on surface)

### 9.2 The Display Duality
Mathematical truth vs. visual approximation is not a compromise but proper separation of concerns:
- Mathematics: Exact operations on limit surfaces
- Display: Smooth enough for aesthetic judgment
- Selection: Always operates on mathematical entities

### 9.3 Seams as Features
Following Peter Pincus's philosophy:
- Seam lines reveal mathematical structure
- No post-processing to hide divisions
- Each seam tells the story of negotiation between math and material

### 9.4 Dance Zones as Opportunities
Conflicts between constraints are not failures but creative opportunities:
- Document the negotiation process
- Multiple valid resolutions exist
- The chosen path becomes part of the artwork's identity

---

## 10. APPENDICES

### Appendix A: Mathematical Foundations
[Details of Laplace-Beltrami operators, eigenfunction computation, etc.]

### Appendix B: Ceramic Slip-Casting Constraints
[Comprehensive material properties, flow dynamics, thermal behavior]

### Appendix C: API Specifications
[Detailed interface definitions for C++ modules and Python classes]

### Appendix D: User Interface Wireframes
[UI/UX designs for the desktop application]

---

## REVISION HISTORY

- **v5.0** (2025-01): Parametric region architecture, rendering pipeline clarification, thermal/flow lenses
- **v4.0** (2025-01): Lossless architecture with native desktop application
- **v3.0** (2024-12): Multi-lens analysis system
- **v2.0** (2024-11): Constraint validation framework
- **v1.0** (2024-10): Initial specification

---

## END OF SPECIFICATION
