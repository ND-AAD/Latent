# 10-Day Sprint Strategy: Maximum Parallelization

**Deadline**: 10 days
**Budget**: $1000 API credits
**Strategy**: Run 6-8 agents in parallel simultaneously for maximum velocity
**Goal**: Complete Phase 0 + Phase 1 MVP in 10 days

---

## Executive Summary

**With maximum parallelization, we can complete the MVP in 10 days for ~$400-600.**

### Aggressive Timeline

| Days | Phase | Agents | Cost |
|------|-------|--------|------|
| **1-2** | Phase 0: C++ Core | 6 agents | $80-120 |
| **3-5** | Phase 1a: UI + Analysis | 8 agents | $150-250 |
| **6-8** | Phase 1b: Constraints + Molds | 6 agents | $120-180 |
| **9-10** | Testing + Polish + Docs | 4 agents | $50-80 |
| **Total** | **10 days** | **24 agents** | **$400-630** |

**Reserve**: $370-600 for debugging, iteration, and contingency

---

## Critical Success Factors

### 1. Maximum Parallelization
- Run **6-8 agents simultaneously** (vs 3-4 in original plan)
- Launch agents in **2-3 batches per day** (vs 1 batch)
- Work **12-14 hour days** during sprint

### 2. Your Role (Orchestrator)
**This is critical**: You must be available for **8-12 hours per day** to:
- Review agent outputs as they complete (every 2-4 hours)
- Test and integrate code immediately
- Fix compilation/integration issues
- Launch next batch of agents

**Time commitment**: 80-120 hours over 10 days (8-12 hours/day)

### 3. Pre-Sprint Preparation (Day 0)
**Before launching any agents**, you must:
- Install all dependencies (OpenSubdiv, CMake, pybind11, TBB)
- Set up directory structure
- Create initial CMakeLists.txt template
- Test basic C++ → Python compilation
- Ensure Rhino/Grasshopper ready

**Estimated time**: 3-4 hours

---

## Day-by-Day Battle Plan

### DAY 0 (PREPARATION - Do this first!)

**Your Tasks** (3-4 hours):
```bash
# Install all dependencies
brew install cmake pybind11 tbb

# Build OpenSubdiv with Metal backend
cd ~/Downloads
git clone https://github.com/PixarAnimationStudios/OpenSubdiv.git
cd OpenSubdiv
git checkout v3_6_0
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release \
         -DCMAKE_INSTALL_PREFIX=/usr/local \
         -DNO_EXAMPLES=ON -DNO_TUTORIALS=ON \
         -DNO_REGRESSION=ON -DNO_DOC=ON -DNO_TESTS=ON \
         -DOSD_ENABLE_METAL=ON
make -j$(sysctl -n hw.ncpu)
sudo make install

# Verify installation
pkg-config --modversion opensubdiv  # Should show 3.6.0

# Create project structure
cd /path/to/Latent
mkdir -p cpp_core/{geometry,analysis,constraints,python_bindings,utils}
mkdir -p ceramic_mold_analyzer/app/{bridge,ui,state,analysis}
mkdir -p rhino tests docs

# Test basic pybind11
python3 -c "import pybind11; print(pybind11.get_include())"
```

**Deliverable**: All dependencies installed, project structure ready

---

### DAY 1: C++ CORE FOUNDATION (6 agents in parallel)

**Morning Launch** (9am - Launch 6 agents):

**Agent 1**: Types & Data Structures
```
Files: cpp_core/geometry/types.h
Task: Define Point3D, SubDControlCage, TessellationResult
Estimated: 30K tokens, $2-3, 2 hours
```

**Agent 2**: SubDEvaluator Header
```
Files: cpp_core/geometry/subd_evaluator.h
Task: Define SubDEvaluator class interface
Estimated: 30K tokens, $2-3, 2 hours
```

**Agent 3**: CMakeLists.txt
```
Files: cpp_core/CMakeLists.txt, setup.py
Task: Complete build system with OpenSubdiv linking
Estimated: 40K tokens, $2-4, 2-3 hours
```

**Agent 4**: SubDEvaluator Core Implementation
```
Files: cpp_core/geometry/subd_evaluator.cpp
Task: Implement initialize() and basic TopologyRefiner
Estimated: 80K tokens, $5-8, 4-5 hours
```

