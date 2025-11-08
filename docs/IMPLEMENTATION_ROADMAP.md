# Ceramic Mold Analyzer - Implementation Roadmap
## Detailed 10-Week Plan to MVP

**Start Date**: January 2025
**Target MVP**: 10 weeks from start
**Approach**: Incremental delivery, test continuously

---

## Overview

**Goal**: Functional desktop application for mathematical decomposition of ceramic mold forms

**Architecture Strategy**: Start pure Python for velocity, pivot to hybrid Python/C++ only when performance bottlenecks emerge (Week 8+)

**MVP Success Criteria**:
- Live Rhino → Desktop app geometry transfer (LOSSLESS - exact SubD via rhino3dm)
- Multi-viewport 3D visualization (VTK)
- ONE working mathematical lens (Differential)
- Panel/Edge edit modes functional
- Iteration system operational
- Basic constraint validation (undercuts)
- Export back to Rhino (LOSSLESS - NURBS, not mesh)

---

## Week-by-Week Breakdown

---

### **WEEK 1: Foundation & VTK Basics**

**Goal**: Get VTK rendering working with test geometry

#### Day 1: Environment Setup ✅ COMPLETE
- [x] Install all dependencies
  ```bash
  pip install vtk==9.3.0 numpy==1.26.2 scipy==1.11.4 requests==2.31.0
  # rhino3dm requires building from source for ARM64
  ```
  - ✅ vtk, numpy, scipy, requests installed and working
  - ✅ PyQt6 reinstalled (6.9.1) - resolved symbol linking issue
  - ✅ rhino3dm 8.17.0 built from source (universal binary: ARM64 + x86_64)

- [x] Create directory structure
  ```bash
  mkdir -p app/{analysis,geometry,constraints}
  mkdir -p tests
  touch app/analysis/__init__.py
  touch app/geometry/__init__.py
  touch app/constraints/__init__.py
  ```
- [x] Set up git ignore for new dependencies
- [x] Test all imports work
- [x] Updated launch.py to auto-configure QT_PLUGIN_PATH

#### Day 2-3: VTK-PyQt6 Integration ✅ COMPLETE
- [x] Replace `viewport_3d.py` placeholder with VTK widget (300 lines)
- [x] Create `QVTKRenderWindowInteractor` widget
- [x] Set up VTK renderer, render window, interactor
- [x] Create test cube method (`create_test_cube()`)
- [x] Implement basic camera controls:
  - [x] Left drag = rotate (orbit) - vtkInteractorStyleTrackballCamera
  - [x] Right drag = pan
  - [x] Scroll = zoom
  - [x] Space = reset camera
- [x] Add axes helper (X/Y/Z indicators in corner widget)
- [x] Add grid plane (XY plane at Z=0, 10x10 grid)
- [x] Add "Show Test Cube" menu item (View → Show Test Cube)
- [x] TEST cube display - Application launches successfully

**Deliverable**: Can see and manipulate a 3D cube ✅
**Status**: COMPLETE - VTK integration tested and working

#### Day 4: Display SubD Geometry ✅ COMPLETE
- [x] Create `app/geometry/subd_display.py`
- [x] Implement `create_vtk_subd_visualization(subd_model)` function
- [x] Create test SubD data using rhino3dm (sphere, torus)
- [x] Display SubD control net in viewport (quad mesh visualization)
- [x] Implement limit surface evaluation for smooth display (VTK subdivision filter)
- [x] Add control face coloring capability (region colors dict)
- [x] Add menu items for test SubD sphere and torus

**Deliverable**: Can display SubD geometry with control net and limit surface evaluation ✅
**Status**: CODE COMPLETE - All SubD display infrastructure implemented

**Files Created**:
- [app/geometry/subd_display.py](app/geometry/subd_display.py) - SubDDisplayModel class, test geometry functions, VTK actor creation
- Updated [app/ui/viewport_3d.py](app/ui/viewport_3d.py) - Added `create_test_subd_sphere()` and `create_test_subd_torus()` methods
- Updated [main.py](main.py) - Added menu items for test SubD geometry

**Note**: rhino3dm 8.17.0 API differs from 8.4.0 - test geometry creation functions need updating to match new API (geometry creation methods changed). Core SubD functionality verified working. Wheel stored at: `../rhino3dm/dist/rhino3dm-8.17.0-cp312-cp312-macosx_13_0_arm64.whl`

#### Day 5: Region Visualization on SubD ✅ COMPLETE
- [x] Implement region coloring system for SubD control faces
- [x] Create `display_regions(subd_model, region_face_ids)` method
- [x] Test with simulated regions (colored groups of control faces)
- [x] Add region selection highlighting framework
- [x] Create test colored cube demonstrating 6 distinct regions
- [x] Add menu item for testing region visualization