**Agent 5**: pybind11 Bindings
```
Files: cpp_core/python_bindings/py_bindings.cpp
Task: Create Python bindings for all classes
Estimated: 60K tokens, $4-6, 3-4 hours
```

**Agent 6**: Grasshopper Server
```
Files: rhino/gh_subd_server.py
Task: HTTP server with control cage extraction
Estimated: 40K tokens, $1-2, 2-3 hours
```

**Afternoon Integration** (2pm-6pm - You):
- Merge all agent outputs
- Build C++ module: `cd cpp_core/build && cmake .. && make`
- Test Python bindings: `python3 test_bindings.py`
- Test Grasshopper server: `curl localhost:8888/status`

**Evening Launch** (6pm - Launch 3 agents):

**Agent 7**: Complete Tessellation
```
Files: cpp_core/geometry/subd_evaluator.cpp (tessellate method)
Task: Implement full uniform refinement and triangulation
Estimated: 100K tokens, $6-10, 5-6 hours
```

**Agent 8**: Desktop Bridge
```
Files: ceramic_mold_analyzer/app/bridge/rhino_bridge.py
Task: Implement RhinoBridge with C++ integration
Estimated: 50K tokens, $3-5, 3-4 hours
```

**Agent 9**: Basic Tests
```
Files: tests/test_subd_evaluator.py, tests/test_bridge.py
Task: Create initial test suite
Estimated: 40K tokens, $1-2, 2-3 hours
```

**Day 1 Evening**: Test end-to-end: Rhino → HTTP → C++ → Tessellation

**Day 1 Totals**:
- **9 agents** launched
- **Cost**: $26-43
- **Deliverable**: Complete SubD tessellation pipeline working

---

### DAY 2: LIMIT EVALUATION + VTK (6 agents in parallel)

**Morning Launch** (9am - Launch 6 agents):

**Agent 10**: Limit Surface Evaluation
```
Files: cpp_core/geometry/subd_evaluator.cpp (evaluate_limit_point)
Task: Implement Stam evaluation with PatchTable
Estimated: 100K tokens, $6-10, 5-6 hours
```

**Agent 11**: VTK Viewport Base
```
Files: ceramic_mold_analyzer/app/ui/viewport_3d.py
Task: Create basic VTK viewport with camera controls
Estimated: 80K tokens, $5-8, 4-5 hours
```

**Agent 12**: VTK SubD Display
```
Files: ceramic_mold_analyzer/app/ui/viewport_3d.py (display_cpp_subd)
Task: Render tessellated SubD in VTK
Estimated: 60K tokens, $4-6, 3-4 hours
```

**Agent 13**: Multi-Viewport Layout
```
Files: ceramic_mold_analyzer/app/ui/viewport_layout.py
Task: Implement 4-viewport layout system
Estimated: 70K tokens, $4-7, 4-5 hours
```

**Agent 14**: Application State
```
Files: ceramic_mold_analyzer/app/state/app_state.py
Task: Centralized state with undo/redo
Estimated: 60K tokens, $4-6, 3-4 hours
```

**Agent 15**: Main Window
```
Files: ceramic_mold_analyzer/main.py, launch.py
Task: PyQt6 main window with menu system
Estimated: 50K tokens, $3-5, 3-4 hours
```

**Afternoon Integration** (2pm-6pm):
- Integrate VTK visualization
- Test multi-viewport rendering
- Visual check: SubD displays smoothly

**Evening Launch** (6pm - Launch 2 agents):

**Agent 16**: Lossless Validation Tests
```
Files: tests/test_lossless.py, tests/fixtures/
Task: Create comprehensive validation suite
Estimated: 60K tokens, $2-4, 3-4 hours
```

**Agent 17**: Phase 0 Documentation
```
Files: docs/PHASE_0_COMPLETE.md, docs/API_REFERENCE.md
Task: Complete Phase 0 documentation
Estimated: 60K tokens, $2-4, 3-4 hours
```

**Day 2 Evening**: Run all tests, verify lossless architecture

**Day 2 Totals**:
- **8 agents** launched
- **Cost**: $30-50
- **Deliverable**: ✅ **PHASE 0 COMPLETE** - Full visualization working

**Phase 0 Total**: $56-93 (Days 1-2)

---

### DAY 3: UI FOUNDATION (8 agents in parallel!)

**Morning Launch** (9am - Launch 8 agents):

**Agent 18**: Edit Mode Manager
```
Files: ceramic_mold_analyzer/app/state/edit_mode.py
Task: S/P/E/V mode state management
Estimated: 50K tokens, $3-5, 3-4 hours
```