**Deliverable**: Can visualize colored regions on SubD control net and limit surface ✅
**Status**: COMPLETE - Region coloring system fully implemented

**Files Modified**:
- [app/geometry/subd_display.py](app/geometry/subd_display.py) - Added `get_colored_control_net_polydata()` for per-face coloring
- [app/ui/viewport_3d.py](app/ui/viewport_3d.py) - Implemented `display_regions()` and `create_test_colored_cube()`
- [main.py](main.py) - Added "Show Colored Cube (Regions)" menu item

**Week 1 Milestone**: ✅ VTK viewport displays SubD geometry with region coloring - **ACHIEVED!**

---

### **WEEK 2: Multi-Viewport System**

**Goal**: Implement viewport layouts and independent cameras

#### Day 1-2: ViewportManager Component
- [ ] Create `app/ui/viewport_manager.py`
- [ ] Implement `ViewportWidget` class (single VTK viewport)
- [ ] Implement `ViewportManager` class (container for multiple viewports)
- [ ] Add layout modes:
  - Single (1 viewport)
  - Side-by-side (2 horizontal)
  - Top/bottom (2 vertical)
  - Quad (4-grid)
- [ ] Test layout switching
- [ ] Ensure proper widget cleanup on layout change

#### Day 3: Independent Cameras
- [ ] Implement per-viewport camera management
- [ ] Create view type presets:
  - Perspective (default)
  - Top (orthographic, Z-axis)
  - Front (orthographic, Y-axis)
  - Right (orthographic, X-axis)
  - Isometric (45° angles)
- [ ] Add view type selector per viewport
- [ ] Test camera synchronization options (optional)
- [ ] Add viewport labeling (show view type)

#### Day 4: Display Modes
- [ ] Implement display mode switching per viewport:
  - Solid (shaded with lighting)
  - Wireframe (edges only)
  - X-ray (transparent with edges)
- [ ] Add display mode selector buttons
- [ ] Test mode switching doesn't affect other viewports
- [ ] Add proper lighting for each mode

#### Day 5: Toolbar Integration
- [ ] Create `app/ui/toolbar.py`
- [ ] Add viewport layout selector buttons (4 icons)
- [ ] Connect layout buttons to ViewportManager
- [ ] Test quick layout switching
- [ ] Add tooltips to buttons
- [ ] Integrate with main window

**Deliverable**: Can switch between 1/2/4 viewport layouts with independent cameras

**Week 2 Milestone**: ✅ Multi-viewport system functional

---

### **WEEK 3: Rhino HTTP Bridge (LOSSLESS ARCHITECTURE)**

**Goal**: Transfer exact SubD representation from Rhino to desktop app with ZERO loss of mathematical fidelity

**⚠️ CRITICAL ARCHITECTURAL PRINCIPLE**: The entire workflow must be LOSSLESS until final G-code export. Do NOT convert SubD → mesh in Grasshopper. This would introduce approximation at the first step and violate the core principle of the system.

#### Day 1-2: Grasshopper SubD Serialization (Lossless)
- [ ] Create `rhino/gh_http_server.py` (new clean implementation)
- [ ] Implement HTTP server using Python's `http.server`
- [ ] Install/import `rhino3dm` library in Grasshopper Python 3
- [ ] Create GET /subd endpoint:
  ```python
  def handle_subd_request():
      # Get SubD from Rhino (DO NOT CONVERT TO MESH!)
      subd = get_subd_from_rhino()

      # Serialize exact SubD using rhino3dm
      subd_json = subd.Encode()  # Preserves Catmull-Clark structure

      # Wrap in JSON envelope
      return {
          "geometry_type": "SubD",
          "version": "rhino3dm_8.4",
          "subd_data": subd_json,
          "metadata": {
              "control_vertex_count": subd.VertexCount,
              "control_face_count": subd.FaceCount,
              "subdivision_level": 0,
              "timestamp": datetime.now().isoformat()
          }
      }
  ```
- [ ] Test SubD serialization in Grasshopper
- [ ] Verify topology and valences are preserved
- [ ] Add error handling for invalid SubD
- [ ] Test server startup in GH Python component

#### Day 2-3: Lossless Transfer Format & Validation
- [ ] Define JSON schema for lossless SubD transfer:
  ```json
  {
    "geometry_type": "SubD",
    "version": "rhino3dm_8.4",
    "subd_data": {
      "control_mesh": {
        "vertices": [[x,y,z], ...],
        "faces": [[v0,v1,v2,v3], ...]
      },
      "topology": {
        "vertex_valences": [4, 5, 3, ...],
        "edge_creases": [[e0, weight], ...],
        "face_adjacency": [[f1, f2], ...]
      },
      "subdivision_scheme": "catmull-clark"
    },
    "metadata": {
      "control_vertex_count": n,
      "control_face_count": m,
      "subdivision_level": 0,
      "timestamp": "..."
    }
  }
  ```
- [ ] Implement lossless serialization in GH
- [ ] Test with various SubD forms (different valences, creases)
- [ ] Validate topology integrity
- [ ] Verify extraordinary vertices (valence ≠ 4) are preserved
- [ ] Test with closed and open SubD surfaces

#### Day 3-4: Python SubD Model (Exact Evaluation)
- [ ] Install `rhino3dm==8.4.0` in Python environment
- [ ] Create `app/geometry/subd_model.py`
- [ ] Implement `SubDModel` class:
  ```python
  import rhino3dm

  class SubDModel:
      """
      Maintains exact SubD representation
      Evaluates limit surface on demand
      NO mesh approximation until display
      """
      def __init__(self, rhino3dm_data):
          # Deserialize exact SubD
          self.subd = rhino3dm.SubD.Decode(rhino3dm_data)

      def evaluate_limit_surface(self, face_id, u, v):
          """
          Exact point on Catmull-Clark limit surface
          Based on Stam (1998) eigenanalysis
          Returns: (point, normal, principal_curvatures)
          """
          return self.subd.LimitSurfacePointFromFace(face_id, u, v)

      def get_display_geometry(self):
          """
          Return SubD for VTK visualization
          VTK will render control net or evaluate limit surface
          Analysis still uses exact evaluation via evaluate_limit_surface()
          """
          return self.subd  # Return exact SubD for visualization
  ```
- [ ] Complete `app/bridge/rhino_bridge.py` implementation
- [ ] Implement polling mechanism (500ms interval)
- [ ] Parse JSON → `SubDModel` object (NOT numpy mesh arrays!)
- [ ] Add connection detection and status signals
- [ ] Add error handling for network issues

#### Day 4: Display vs. Analysis Separation
- [ ] Update `ApplicationState` to store `SubDModel` (not mesh!)
- [ ] Pass SubD directly to VTK for visualization (control net + limit surface)
- [ ] Keep exact SubD model as single source of truth
- [ ] All region definitions reference SubD parameters (face_id, u, v)
- [ ] Test: VTK displays SubD, analysis evaluates limit surface
- [ ] Verify regions remain defined in parameter space
- [ ] Connect bridge to main window
- [ ] Test geometry update on SubD change in Rhino
- [ ] Add loading indicator during fetch

#### Day 5: Lossless Validation & POST Endpoint
- [ ] **CRITICAL TEST**: Verify lossless transfer
  - [ ] Evaluate limit surface in Rhino at (face_id=0, u=0.5, v=0.5)
  - [ ] Evaluate same point in Desktop app
  - [ ] Compare coordinates: error should be < 1e-10 (machine epsilon)
  - [ ] Test with multiple faces and parameter values
  - [ ] Test with extraordinary vertices (valence 3, 5, 6)
- [ ] Document any numerical precision issues
- [ ] Implement POST /molds endpoint in GH (for later)
- [ ] Create mold serialization format (lossless NURBS, not mesh)
- [ ] Implement `send_molds()` in Python client
- [ ] Test round-trip: Python → Rhino
- [ ] Add success/failure feedback

**Deliverable**: Exact SubD in Rhino transfers to desktop app with ZERO mathematical loss

**Week 3 Milestone**: ✅ Lossless SubD transfer - exact limit surface evaluation working

**⚠️ VALIDATION CRITERIA**:
- [ ] Can evaluate limit surface at arbitrary (face_id, u, v) parameters
- [ ] Numerical error vs. Rhino evaluation < 1e-10
- [ ] Topology (vertex valences, edge creases) preserved exactly
- [ ] NO mesh approximation anywhere in pipeline
- [ ] VTK visualizes SubD directly (control net or evaluated limit surface)

---

### **WEEK 4: Edit Mode System** ✅ COMPLETE

**Goal**: Implement face/edge/vertex selection and editing