**Agent 19**: Face Picker
```
Files: ceramic_mold_analyzer/app/ui/picker.py (SubDFacePicker)
Task: Triangle→Face mapping picker
Estimated: 60K tokens, $4-6, 3-4 hours
```

**Agent 20**: Edge Picker
```
Files: ceramic_mold_analyzer/app/ui/picker.py (SubDEdgePicker)
Task: Edge selection with highlighting
Estimated: 60K tokens, $4-6, 3-4 hours
```

**Agent 21**: Vertex Picker
```
Files: ceramic_mold_analyzer/app/ui/picker.py (SubDVertexPicker)
Task: Vertex selection on control cage
Estimated: 50K tokens, $3-5, 3-4 hours
```

**Agent 22**: Edit Mode Toolbar
```
Files: ceramic_mold_analyzer/app/ui/edit_mode_toolbar.py
Task: S/P/E/V mode selector UI
Estimated: 40K tokens, $2-4, 2-3 hours
```

**Agent 23**: Parametric Region
```
Files: ceramic_mold_analyzer/app/state/parametric_region.py
Task: Region data structure and management
Estimated: 50K tokens, $3-5, 3-4 hours
```

**Agent 24**: Region List UI
```
Files: ceramic_mold_analyzer/app/ui/region_list.py
Task: Region list with pin/unpin
Estimated: 60K tokens, $4-6, 3-4 hours
```

**Agent 25**: Region Visualization
```
Files: ceramic_mold_analyzer/app/ui/region_renderer.py
Task: Color-code regions on tessellated mesh
Estimated: 60K tokens, $4-6, 3-4 hours
```

**Afternoon Integration** (2pm-6pm):
- Integrate all edit modes
- Test face/edge/vertex selection
- Test region creation and visualization

**Day 3 Totals**:
- **8 agents** launched
- **Cost**: $27-47
- **Deliverable**: Complete edit mode system + region management

---

### DAY 4: CURVATURE ANALYSIS (6 agents in parallel)

**Morning Launch** (9am - Launch 6 agents):

**Agent 26**: C++ Curvature Analyzer Header
```
Files: cpp_core/analysis/curvature_analyzer.h
Task: Define CurvatureAnalyzer interface
Estimated: 40K tokens, $2-4, 2-3 hours
```

**Agent 27**: C++ Curvature Implementation
```
Files: cpp_core/analysis/curvature_analyzer.cpp
Task: Implement exact curvature from limit derivatives
Estimated: 120K tokens, $7-12, 6-7 hours
```

**Agent 28**: Curvature Python Bindings
```
Files: cpp_core/python_bindings/py_bindings.cpp (curvature)
Task: Add pybind11 bindings for curvature
Estimated: 40K tokens, $2-4, 2-3 hours
```

**Agent 29**: Curvature Visualization
```
Files: ceramic_mold_analyzer/app/analysis/curvature_viz.py
Task: Color mesh by mean/Gaussian curvature
Estimated: 60K tokens, $4-6, 3-4 hours
```

**Agent 30**: Curvature Tests
```
Files: tests/test_curvature.py, tests/fixtures/sphere.json
Task: Validate curvature on known geometries
Estimated: 50K tokens, $2-3, 2-3 hours
```

**Agent 31**: Analysis Panel UI
```
Files: ceramic_mold_analyzer/app/ui/analysis_panel.py
Task: Lens selector and parameters UI
Estimated: 60K tokens, $4-6, 3-4 hours
```

**Afternoon Integration** (2pm-6pm):
- Build C++ with curvature analyzer
- Test curvature computation (sphere: H=1/r, K=1/r²)
- Test visualization

**Evening Launch** (6pm - Launch 2 agents):

**Agent 32**: Differential Decomposition
```
Files: ceramic_mold_analyzer/app/analysis/differential_decomposition.py
Task: Region discovery from curvature classification
Estimated: 100K tokens, $6-10, 5-6 hours
```

**Agent 33**: Iteration System
```
Files: ceramic_mold_analyzer/app/state/iteration.py, app/ui/iteration_panel.py
Task: Design iteration snapshots with thumbnails
Estimated: 80K tokens, $5-8, 4-5 hours
```

**Day 4 Totals**:
- **8 agents** launched
- **Cost**: $32-53
- **Deliverable**: Curvature analysis + differential lens working

---

### DAY 5: SPECTRAL ANALYSIS + INTEGRATION (6 agents in parallel)

**Morning Launch** (9am - Launch 6 agents):

**Agent 34**: Laplacian Matrix Builder
```
Files: ceramic_mold_analyzer/app/analysis/laplacian.py
Task: Build cotangent-weight Laplacian
Estimated: 70K tokens, $4-7, 4-5 hours
```

**Agent 35**: Spectral Decomposition
```
Files: ceramic_mold_analyzer/app/analysis/spectral_decomposition.py
Task: Eigenvalue solver and nodal domain extraction
Estimated: 90K tokens, $5-9, 5-6 hours
```

**Agent 36**: Spectral Visualization
```
Files: ceramic_mold_analyzer/app/analysis/spectral_viz.py
Task: Visualize eigenfunctions and nodal lines
Estimated: 60K tokens, $4-6, 3-4 hours
```

**Agent 37**: Region Merge/Split Tools
```
Files: ceramic_mold_analyzer/app/ui/region_tools.py
Task: UI for merging and splitting regions
Estimated: 70K tokens, $4-7, 4-5 hours
```

**Agent 38**: Lens Integration
```
Files: ceramic_mold_analyzer/app/analysis/lens_manager.py
Task: Unified interface for all mathematical lenses
Estimated: 60K tokens, $4-6, 3-4 hours
```

**Agent 39**: Analysis Tests
```
Files: tests/test_differential.py, tests/test_spectral.py
Task: Comprehensive analysis testing
Estimated: 60K tokens, $2-4, 3-4 hours
```

**Afternoon Integration** (2pm-6pm):
- Test all mathematical lenses
- Verify region discovery on multiple forms
- Test iteration system

**Day 5 Totals**:
- **6 agents** launched
- **Cost**: $23-39
- **Deliverable**: All mathematical lenses operational

**Days 3-5 Total**: $82-139 (Phase 1a: UI + Analysis)

---

### DAY 6: CONSTRAINT VALIDATION (6 agents in parallel)

**Morning Launch** (9am - Launch 6 agents):

**Agent 40**: C++ Constraint Validator Header
```
Files: cpp_core/constraints/validator.h
Task: Define UndercutDetector and DraftChecker interfaces
Estimated: 50K tokens, $3-5, 2-3 hours
```

**Agent 41**: Undercut Detection
```
Files: cpp_core/constraints/validator.cpp (undercut)
Task: Ray-casting undercut detection
Estimated: 100K tokens, $6-10, 5-6 hours
```

**Agent 42**: Draft Angle Checker
```
Files: cpp_core/constraints/validator.cpp (draft)
Task: Draft angle computation per face
Estimated: 80K tokens, $5-8, 4-5 hours
```

**Agent 43**: Constraint Python Bindings
```
Files: cpp_core/python_bindings/py_bindings.cpp (constraints)
Task: pybind11 bindings for validators
Estimated: 40K tokens, $2-4, 2-3 hours
```

**Agent 44**: Constraint UI Panel
```
Files: ceramic_mold_analyzer/app/ui/constraint_panel.py
Task: 3-tier constraint display (binary/warning/aesthetic)
Estimated: 70K tokens, $4-7, 4-5 hours
```

**Agent 45**: Constraint Visualization
```
Files: ceramic_mold_analyzer/app/ui/constraint_viz.py
Task: Highlight undercuts and draft issues
Estimated: 60K tokens, $4-6, 3-4 hours
```

**Afternoon Integration** (2pm-6pm):
- Build C++ with constraint validators
- Test undercut detection
- Test draft angle checking

**Day 6 Totals**:
- **6 agents** launched
- **Cost**: $24-40
- **Deliverable**: Constraint validation working

---

### DAY 7: OPENCASCADE + NURBS (6 agents in parallel)

**Morning Preparation** (You - 1 hour):
```bash
# Install OpenCASCADE
brew install opencascade

# Update CMakeLists.txt to find OCCT
# Test basic OCCT compilation
```

**Morning Launch** (10am - Launch 6 agents):

**Agent 46**: NURBS Generator Header
```
Files: cpp_core/geometry/nurbs_generator.h
Task: Define NURBSMoldGenerator interface
Estimated: 50K tokens, $3-5, 2-3 hours
```