#### Day 1-2: Edit Mode Infrastructure & VTK Picking System ✅
- [x] Extended `ApplicationState` with edit mode tracking (EditModeManager)
- [x] Added `EditMode` enum: `SOLID | PANEL | EDGE | VERTEX`
- [x] Created edit mode selector in toolbar (4 toggle buttons: S/P/E/V)
- [x] Implemented mode switching logic with visual indicators
- [x] Created `app/ui/picker.py` with SubDFacePicker, SubDEdgePicker, SubDVertexPicker
- [x] Integrated pickers with CustomCameraInteractor via pick callbacks
- [x] LEFT click reserved for selection (no camera movement)
- [x] Shift key detection for multi-select implemented

#### Day 3-4: All Selection Modes Implemented ✅
- [x] **Solid Mode**: View-only, no selection (intentional design)
- [x] **Panel Mode**: Face selection with yellow highlighting
  - Single-click selection
  - Shift+Click multi-select (add/remove from selection)
  - Proper VTK cell picking on mesh faces
- [x] **Edge Mode**: Edge selection with yellow highlighting
  - Edge extraction with VTK filters
  - Cyan wireframe guide for visibility
  - Proper edge selection extraction (only selected edges highlighted)
  - Thick tubular rendering for visibility
- [x] **Vertex Mode**: Vertex selection with yellow spheres
  - Point picking with vtkPointPicker
  - Sphere visualization for selected vertices

#### Day 5: Visual Feedback & Polish ✅
- [x] Unified yellow highlighting for all selection types (1.0, 1.0, 0.0)
- [x] HighlightManager with proper VTK selection extraction
- [x] Selection state tracked per viewport (selected_faces, edges, vertices)
- [x] Geometry actor pickability controlled per mode
- [x] Edge actor created on-demand with proper extraction
- [x] Selection toggle (Shift+Click on selected element deselects it)
- [x] Fixed edge highlighting to show only selected edges (not all)

**Deliverable**: ✅ Can select faces, edges, and vertices with multi-select

**Week 4 Milestone**: ✅ Edit mode system FULLY functional (all 4 modes working)

---

### **WEEK 5: Differential Decomposition** ← CURRENT WEEK

**Goal**: Implement first working mathematical lens operating on exact SubD limit surface

**Parallel Priority**: Fix lossless SubD transfer (rhino3dm .3dm encoding instead of mesh)

#### Day 1: Curvature Computation Infrastructure
- [ ] Create `app/geometry/curvature.py`
- [ ] Implement mesh-based curvature estimation (finite differences):
  - Use existing mesh representation from Rhino bridge
  - Compute face normals and vertex normals
  - Estimate principal curvatures via discrete operators
  - Return κ₁, κ₂, mean curvature H, Gaussian curvature K
- [ ] Test on simple test geometry (sphere, cylinder, saddle)
- [ ] Validate results against known analytical values
- [ ] **Parallel**: Start lossless bridge update (rhino3dm .3dm encoding)

#### Day 2: Differential Analysis Engine
- [ ] Create `app/analysis/differential_decomposition.py`
- [ ] Implement `DifferentialDecomposition` class
- [ ] Sample curvature at mesh face centers
- [ ] Classify faces by curvature type:
  - Elliptic (K > 0, bowl-like)
  - Hyperbolic (K < 0, saddle-like)
  - Parabolic (K ≈ 0, cylindrical)
  - Planar (K ≈ 0 and H ≈ 0)
- [ ] Visualize curvature field (color map on mesh)
- [ ] **Parallel**: Test lossless bridge with .3dm encoding

#### Day 3: Region Discovery Algorithm
- [ ] Implement region growing from curvature coherence:
  - Seed regions from curvature extrema
  - Grow regions using connected component analysis
  - Merge small regions into neighbors (min size threshold)
- [ ] Extract region boundaries (edge loops between regions)
- [ ] Convert discovered regions to `ParametricRegion` objects
- [ ] Compute resonance score (curvature coherence within region)
- [ ] Test on various mesh forms

#### Day 4: UI Integration
- [ ] Connect Differential lens to "Analyze" button in main window
- [ ] Display discovered regions in viewport (colored by region)
- [ ] Update region list widget with discovered regions
- [ ] Show unity principle: "Similar curvature behavior: [type]"
- [ ] Display unity strength (resonance score) as progress bar
- [ ] Add analysis progress indicator (QProgressDialog)
- [ ] Test full workflow: Load geometry → Analyze → View regions

#### Day 5: Testing, Refinement & Documentation
- [ ] Test on simple forms (sphere: 1 region, torus: 2-3 regions)
- [ ] Test on complex organic forms (multiple curvature types)
- [ ] Tune parameters:
  - Curvature classification thresholds
  - Minimum region size (faces)
  - Region growing tolerance
- [ ] Add user parameter dialog (optional advanced settings)
- [ ] Document what works well vs. poorly
- [ ] **Finalize lossless bridge** - validate exact SubD transfer
- [ ] Update documentation with Week 5 completion

**Deliverables**:
1. ✅ Differential lens discovers curvature-based regions
2. ✅ Lossless SubD transfer via rhino3dm .3dm encoding (exact, not mesh)

**Week 5 Milestone**: ✅ First mathematical lens working + Lossless architecture validated

**Note on Architecture**: This implementation uses mesh-based curvature estimation (adequate for MVP). If performance bottlenecks emerge in Week 8+, we'll migrate to exact SubD limit surface evaluation via OpenSubdiv C++ module. The interface remains the same - only the implementation changes.

---

### **WEEK 6: Iteration Management System**

**Goal**: Save/load/compare design snapshots

#### Day 1-2: Iteration Data Structure
- [ ] Create `app/state/iteration.py`
- [ ] Implement `DesignIteration` dataclass:
  ```python
  @dataclass
  class DesignIteration:
      id: int
      name: str
      timestamp: datetime
      regions: List[ParametricRegion]
      viewport_states: List[Dict]
      thumbnail: Optional[QPixmap]
      lens_used: str
      parameters: Dict
      subd_data: Dict  # Exact SubD representation (rhino3dm serialized)
  ```
- [ ] Extend `ApplicationState` with iteration tracking
- [ ] Implement save/load iteration methods (preserve exact SubD)
- [ ] Test state serialization (verify SubD lossless roundtrip)

#### Day 2-3: Iteration Sidebar UI
- [ ] Create `app/ui/iteration_panel.py`
- [ ] Implement collapsible sidebar (expanded/icon-only modes)
- [ ] Display iteration list with thumbnails
- [ ] Add "New Iteration" button
- [ ] Add "Duplicate Iteration" button
- [ ] Add "Delete Iteration" button (min 1 required)
- [ ] Implement iteration selection
- [ ] Add timestamp display

#### Day 3-4: Thumbnail Generation
- [ ] Implement viewport screenshot capture
- [ ] Create thumbnail on iteration save (256x256px)
- [ ] Display thumbnail in iteration list
- [ ] Add hover preview (larger thumbnail)
- [ ] Test thumbnail quality

#### Day 4-5: Iteration Switching
- [ ] Implement iteration loading
- [ ] Restore regions, viewport states, settings
- [ ] Update all UI components on switch
- [ ] Add transition animation (optional)
- [ ] Test switching preserves state correctly
- [ ] Test with multiple iterations (5-10)

**Deliverable**: Can save design snapshots and switch between them

**Week 6 Milestone**: ✅ Iteration system enables non-destructive exploration

---

### **WEEK 7: Constraint Validation**

**Goal**: Implement physical constraint checking

#### Day 1-2: Undercut Detection
- [ ] Create `app/constraints/physical.py`
- [ ] Implement `UndercutDetector` class
- [ ] Ray casting method:
  - For each face, cast ray along draft direction
  - Check for intersections with other faces
  - Faces with upward-facing intersections = undercuts
- [ ] Test on known problematic geometries
- [ ] Visualize undercuts in 3D (red overlay)
- [ ] Add to constraint panel

#### Day 2-3: Constraint Validation Pipeline
- [ ] Create `app/constraints/validator.py`
- [ ] Implement `ConstraintValidator` class
- [ ] Define 3-tier system:
  - Tier 1: Physical (must fix)
  - Tier 2: Manufacturing (warnings)
  - Tier 3: Mathematical (documentation)
- [ ] Implement validation workflow
- [ ] Return structured results:
  ```python
  {
      'physical': {
          'undercuts': True/False,
          'details': [...]
      },
      'manufacturing': {...},
      'mathematical': {...}
  }
  ```

#### Day 3: Draft Angle Analysis on SubD
- [ ] Implement draft angle computation per SubD control face
- [ ] Evaluate limit surface normal at face centers
- [ ] Check against minimum threshold (0.5°)
- [ ] Classify as pass/warning/fail
- [ ] Visualize draft angle gradient on SubD control net
- [ ] Add to constraint panel

#### Day 4: Constraint Panel Integration
- [ ] Update `constraint_panel.py` with real data
- [ ] Display validation results by tier
- [ ] Color-code: ✅ green (pass), ⚠️ orange (warning), ❌ red (fail)
- [ ] Show detailed violation information
- [ ] Add "Details" expandable sections
- [ ] Link violations to 3D visualization (click to highlight)