**Agent 47**: NURBS Surface Fitting
```
Files: cpp_core/geometry/nurbs_generator.cpp (fit_nurbs)
Task: Sample limit surface and fit NURBS
Estimated: 120K tokens, $7-12, 6-7 hours
```

**Agent 48**: Draft Transformation
```
Files: cpp_core/geometry/nurbs_generator.cpp (apply_draft)
Task: Apply draft angle to NURBS surface
Estimated: 100K tokens, $6-10, 5-6 hours
```

**Agent 49**: Solid Brep Creation
```
Files: cpp_core/geometry/nurbs_generator.cpp (create_solid)
Task: Create mold solid with wall thickness
Estimated: 100K tokens, $6-10, 5-6 hours
```

**Agent 50**: NURBS Python Bindings
```
Files: cpp_core/python_bindings/py_bindings.cpp (nurbs)
Task: pybind11 bindings for mold generation
Estimated: 50K tokens, $3-5, 2-3 hours
```

**Agent 51**: NURBS Tests
```
Files: tests/test_nurbs.py
Task: Validate NURBS generation and quality
Estimated: 60K tokens, $2-4, 3-4 hours
```

**Afternoon Integration** (3pm-7pm):
- Build C++ with OpenCASCADE
- Test NURBS generation
- Verify draft angles applied correctly
- Check solid Brep validity

**Day 7 Totals**:
- **6 agents** launched
- **Cost**: $27-46
- **Deliverable**: NURBS mold generation working

---

### DAY 8: RHINO EXPORT + MOLD UI (6 agents in parallel)

**Morning Launch** (9am - Launch 6 agents):

**Agent 52**: NURBS Serialization
```
Files: ceramic_mold_analyzer/app/export/nurbs_serializer.py
Task: Serialize NURBS Brep to JSON/Rhino format
Estimated: 80K tokens, $5-8, 4-5 hours
```

**Agent 53**: Grasshopper POST Endpoint
```
Files: rhino/gh_subd_server.py (POST /molds)
Task: Receive and import NURBS molds in Rhino
Estimated: 60K tokens, $2-4, 3-4 hours
```

**Agent 54**: Mold Parameters Dialog
```
Files: ceramic_mold_analyzer/app/ui/mold_params_dialog.py
Task: UI for draft angle, wall thickness, etc.
Estimated: 60K tokens, $4-6, 3-4 hours
```

**Agent 55**: Mold Generation Workflow
```
Files: ceramic_mold_analyzer/app/workflow/mold_generator.py
Task: Orchestrate region→constraint→NURBS→export
Estimated: 80K tokens, $5-8, 4-5 hours
```

**Agent 56**: Progress Feedback UI
```
Files: ceramic_mold_analyzer/app/ui/progress_dialog.py
Task: Show mold generation progress
Estimated: 40K tokens, $2-4, 2-3 hours
```

**Agent 57**: Export Tests
```
Files: tests/test_export.py, tests/test_roundtrip.py
Task: Validate Rhino export and round-trip
Estimated: 60K tokens, $2-4, 3-4 hours
```

**Afternoon Integration** (2pm-6pm):
- Test complete workflow: Analyze → Edit → Generate → Export
- Verify molds import correctly in Rhino
- Check round-trip lossless

**Day 8 Totals**:
- **6 agents** launched
- **Cost**: $20-34
- **Deliverable**: ✅ **End-to-end mold pipeline working!**

**Days 6-8 Total**: $71-120 (Phase 1b: Constraints + Molds)

---

### DAY 9: TESTING + POLISH (6 agents in parallel)

**Morning Launch** (9am - Launch 6 agents):

**Agent 58**: C++ Unit Tests
```
Files: cpp_core/tests/ (Google Test framework)
Task: Comprehensive C++ unit tests
Estimated: 100K tokens, $6-10, 5-6 hours
```

**Agent 59**: Python Unit Tests
```
Files: tests/ (pytest framework)
Task: Comprehensive Python unit tests
Estimated: 100K tokens, $3-6, 5-6 hours
```

**Agent 60**: Integration Tests
```
Files: tests/integration/
Task: End-to-end workflow tests with multiple forms
Estimated: 80K tokens, $3-5, 4-5 hours
```

**Agent 61**: Performance Benchmarks
```
Files: tests/benchmarks/
Task: Profile and document performance
Estimated: 60K tokens, $2-4, 3-4 hours
```