#### Day 5: Real-Time Validation
- [ ] Connect validation to edit mode changes
- [ ] Re-validate on region modification
- [ ] Update constraint panel automatically
- [ ] Add validation progress indicator
- [ ] Test performance with complex SubD forms
- [ ] Disable "Generate Molds" button if fatal violations exist

**Deliverable**: Physical constraint validation working with visual feedback

**Week 7 Milestone**: ✅ Basic constraint system operational

---

### **WEEK 8: Mold Generation & Export (LOSSLESS)**

**Goal**: Generate NURBS mold geometry from SubD and send back to Rhino

#### Day 1-2: Draft Transformation on SubD Limit Surface
- [ ] Create `app/geometry/draft.py`
- [ ] Implement draft angle application on evaluated limit surface:
  - Evaluate SubD limit surface at grid of (face_id, u, v) parameters
  - For each evaluated point, offset along exact limit surface normal
  - Offset distance = depth × tan(draft_angle)
  - Depth = distance from parting plane
- [ ] Test on simple SubD geometries
- [ ] Verify correctness (measure actual angles)
- [ ] Handle edge cases (extraordinary vertices)

#### Day 2-3: NURBS Mold Surface Generation
- [ ] Create `app/geometry/mold_generator.py`
- [ ] Implement `MoldGenerator` class
- [ ] For each parametric region:
  - Evaluate SubD limit surface at region parameters
  - Apply draft transformation to evaluated points
  - Fit NURBS surface through drafted points (exact, analytical)
  - Add wall thickness via NURBS offset
  - Create solid Brep volume (exact Boolean operations)
- [ ] Generate parting plane location
- [ ] Test NURBS mold piece generation

#### Day 3-4: Export to Rhino (NURBS, not mesh!)
- [ ] Implement NURBS mold serialization format
- [ ] Convert NURBS Breps to rhino3dm format
- [ ] Send via HTTP POST /molds (exact NURBS geometry)
- [ ] Test import in Rhino (verify NURBS preserved)
- [ ] Verify geometry accuracy (no mesh approximation)
- [ ] Add metadata (region ID, parameters)

#### Day 4-5: Generate Molds Button
- [ ] Create generation parameters dialog:
  - Draft direction selector
  - Draft angle slider (0-5°)
  - Wall thickness slider (3-6mm)
  - Mold wall thickness (38-51mm)
- [ ] Connect to "Generate Molds" button
- [ ] Show progress during generation
- [ ] Display results in viewport
- [ ] Enable "Send to Rhino" button
- [ ] Test complete workflow

**Deliverable**: Can generate simple molds and send to Rhino

**Week 8 Milestone**: ✅ End-to-end pipeline functional

---

### **WEEK 9: Polish & Refinement**

**Goal**: Bug fixes, performance, user experience

#### Day 1: Performance Optimization
- [ ] Profile slow operations (Python `cProfile`)
- [ ] Optimize SubD evaluation operations (cache limit surface queries)
- [ ] Add caching where appropriate (evaluated points, curvatures)
- [ ] Test with large SubD forms (>10k control faces)
- [ ] Implement adaptive limit surface sampling if needed
- [ ] Add async operations for heavy computation

#### Day 2: Error Handling
- [ ] Add try/except blocks around critical operations
- [ ] Implement graceful degradation
- [ ] Add user-friendly error messages
- [ ] Handle connection loss gracefully
- [ ] Add validation for user inputs
- [ ] Test edge cases and failure modes

#### Day 3: User Experience Polish
- [ ] Add loading indicators for all operations
- [ ] Improve visual feedback (hover states, tooltips)
- [ ] Add keyboard shortcuts reference (Help menu)
- [ ] Implement status bar messages
- [ ] Add progress bars for long operations
- [ ] Test workflow from user perspective

#### Day 4: Visual Polish
- [ ] Refine color schemes (check UX design)
- [ ] Improve region coloring (distinct, accessible)
- [ ] Add smooth transitions/animations
- [ ] Improve lighting in viewports
- [ ] Add ambient occlusion (optional)
- [ ] Test on high-DPI displays

#### Day 5: Documentation
- [ ] Write user guide (basic workflow)
- [ ] Document all keyboard shortcuts
- [ ] Create troubleshooting guide
- [ ] Add inline help text
- [ ] Document known limitations
- [ ] Update README with screenshots

**Week 9 Milestone**: ✅ Polished, professional application

---

### **WEEK 10: Testing & Validation**

**Goal**: Comprehensive testing with real ceramic forms

#### Day 1-2: Unit Testing
- [ ] Set up pytest framework
- [ ] Write tests for state management
- [ ] Write tests for geometry operations
- [ ] Write tests for curvature computation
- [ ] Write tests for constraint validation
- [ ] Achieve >70% code coverage

#### Day 2-3: Integration Testing
- [ ] Test Rhino bridge with various forms
- [ ] Test analysis workflow end-to-end
- [ ] Test edit mode workflows
- [ ] Test iteration system
- [ ] Test constraint validation
- [ ] Test mold generation

#### Day 3-4: Real-World Testing
- [ ] Test with simple ceramic forms (sphere, cylinder)
- [ ] Test with complex organic forms
- [ ] Test with forms of various genus (0, 1, 2+)
- [ ] Document which lens works best for which forms
- [ ] Identify failure modes
- [ ] Create test suite of reference forms

#### Day 4-5: Bug Fixing & Final Polish
- [ ] Fix all critical bugs discovered in testing
- [ ] Address performance issues
- [ ] Refine UI based on testing feedback
- [ ] Final documentation pass
- [ ] Create demo video (optional)
- [ ] Prepare for release

**Week 10 Milestone**: ✅ **MVP COMPLETE**

---

## Success Checklist

### MVP Requirements Met

- [ ] ✅ Desktop app launches and runs stably
- [ ] ✅ Multi-viewport system (1/2/4 layouts) working
- [ ] ✅ VTK 3D visualization displays SubD geometry (control net + limit surface)
- [ ] ✅ Live HTTP bridge transfers exact SubD from Rhino (lossless)
- [ ] ✅ Differential lens discovers curvature-based regions via limit surface evaluation
- [ ] ✅ Regions visualized with distinct colors on SubD
- [ ] ✅ Panel edit mode selects and modifies SubD control faces
- [ ] ✅ Edge edit mode adjusts parametric boundaries
- [ ] ✅ Pin regions to preserve across re-analysis
- [ ] ✅ Iteration system saves/loads design snapshots (preserves exact SubD)
- [ ] ✅ Undercut detection validates manufacturability
- [ ] ✅ Mold generation creates NURBS mold pieces from SubD
- [ ] ✅ Export sends NURBS molds back to Rhino (lossless)
- [ ] ✅ User can complete full lossless workflow start to finish

---

## Post-MVP Roadmap (Weeks 11-16)

### Week 11-12: Second Mathematical Lens
- Implement Spectral decomposition (Laplacian eigenvalues)
- Compare results with Differential lens
- Add lens comparison mode

### Week 13: Third Mathematical Lens
- Implement Flow/Geodesic decomposition (heat method)
- Test on various form types
- Document resonance patterns

### Week 14: Enhanced NURBS Surface Generation
- Refine NURBS mold surface quality
- Implement advanced surface fitting techniques
- Optimize NURBS degree and control point placement
- Test manufacturability on complex forms

### Week 15: Advanced Constraints
- Implement all Tier 2 manufacturing checks
- Add auto-fix suggestions
- Implement constraint-guided editing

### Week 16: File I/O & Polish
- Save/load session files
- Export to STL, STEP, IGES
- Final polish and optimization
- User documentation complete

---

## Development Practices

### Daily Workflow
1. Start day: Review previous day's work
2. Run existing tests
3. Implement feature incrementally
4. Test continuously (manual + automated)
5. Commit working code frequently
6. Document as you go
7. End day: Update progress, plan tomorrow

### Testing Strategy
- Write tests alongside features (not after)
- Test with real geometry frequently
- Manual testing in addition to automated
- Get user feedback early and often

### Code Quality
- Follow PEP 8 style guide
- Use type hints consistently
- Document complex algorithms
- Keep functions small and focused
- Avoid premature optimization

### Git Workflow
- Commit working code frequently
- Use descriptive commit messages
- Branch for experimental features
- Tag milestones (Week 1, Week 2, etc.)
- Don't commit broken code to main

---

## Risk Mitigation

### If Behind Schedule
**Priority 1 (Must have for MVP)**:
- VTK multi-viewport
- Rhino HTTP bridge
- One mathematical lens
- Panel edit mode
- Basic undercut check

**Priority 2 (Nice to have)**:
- Edge edit mode
- Iteration system
- Full constraint validation

**Priority 3 (Post-MVP)**:
- Vertex edit mode
- Additional lenses
- NURBS generation

### If Blocked
- **VTK issues**: Start with simpler visualization (matplotlib 3D), migrate later
- **Math problems**: Consult research papers, computational geometry experts
- **Performance**: Profile first, optimize bottlenecks, consider C++ extensions
- **Scope creep**: Defer nice-to-haves, focus on core MVP

---

## Dependencies Between Weeks