**Agent 62**: UI Polish
```
Files: ceramic_mold_analyzer/app/ui/ (various)
Task: Fix UI issues, add tooltips, improve UX
Estimated: 80K tokens, $5-8, 4-5 hours
```

**Agent 63**: Error Handling
```
Files: ceramic_mold_analyzer/app/ (various)
Task: Add robust error handling throughout
Estimated: 70K tokens, $4-7, 4-5 hours
```

**Afternoon Testing** (2pm-8pm - You):
- Run full test suite
- Manual testing with diverse forms
- Fix any critical bugs
- Performance profiling

**Day 9 Totals**:
- **6 agents** launched
- **Cost**: $23-40
- **Deliverable**: Comprehensive test suite, polished UI

---

### DAY 10: DOCUMENTATION + FINAL TESTING (4 agents in parallel)

**Morning Launch** (9am - Launch 4 agents):

**Agent 64**: User Guide
```
Files: docs/USER_GUIDE.md
Task: Complete user documentation with screenshots
Estimated: 100K tokens, $3-6, 6-8 hours
```

**Agent 65**: Developer Documentation
```
Files: docs/DEVELOPER_GUIDE.md, docs/ARCHITECTURE.md
Task: Technical documentation for developers
Estimated: 100K tokens, $3-6, 6-8 hours
```

**Agent 66**: API Reference
```
Files: docs/API_REFERENCE.md
Task: Complete C++ and Python API docs
Estimated: 80K tokens, $2-4, 5-6 hours
```

**Agent 67**: Tutorial & Examples
```
Files: docs/TUTORIAL.md, examples/
Task: Step-by-step tutorial with example files
Estimated: 80K tokens, $2-4, 5-6 hours
```

**Afternoon** (2pm-6pm - You):
- Final integration testing
- Create demo video
- Package release
- Write release notes

**Evening** (6pm-8pm):
- Final review
- Commit final version
- Deploy (if applicable)

**Day 10 Totals**:
- **4 agents** launched
- **Cost**: $10-20
- **Deliverable**: ✅ **COMPLETE MVP WITH DOCUMENTATION!**

**Days 9-10 Total**: $33-60 (Testing + Polish + Docs)

---

## 10-Day Sprint Summary

### Timeline Breakdown

| Days | Phase | Agents | Cost | Deliverables |
|------|-------|--------|------|--------------|
| **1-2** | Phase 0: C++ Core | 17 agents | $56-93 | SubD eval, tessellation, limit surface, VTK |
| **3-5** | Phase 1a: UI + Analysis | 22 agents | $82-139 | Edit modes, regions, curvature, spectral |
| **6-8** | Phase 1b: Constraints + Molds | 18 agents | $71-120 | Validation, NURBS, export |
| **9-10** | Testing + Polish | 10 agents | $33-60 | Tests, docs, polish |
| **TOTAL** | **10 days** | **67 agents** | **$242-412** | **Production MVP** |

### Budget Analysis

**Total Estimated Cost**: $242-412
- **Well under $1000 budget!**
- **Reserve**: $588-758 for:
  - Debugging (budget $100-150)
  - Iteration on failed agents ($50-100)
  - Additional features ($200-300)
  - Phase 2 advanced work ($238-308)

### Key Metrics

**Velocity**:
- **10 days** vs 16 weeks solo (11x faster!)
- **67 agents** working in parallel
- **Effective**: ~400-500 agent-hours compressed into 10 days

**Your Time Commitment**:
- **8-12 hours per day** for 10 days
- **Primary tasks**: Review, integrate, test, launch next batch
- **80-120 total hours** orchestrating agents

**Success Rate Assumptions**:
- 80% of agents succeed first time
- 20% need iteration/fixes (cost: +$40-80)
- Total adjusted cost: $280-490

---

## Daily Schedule Template

### Morning (9am-12pm)
```
9:00-9:30   Review overnight agent outputs (if any)
9:30-10:00  Launch morning agent batch (6-8 agents)
10:00-12:00 Review completed agents, test, integrate
```

### Afternoon (12pm-6pm)
```
12:00-1:00  Lunch break
1:00-3:00   Continue integration work
3:00-4:00   Launch afternoon/evening batch (2-4 agents)
4:00-6:00   Test integrated system, fix issues
```

### Evening (6pm-9pm)
```
6:00-8:00   Review evening agent outputs
8:00-9:00   Final testing, prepare for next day
```