```
Week 1 (VTK) → Week 2 (Multi-viewport) → Week 4 (Edit modes)
                                      ↘
Week 3 (HTTP Bridge) ─────────────────→ Week 5 (Math lens)
                                         ↓
Week 6 (Iterations) ←───────────────── Week 7 (Constraints)
       ↓                                  ↓
Week 8 (Mold generation & Export) ───→ Week 9 (Polish)
                                         ↓
                                    Week 10 (Testing)
```

---

## Resources

### VTK Learning
- VTK User's Guide: https://vtk.org/doc/nightly/html/
- VTK Examples: https://kitware.github.io/vtk-examples/site/
- PyQt VTK Integration: Search "QVTKRenderWindowInteractor"

### Computational Geometry
- Discrete Differential Geometry (CMU course notes)
- "Polygon Mesh Processing" by Botsch et al.
- libigl tutorials: https://libigl.github.io/tutorial/

### HTTP/JSON
- Python `requests` library docs
- Python `http.server` module docs
- JSON serialization best practices

---

## Architecture Pivot Strategy (Weeks 8+)

### When to Pivot from Pure Python to Hybrid Python/C++

**Stay Pure Python While:**
- ✅ UI development is rapid (2-3 day feature cycles)
- ✅ Working with test geometry (<5K control points)
- ✅ Mathematical algorithms prototyping
- ✅ Curvature/eigensolvers complete in <2 seconds
- ✅ Multi-viewport rendering >30 FPS
- ✅ Real-time interaction feels responsive

**Pivot to Hybrid When (Week 8+ decision point):**
- 🚨 Real-time SubD evaluation becomes sluggish (>100ms)
- 🚨 Multi-viewport rendering drops below 30 FPS
- 🚨 Spectral analysis (eigensolvers) takes >5 seconds
- 🚨 Working with production-scale models (10K-50K control points)
- 🚨 Testing with actual light fixture designs shows performance issues

### Hybrid Architecture Migration Path

**IF performance bottlenecks emerge, migrate ONLY slow operations:**

1. **Week 8-9: Profile and Measure**
   - Use Python `cProfile` to identify bottlenecks
   - Test with real ceramic forms from portfolio
   - Measure specific operations (curvature computation, eigensolvers, rendering)
   - Document which operations are too slow

2. **Week 10+: Selective C++ Migration**
   - **Migrate to C++** (via pybind11):
     - SubD limit surface evaluation → OpenSubdiv
     - NURBS operations → OpenCASCADE
     - Heavy geometry operations
   - **Keep in Python**:
     - All UI code (PyQt6)
     - State management
     - Workflow orchestration
     - SciPy eigensolvers (already calls LAPACK - adequate)

3. **Architecture: Hybrid Python/C++ Pattern**
   ```
   Python Layer (UI/Orchestration)
       ↕ pybind11 bindings
   C++ Layer (Geometry Kernel)
       - OpenCASCADE (NURBS)
       - OpenSubdiv (exact SubD limit evaluation)
   ```

**This is the FreeCAD pattern - proven with 300K+ users.**

### Lossless Architecture Priority

**The mesh vs. SubD transfer issue is ORTHOGONAL to Python/C++ question.**

**Fix lossless transfer in Week 5** (pure Python solution):
- Use rhino3dm .3dm encoding (exact SubD, not mesh)
- Binary .3dm format via base64 over HTTP
- No C++ required - rhino3dm Python library handles it

**Current:** Grasshopper → Mesh → JSON → Python ❌ Violates lossless principle
**Target:** Grasshopper → SubD → .3dm → Python ✅ Maintains exact representation

This maintains lossless architecture using pure Python until Week 8+.

---

## Conclusion

This roadmap provides a structured path to MVP in 10 weeks. The key is incremental delivery - each week builds on the previous, with clear milestones and deliverables.

**Critical Path**: VTK (Week 1-2) → HTTP Bridge (Week 3) → Edit Modes (Week 4) → Math Lens (Week 5)

Everything else supports this critical path. If behind schedule, protect these features first.

**Architecture Strategy**: Start pure Python for velocity, pivot to hybrid Python/C++ only when measured performance bottlenecks emerge (Week 8+). Fix lossless transfer in Week 5 using pure Python (rhino3dm library).

**Success depends on**:
- Daily progress and testing
- Focus on MVP scope (resist feature creep)
- Getting user feedback early
- Iterating based on real ceramic forms
- Data-driven architecture decisions (profile before optimizing)

---

*Document Version: 1.1*
*Last Updated: November 2025*
*See: PROJECT_STATUS.md for current progress*