**Weekend work**: Days 6-7 (Sat-Sun) - same schedule

---

## Risk Mitigation

### If Behind Schedule

**After Day 2** (should have Phase 0 complete):
- If not complete: Add 1 extra day, shift all subsequent days +1
- Budget impact: +$30-50

**After Day 5** (should have analysis working):
- If not complete: Skip spectral lens, focus on differential only
- Budget savings: -$15-25

**After Day 8** (should have molds working):
- If not complete: Simplify NURBS generation (skip draft angle initially)
- Budget savings: -$20-40

### If Over Budget

**Contingency plan** (if approaching $600 spent):
1. Switch remaining agents to Haiku (50% cost reduction)
2. Handle simpler tasks yourself (docs, simple UI)
3. Reduce parallelism (4 agents instead of 6-8)
4. Focus on core functionality only

### Agent Failure Handling

**If an agent produces broken code**:
- **Immediate fix**: Launch repair agent with error logs ($3-8, 1-2 hours)
- **Escalate**: If repair fails, you fix manually
- **Budget**: Reserve $100-150 for agent failures

---

## Success Criteria

### Phase 0 (Days 1-2)
- [ ] ✅ OpenSubdiv integration compiles
- [ ] ✅ Python bindings work
- [ ] ✅ Rhino→Desktop control cage transfer
- [ ] ✅ Tessellation generates valid triangles
- [ ] ✅ Exact limit evaluation: error <1e-6
- [ ] ✅ VTK displays smooth SubD

### Phase 1a (Days 3-5)
- [ ] ✅ All edit modes (S/P/E/V) functional
- [ ] ✅ Region creation and visualization
- [ ] ✅ Curvature analysis accurate
- [ ] ✅ Differential lens discovers regions
- [ ] ✅ Spectral lens working

### Phase 1b (Days 6-8)
- [ ] ✅ Undercut detection functional
- [ ] ✅ Draft angle validation working
- [ ] ✅ NURBS mold generation successful
- [ ] ✅ Export to Rhino lossless

### Final (Days 9-10)
- [ ] ✅ Test coverage >70%
- [ ] ✅ All performance benchmarks met
- [ ] ✅ Complete documentation
- [ ] ✅ Zero critical bugs

---

## Orchestration Best Practices

### Launching Agents in Parallel

**Use single message with multiple Task tool calls**:
```markdown
I need to launch 6 agents in parallel for Day 3 morning:

Agent 18: [Edit Mode Manager task description...]
Agent 19: [Face Picker task description...]
Agent 20: [Edge Picker task description...]
Agent 21: [Vertex Picker task description...]
Agent 22: [Edit Mode Toolbar task description...]
Agent 23: [Parametric Region task description...]

Run all agents in parallel.
```

### Integration Protocol

**For each completed agent**:
1. ✅ Review code quality
2. ✅ Check against specification
3. ✅ Run provided tests
4. ✅ Integrate into main codebase
5. ✅ Test integration points
6. ✅ Commit to repository
7. ✅ Update progress tracker

### Communication Between Agents

**Prevent conflicts** via:
- Clear file ownership (no overlapping files)
- Well-defined interfaces
- No shared state during development
- Integration happens after all agents complete

---

## Recommendation

**This is an aggressive but achievable plan.**

### Prerequisites for Success

✅ **You must commit** to 8-12 hour days for 10 days
✅ **Pre-sprint prep** is critical (Day 0 setup)
✅ **Quick integration** is essential (test within 2 hours of agent completion)
✅ **Flexibility** if some agents take longer than expected

### Expected Outcome

**Day 10 Evening**: You will have a **production-ready MVP** of Latent:
- Complete C++ core with OpenSubdiv + OpenCASCADE
- Professional PyQt6 UI
- 2+ mathematical lenses
- Constraint validation
- NURBS mold generation
- Rhino export
- Comprehensive tests
- Full documentation

**Total cost**: $280-490 (with contingency for failures)
**Remaining budget**: $510-720 for Phase 2 features

---

## Ready to Start?

**Tomorrow is Day 0 (Preparation)**:
- Install all dependencies (3-4 hours)
- Set up project structure
- Verify everything builds

**Day 1 starts with launching 6 agents in parallel!**

Should we begin? I can help you with Day 0 setup checklist right now.

---

*Document Version: 1.0 - 10-Day Sprint*
*Created: November 2025*
*Based on: Implementation Roadmap v3.0*
