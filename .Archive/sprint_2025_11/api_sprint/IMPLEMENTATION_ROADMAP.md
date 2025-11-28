# Ceramic Mold Analyzer - Implementation Roadmap
## Revised Plan: Hybrid C++/Python Architecture (v5.0)

**Start Date**: November 2025
**Target MVP**: Phase 0 (3 weeks) + Phase 1 (3 months) = ~4 months to functional MVP
**Architecture**: Hybrid C++/Python from start (not optional - required for lossless architecture)

---

## Critical Architectural Decision

**rhino3dm does NOT support SubD serialization** - this invalidates the pure Python approach entirely.

The v5.0 specification explicitly requires:
- **OpenSubdiv** (C++) for exact SubD limit surface evaluation
- **OpenCASCADE** (C++) for NURBS operations
- **pybind11** for Python-C++ bindings
- **Mathematical operations on exact limit surfaces, display via tessellation**

**This is not an optimization - it's a fundamental requirement for the lossless architecture.**

---

## Architecture Overview

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

**Data Flow (Lossless):**
```
Rhino/Grasshopper:
  SubD control cage → JSON (vertices, faces, topology)
    ↓ HTTP
Desktop Python:
  Parse JSON → Pass to C++ module
    ↓ pybind11
C++ OpenSubdiv:
  Build TopologyRefiner → Exact limit surface evaluation
  Tessellate for display → Return numpy arrays
    ↓ pybind11
Python VTK:
  Render tessellated mesh
  All analysis queries exact limit surface via C++
```

---

# PHASE 0: C++ CORE FOUNDATION (3 weeks)

**Goal**: Prove OpenSubdiv integration and establish build system

**Phase Success Criteria**:
- [ ] C++ module builds and loads in Python
- [ ] OpenSubdiv tessellates control cage to triangle mesh
- [ ] Exact limit surface evaluation achieves <1e-6 error vs Rhino
- [ ] Control cage transfers from Grasshopper via HTTP
- [ ] VTK displays tessellated geometry from C++

---

## Week 0.1: Build System & OpenSubdiv Integration

### Day 1: Environment Setup

**Tasks**:
- [ ] Install Xcode Command Line Tools
  ```bash
  xcode-select --install
  ```
- [ ] Verify Homebrew installation
  ```bash
  brew --version
  ```
- [ ] Install CMake
  ```bash
  brew install cmake
  cmake --version  # Should be 3.20+
  ```
- [ ] Install pybind11
  ```bash
  brew install pybind11
  ```
- [ ] Install Threading Building Blocks (TBB)
  ```bash
  brew install tbb
  ```

**Tests**:
```bash
# Test CMake
cmake --version

# Test pybind11
python3 -c "import pybind11; print(pybind11.get_include())"

# Test TBB
pkg-config --modversion tbb
```

**Success Metrics**:
- ✅ All dependencies install without errors
- ✅ CMake version ≥ 3.20
- ✅ pybind11 importable in Python 3.11+
- ✅ TBB version ≥ 2021

**Deliverable**: Development environment ready for C++ compilation

---

### Day 2: OpenSubdiv Installation

**Tasks**:
- [ ] Download OpenSubdiv source
  ```bash
  cd ~/Downloads
  git clone https://github.com/PixarAnimationStudios/OpenSubdiv.git
  cd OpenSubdiv
  git checkout v3_6_0  # Use stable release
  ```
- [ ] Build OpenSubdiv with Metal backend
  ```bash
  mkdir build && cd build
  cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DNO_EXAMPLES=ON \
    -DNO_TUTORIALS=ON \
    -DNO_REGRESSION=ON \
    -DNO_DOC=ON \
    -DNO_TESTS=ON \
    -DOSD_ENABLE_METAL=ON

  make -j$(sysctl -n hw.ncpu)
  sudo make install
  ```
- [ ] Verify installation
  ```bash
  pkg-config --modversion opensubdiv
  pkg-config --cflags opensubdiv
  pkg-config --libs opensubdiv
  ```

**Tests**:
```bash
# Check header files installed
ls /usr/local/include/opensubdiv/

# Check libraries installed
ls /usr/local/lib/libosd*

# Test pkg-config
pkg-config --modversion opensubdiv  # Should show 3.6.0
```

**Success Metrics**:
- ✅ OpenSubdiv builds without errors (30-60 minutes)
- ✅ Metal backend enabled (check build output for "Metal support: ON")
- ✅ Headers installed in `/usr/local/include/opensubdiv/`
- ✅ Libraries installed in `/usr/local/lib/`
- ✅ pkg-config finds OpenSubdiv

**Deliverable**: OpenSubdiv 3.6+ installed with Metal support

**Troubleshooting**:
- If Metal not detected: Install Xcode (full version, not just CLI tools)
- If TBB errors: `export TBB_ROOT=$(brew --prefix tbb)`
- If build fails: Check `build/CMakeCache.txt` for configuration issues

---

### Day 3: Project Structure & CMake Setup

**Tasks**:
- [ ] Create C++ module directory structure
  ```bash
  cd /path/to/Latent
  mkdir -p cpp_core/{geometry,analysis,constraints,python_bindings,utils}
  ```
- [ ] Create `cpp_core/geometry/types.h`:
  ```cpp
  #pragma once
  #include <vector>
  #include <array>
  #include <cstdint>

  namespace latent {

  struct Point3D {
      float x, y, z;
      Point3D() : x(0), y(0), z(0) {}
      Point3D(float _x, float _y, float _z) : x(_x), y(_y), z(_z) {}
  };

  struct SubDControlCage {
      std::vector<Point3D> vertices;
      std::vector<std::vector<int>> faces;  // Quad/n-gon faces
      std::vector<std::pair<int, float>> creases;  // Edge ID, sharpness

      size_t vertex_count() const { return vertices.size(); }
      size_t face_count() const { return faces.size(); }
  };

  struct TessellationResult {
      std::vector<float> vertices;      // Flattened [x,y,z, x,y,z, ...]
      std::vector<float> normals;       // Flattened normals
      std::vector<int> triangles;       // Flattened triangle indices [i,j,k, ...]
      std::vector<int> face_parents;    // Which SubD face each tri came from

      size_t vertex_count() const { return vertices.size() / 3; }
      size_t triangle_count() const { return triangles.size() / 3; }
  };

  }  // namespace latent
  ```

- [ ] Create `cpp_core/CMakeLists.txt`:
  ```cmake
  cmake_minimum_required(VERSION 3.20)
  project(latent_cpp_core VERSION 0.5.0 LANGUAGES CXX)

  set(CMAKE_CXX_STANDARD 17)
  set(CMAKE_CXX_STANDARD_REQUIRED ON)
  set(CMAKE_CXX_EXTENSIONS OFF)

  # Build type defaults to Release
  if(NOT CMAKE_BUILD_TYPE)
      set(CMAKE_BUILD_TYPE Release)
  endif()

  # Find dependencies
  find_package(OpenSubdiv REQUIRED)
  find_package(pybind11 REQUIRED)

  # Core library (static)
  add_library(latent_core STATIC
      geometry/subd_evaluator.cpp
      utils/mesh_mapping.cpp
  )

  target_include_directories(latent_core PUBLIC
      ${CMAKE_CURRENT_SOURCE_DIR}
      ${OPENSUBDIV_INCLUDE_DIR}
  )

  target_link_libraries(latent_core PUBLIC
      ${OPENSUBDIV_LIBRARIES}
  )

  # Enable Metal on macOS
  if(APPLE)
      target_compile_definitions(latent_core PUBLIC OPENSUBDIV_HAS_METAL)
  endif()

  # Python bindings (shared library)
  pybind11_add_module(cpp_core python_bindings/py_bindings.cpp)
  target_link_libraries(cpp_core PRIVATE latent_core)

  # Installation
  install(TARGETS cpp_core LIBRARY DESTINATION .)
  ```

- [ ] Create initial `cpp_core/geometry/subd_evaluator.h`:
  ```cpp
  #pragma once
  #include "types.h"
  #include <opensubdiv/far/topologyRefiner.h>
  #include <memory>

  namespace latent {

  class SubDEvaluator {
  private:
      std::unique_ptr<OpenSubdiv::Far::TopologyRefiner> refiner_;
      std::vector<int> triangle_to_face_map_;
      bool initialized_;

  public:
      SubDEvaluator();
      ~SubDEvaluator();

      // Build from control cage
      void initialize(const SubDControlCage& cage);

      // Check if initialized
      bool is_initialized() const { return initialized_; }

      // Tessellate for display
      TessellationResult tessellate(int subdivision_level = 3,
                                     bool adaptive = false);

      // Exact limit surface evaluation
      Point3D evaluate_limit_point(int face_index, float u, float v) const;

      // Evaluate with normal
      void evaluate_limit(int face_index, float u, float v,
                         Point3D& point, Point3D& normal) const;

      // Get parent face for tessellated triangle
      int get_parent_face(int triangle_index) const;

      // Get statistics
      size_t get_control_vertex_count() const;
      size_t get_control_face_count() const;
  };

  }  // namespace latent
  ```

**Tests**:
```bash
# Test CMake configuration (don't build yet)
cd cpp_core
mkdir build && cd build
cmake ..

# Should see output:
# -- Found OpenSubdiv: ...
# -- Found pybind11: ...
# -- Configuring done
# -- Generating done
```

**Success Metrics**:
- ✅ Directory structure created correctly
- ✅ CMake configures without errors
- ✅ OpenSubdiv found by CMake
- ✅ pybind11 found by CMake
- ✅ No compiler errors (not building yet, just configuring)

**Deliverable**: Project structure and build system configured

---

### Day 4: Minimal SubDEvaluator Implementation

**Tasks**:
- [ ] Implement `cpp_core/geometry/subd_evaluator.cpp` (minimal version)
  ```cpp
  #include "subd_evaluator.h"
  #include <opensubdiv/far/topologyDescriptor.h>
  #include <opensubdiv/far/primvarRefiner.h>
  #include <stdexcept>
  #include <iostream>

  using namespace OpenSubdiv;

  namespace latent {

  SubDEvaluator::SubDEvaluator() : initialized_(false) {}

  SubDEvaluator::~SubDEvaluator() {}

  void SubDEvaluator::initialize(const SubDControlCage& cage) {
      if (cage.vertex_count() == 0 || cage.face_count() == 0) {
          throw std::invalid_argument("Empty control cage");
      }

      // Build OpenSubdiv topology descriptor
      typedef Far::TopologyDescriptor Descriptor;

      Descriptor desc;
      desc.numVertices = cage.vertex_count();
      desc.numFaces = cage.face_count();

      // Build face vertex indices
      std::vector<int> numVertsPerFace;
      std::vector<int> vertIndices;

      for (const auto& face : cage.faces) {
          numVertsPerFace.push_back(face.size());
          for (int idx : face) {
              vertIndices.push_back(idx);
          }
      }

      desc.numVertsPerFace = numVertsPerFace.data();
      desc.vertIndicesPerFace = vertIndices.data();

      // Create topology refiner
      typedef Far::TopologyRefinerFactory<Descriptor> Factory;

      Sdc::SchemeType type = Sdc::SCHEME_CATMULL_CLARK;
      Sdc::Options options;
      options.SetVtxBoundaryInterpolation(Sdc::Options::VTX_BOUNDARY_EDGE_ONLY);

      refiner_.reset(Factory::Create(desc,
          Factory::Options(type, options)));

      if (!refiner_) {
          throw std::runtime_error("Failed to create topology refiner");
      }

      // Apply edge creases if any
      if (!cage.creases.empty()) {
          // TODO: Apply creases to refiner
      }

      initialized_ = true;

      std::cout << "SubDEvaluator initialized: "
                << cage.vertex_count() << " vertices, "
                << cage.face_count() << " faces" << std::endl;
  }

  TessellationResult SubDEvaluator::tessellate(int subdivision_level, bool adaptive) {
      if (!initialized_) {
          throw std::runtime_error("SubDEvaluator not initialized");
      }

      TessellationResult result;

      // Refine topology
      if (adaptive) {
          // TODO: Implement adaptive refinement
          throw std::runtime_error("Adaptive refinement not yet implemented");
      } else {
          refiner_->RefineUniform(Far::TopologyRefiner::UniformOptions(subdivision_level));
      }

      // TODO: Extract tessellated geometry
      // For now, return empty result
      std::cout << "Tessellation requested at level " << subdivision_level << std::endl;

      return result;
  }

  Point3D SubDEvaluator::evaluate_limit_point(int face_index, float u, float v) const {
      if (!initialized_) {
          throw std::runtime_error("SubDEvaluator not initialized");
      }

      // TODO: Implement exact limit surface evaluation using Stam's method
      return Point3D(0, 0, 0);
  }

  void SubDEvaluator::evaluate_limit(int face_index, float u, float v,
                                    Point3D& point, Point3D& normal) const {
      if (!initialized_) {
          throw std::runtime_error("SubDEvaluator not initialized");
      }

      // TODO: Implement
      point = Point3D(0, 0, 0);
      normal = Point3D(0, 0, 1);
  }

  int SubDEvaluator::get_parent_face(int triangle_index) const {
      if (triangle_index < 0 || triangle_index >= triangle_to_face_map_.size()) {
          return -1;
      }
      return triangle_to_face_map_[triangle_index];
  }

  size_t SubDEvaluator::get_control_vertex_count() const {
      if (!refiner_) return 0;
      return refiner_->GetNumVertices(0);  // Level 0 = control cage
  }

  size_t SubDEvaluator::get_control_face_count() const {
      if (!refiner_) return 0;
      return refiner_->GetNumFaces(0);
  }

  }  // namespace latent
  ```

- [ ] Create placeholder `cpp_core/utils/mesh_mapping.cpp`:
  ```cpp
  #include "mesh_mapping.h"

  namespace latent {
  // Placeholder for future mesh mapping utilities
  }
  ```

- [ ] Create placeholder `cpp_core/utils/mesh_mapping.h`:
  ```cpp
  #pragma once

  namespace latent {
  // Future: Triangle→Face mapping utilities
  }
  ```

**Tests**:
```bash
# Build C++ module
cd cpp_core/build
cmake ..
make -j$(sysctl -n hw.ncpu)

# Should see:
# [ 50%] Building CXX object CMakeFiles/latent_core.a
# [100%] Linking CXX static library liblatent_core.a
```

**Success Metrics**:
- ✅ C++ code compiles without errors
- ✅ Static library `liblatent_core.a` created
- ✅ No linker errors
- ✅ OpenSubdiv headers found and included
- ✅ Build completes in <5 minutes

**Deliverable**: Minimal C++ SubDEvaluator that compiles and links

---

### Day 5: pybind11 Bindings

**Tasks**:
- [ ] Implement `cpp_core/python_bindings/py_bindings.cpp`:
  ```cpp
  #include <pybind11/pybind11.h>
  #include <pybind11/stl.h>
  #include <pybind11/numpy.h>
  #include "../geometry/subd_evaluator.h"

  namespace py = pybind11;
  using namespace latent;

  PYBIND11_MODULE(cpp_core, m) {
      m.doc() = "Latent C++ core for exact SubD evaluation via OpenSubdiv";

      // Point3D binding
      py::class_<Point3D>(m, "Point3D")
          .def(py::init<>())
          .def(py::init<float, float, float>())
          .def_readwrite("x", &Point3D::x)
          .def_readwrite("y", &Point3D::y)
          .def_readwrite("z", &Point3D::z)
          .def("__repr__", [](const Point3D& p) {
              return "Point3D(" + std::to_string(p.x) + ", " +
                     std::to_string(p.y) + ", " + std::to_string(p.z) + ")";
          });

      // SubDControlCage binding
      py::class_<SubDControlCage>(m, "SubDControlCage")
          .def(py::init<>())
          .def_readwrite("vertices", &SubDControlCage::vertices)
          .def_readwrite("faces", &SubDControlCage::faces)
          .def_readwrite("creases", &SubDControlCage::creases)
          .def("vertex_count", &SubDControlCage::vertex_count)
          .def("face_count", &SubDControlCage::face_count);

      // TessellationResult binding
      py::class_<TessellationResult>(m, "TessellationResult")
          .def(py::init<>())
          .def_readonly("vertices", &TessellationResult::vertices)
          .def_readonly("normals", &TessellationResult::normals)
          .def_readonly("triangles", &TessellationResult::triangles)
          .def_readonly("face_parents", &TessellationResult::face_parents)
          .def("vertex_count", &TessellationResult::vertex_count)
          .def("triangle_count", &TessellationResult::triangle_count);

      // SubDEvaluator binding
      py::class_<SubDEvaluator>(m, "SubDEvaluator")
          .def(py::init<>())
          .def("initialize", &SubDEvaluator::initialize,
               py::arg("cage"),
               "Initialize evaluator with control cage")
          .def("is_initialized", &SubDEvaluator::is_initialized)
          .def("tessellate", &SubDEvaluator::tessellate,
               py::arg("subdivision_level") = 3,
               py::arg("adaptive") = false,
               "Tessellate SubD surface for display")
          .def("evaluate_limit_point", &SubDEvaluator::evaluate_limit_point,
               py::arg("face_index"),
               py::arg("u"),
               py::arg("v"),
               "Evaluate exact point on limit surface")
          .def("get_parent_face", &SubDEvaluator::get_parent_face,
               py::arg("triangle_index"))
          .def("get_control_vertex_count", &SubDEvaluator::get_control_vertex_count)
          .def("get_control_face_count", &SubDEvaluator::get_control_face_count);

      // Version info
      m.attr("__version__") = "0.5.0";
      m.attr("opensubdiv_version") = "3.6.0";
  }
  ```

- [ ] Build Python module:
  ```bash
  cd cpp_core/build
  cmake ..
  make -j$(sysctl -n hw.ncpu)
  ```

- [ ] Create test script `cpp_core/test_bindings.py`:
  ```python
  #!/usr/bin/env python3
  """Test C++ bindings"""
  import sys
  sys.path.insert(0, 'build')

  import cpp_core

  print(f"cpp_core version: {cpp_core.__version__}")
  print(f"OpenSubdiv version: {cpp_core.opensubdiv_version}")

  # Test Point3D
  p = cpp_core.Point3D(1.0, 2.0, 3.0)
  print(f"\nPoint3D: {p}")
  assert p.x == 1.0
  assert p.y == 2.0
  assert p.z == 3.0

  # Test SubDControlCage
  cage = cpp_core.SubDControlCage()
  cage.vertices = [
      cpp_core.Point3D(0, 0, 0),
      cpp_core.Point3D(1, 0, 0),
      cpp_core.Point3D(1, 1, 0),
      cpp_core.Point3D(0, 1, 0),
      cpp_core.Point3D(0.5, 0.5, 1)
  ]
  cage.faces = [
      [0, 1, 2, 3],  # Bottom quad
      [0, 1, 4],     # Triangular faces of pyramid
      [1, 2, 4],
      [2, 3, 4],
      [3, 0, 4]
  ]

  print(f"\nControl cage: {cage.vertex_count()} vertices, {cage.face_count()} faces")

  # Test SubDEvaluator
  evaluator = cpp_core.SubDEvaluator()
  print(f"Evaluator initialized: {evaluator.is_initialized()}")

  evaluator.initialize(cage)
  print(f"Evaluator initialized: {evaluator.is_initialized()}")
  print(f"Control vertices: {evaluator.get_control_vertex_count()}")
  print(f"Control faces: {evaluator.get_control_face_count()}")

  # Test tessellation (will be empty for now)
  result = evaluator.tessellate(subdivision_level=2)
  print(f"\nTessellation result:")
  print(f"  Vertices: {result.vertex_count()}")
  print(f"  Triangles: {result.triangle_count()}")

  print("\n✅ All binding tests passed!")
  ```

**Tests**:
```bash
cd cpp_core
python3 test_bindings.py
```

**Success Metrics**:
- ✅ Python module `cpp_core.so` builds successfully
- ✅ Module imports without errors in Python
- ✅ All classes (Point3D, SubDControlCage, SubDEvaluator) accessible
- ✅ SubDEvaluator initializes with test control cage
- ✅ Test script runs without crashes
- ✅ Topology refiner created successfully

**Deliverable**: Python bindings working, can initialize SubDEvaluator from Python

**Milestone 0.1 Complete**: Build system operational, OpenSubdiv integrated, Python bindings functional

---

## Week 0.2: Rhino Communication & Tessellation

### Day 6-7: Grasshopper Control Cage Server

**Tasks**:
- [ ] Create `rhino/gh_subd_server.py`:
  ```python
  """
  Grasshopper Python 3 component for SubD control cage HTTP server

  Inputs:
    - SubD: SubD geometry from Rhino
    - Port: Server port (default 8888)
    - Run: Boolean to start/stop server

  Outputs:
    - Status: Server status message
  """
  import Rhino.Geometry as rg
  import json
  import http.server
  import socketserver
  import threading

  class SubDHandler(http.server.BaseHTTPRequestHandler):
      subd_geometry = None  # Class variable to share SubD

      def log_message(self, format, *args):
          # Suppress default logging
          pass

      def do_GET(self):
          if self.path == '/subd':
              if SubDHandler.subd_geometry is None:
                  self.send_error(404, "No SubD geometry available")
                  return

              try:
                  # Extract control cage
                  subd = SubDHandler.subd_geometry

                  # Get control vertices
                  control_vertices = []
                  for i in range(subd.Vertices.Count):
                      v = subd.Vertices[i].ControlNetPoint
                      control_vertices.append([v.X, v.Y, v.Z])

                  # Get control faces
                  control_faces = []
                  for i in range(subd.Faces.Count):
                      face = subd.Faces[i]
                      edge_count = face.EdgeCount
                      indices = []
                      for j in range(edge_count):
                          edge = face.GetEdge(j)
                          indices.append(edge.StartVertex.Id)
                      control_faces.append(indices)

                  # Get edge creases
                  creases = []
                  for i in range(subd.Edges.Count):
                      edge = subd.Edges[i]
                      if edge.Sharpness > 0:
                          creases.append([i, float(edge.Sharpness)])

                  # Build response
                  response = {
                      "geometry_type": "SubDControlCage",
                      "vertices": control_vertices,
                      "faces": control_faces,
                      "creases": creases,
                      "metadata": {
                          "vertex_count": len(control_vertices),
                          "face_count": len(control_faces),
                          "scheme": "catmull-clark",
                          "boundary_type": "edge_only"
                      }
                  }

                  # Send response
                  self.send_response(200)
                  self.send_header('Content-type', 'application/json')
                  self.send_header('Access-Control-Allow-Origin', '*')
                  self.end_headers()
                  self.wfile.write(json.dumps(response).encode('utf-8'))

              except Exception as e:
                  self.send_error(500, f"Error extracting SubD: {str(e)}")

          elif self.path == '/status':
              self.send_response(200)
              self.send_header('Content-type', 'application/json')
              self.end_headers()
              status = {
                  "status": "running",
                  "has_geometry": SubDHandler.subd_geometry is not None
              }
              self.wfile.write(json.dumps(status).encode('utf-8'))

          else:
              self.send_error(404, "Endpoint not found")

  # Server management
  server = None
  server_thread = None

  def start_server(port):
      global server, server_thread

      if server is not None:
          return "Server already running"

      try:
          server = socketserver.TCPServer(('localhost', port), SubDHandler)
          server_thread = threading.Thread(target=server.serve_forever)
          server_thread.daemon = True
          server_thread.start()
          return f"Server started on port {port}"
      except Exception as e:
          return f"Error starting server: {str(e)}"

  def stop_server():
      global server, server_thread

      if server is None:
          return "Server not running"

      try:
          server.shutdown()
          server = None
          server_thread = None
          return "Server stopped"
      except Exception as e:
          return f"Error stopping server: {str(e)}"

  # Main logic
  if Run:
      SubDHandler.subd_geometry = SubD
      Status = start_server(Port if Port else 8888)
  else:
      SubDHandler.subd_geometry = None
      Status = stop_server()
  ```

- [ ] Create test SubD in Rhino (simple sphere or box)
- [ ] Create Grasshopper definition with server component
- [ ] Test server startup and `/status` endpoint

**Tests**:
```bash
# Test server from command line
curl http://localhost:8888/status

# Should return:
# {"status": "running", "has_geometry": true}

# Test SubD endpoint
curl http://localhost:8888/subd | python3 -m json.tool

# Should return valid JSON with vertices, faces, creases
```

**Success Metrics**:
- ✅ Server starts without errors in Grasshopper
- ✅ `/status` endpoint returns valid JSON
- ✅ `/subd` endpoint returns control cage data
- ✅ Control vertices match Rhino geometry
- ✅ Face topology preserved correctly
- ✅ Edge creases included if present

**Deliverable**: Grasshopper server extracts and serves SubD control cage via HTTP

---

### Day 8: Desktop Client Integration

**Tasks**:
- [ ] Update `ceramic_mold_analyzer/app/bridge/rhino_bridge.py`:
  ```python
  """
  Rhino HTTP bridge for SubD control cage transfer
  """
  import requests
  import sys
  from typing import Optional, Dict, Any

  # Import C++ module
  sys.path.insert(0, '../../cpp_core/build')
  import cpp_core

  class RhinoBridge:
      """HTTP client for fetching SubD control cage from Grasshopper"""

      def __init__(self, host='localhost', port=8888):
          self.host = host
          self.port = port
          self.base_url = f"http://{host}:{port}"
          self.evaluator = None
          self._last_hash = None

      def is_connected(self) -> bool:
          """Check if Grasshopper server is running"""
          try:
              response = requests.get(f"{self.base_url}/status", timeout=1.0)
              if response.status_code == 200:
                  data = response.json()
                  return data.get('status') == 'running'
          except:
              pass
          return False

      def has_geometry(self) -> bool:
          """Check if server has SubD geometry loaded"""
          try:
              response = requests.get(f"{self.base_url}/status", timeout=1.0)
              if response.status_code == 200:
                  data = response.json()
                  return data.get('has_geometry', False)
          except:
              pass
          return False

      def fetch_subd(self) -> Optional[cpp_core.SubDEvaluator]:
          """
          Fetch SubD control cage from Rhino and initialize C++ evaluator

          Returns:
              SubDEvaluator if successful, None otherwise
          """
          try:
              response = requests.get(f"{self.base_url}/subd", timeout=5.0)

              if response.status_code != 200:
                  print(f"Error fetching SubD: HTTP {response.status_code}")
                  return None

              data = response.json()

              # Check if geometry changed
              import hashlib
              data_hash = hashlib.md5(
                  str(data['vertices']).encode() +
                  str(data['faces']).encode()
              ).hexdigest()

              if data_hash == self._last_hash:
                  # No change, return existing evaluator
                  return self.evaluator

              self._last_hash = data_hash

              # Build C++ control cage
              cage = cpp_core.SubDControlCage()

              # Convert vertices
              for v in data['vertices']:
                  cage.vertices.append(cpp_core.Point3D(v[0], v[1], v[2]))

              # Convert faces
              cage.faces = data['faces']

              # Convert creases
              for crease in data.get('creases', []):
                  cage.creases.append((crease[0], crease[1]))

              # Initialize C++ evaluator
              evaluator = cpp_core.SubDEvaluator()
              evaluator.initialize(cage)

              self.evaluator = evaluator

              print(f"✅ SubD loaded: {cage.vertex_count()} vertices, "
                    f"{cage.face_count()} faces")

              return evaluator

          except requests.exceptions.RequestException as e:
              print(f"Network error: {e}")
              return None
          except Exception as e:
              print(f"Error processing SubD: {e}")
              import traceback
              traceback.print_exc()
              return None

      def get_display_mesh(self, subdivision_level=3) -> Optional[Dict[str, Any]]:
          """
          Get tessellated mesh for VTK display

          Returns:
              Dict with 'vertices', 'normals', 'triangles', 'face_map'
          """
          if self.evaluator is None:
              return None

          try:
              result = self.evaluator.tessellate(subdivision_level)

              return {
                  'vertices': result.vertices,
                  'normals': result.normals,
                  'triangles': result.triangles,
                  'face_map': result.face_parents,
                  'subdivision_level': subdivision_level
              }
          except Exception as e:
              print(f"Error tessellating: {e}")
              return None
  ```

- [ ] Create test script `test_bridge.py`:
  ```python
  #!/usr/bin/env python3
  """Test Rhino bridge"""
  import sys
  sys.path.insert(0, 'ceramic_mold_analyzer')

  from app.bridge.rhino_bridge import RhinoBridge

  print("Testing Rhino bridge...")

  bridge = RhinoBridge()

  # Test connection
  print(f"Connected: {bridge.is_connected()}")
  print(f"Has geometry: {bridge.has_geometry()}")

  # Fetch SubD
  evaluator = bridge.fetch_subd()

  if evaluator:
      print(f"✅ SubD fetched successfully")
      print(f"   Control vertices: {evaluator.get_control_vertex_count()}")
      print(f"   Control faces: {evaluator.get_control_face_count()}")

      # Test display mesh generation
      mesh = bridge.get_display_mesh(subdivision_level=2)
      if mesh:
          print(f"✅ Display mesh generated")
          print(f"   Vertices: {len(mesh['vertices']) // 3}")
          print(f"   Triangles: {len(mesh['triangles']) // 3}")
  else:
      print("❌ Failed to fetch SubD")
  ```

**Tests**:
```bash
# Start Grasshopper server first!
# Then run:
python3 test_bridge.py
```

**Success Metrics**:
- ✅ Bridge connects to Grasshopper server
- ✅ Control cage transfers successfully
- ✅ C++ evaluator initializes from transferred data
- ✅ Vertex/face counts match Rhino geometry
- ✅ Hash detection prevents duplicate transfers
- ✅ No memory leaks (test multiple fetches)

**Deliverable**: Desktop app can fetch SubD control cage from Rhino and initialize C++ evaluator

---

### Day 9-10: Complete Tessellation Implementation

**Tasks**:
- [ ] Implement full tessellation in `subd_evaluator.cpp`:
  ```cpp
  TessellationResult SubDEvaluator::tessellate(int subdivision_level, bool adaptive) {
      if (!initialized_) {
          throw std::runtime_error("SubDEvaluator not initialized");
      }

      TessellationResult result;

      // Refine topology uniformly
      refiner_->RefineUniform(Far::TopologyRefiner::UniformOptions(subdivision_level));

      // Get refined level
      int level = subdivision_level;
      int num_verts = refiner_->GetNumVertices(level);
      int num_faces = refiner_->GetNumFaces(level);

      // Allocate vertex data
      std::vector<float> vertex_positions(num_verts * 3);

      // Get vertex positions at refined level
      // This requires interpolating from base level
      Far::PrimvarRefiner primvarRefiner(*refiner_);

      // Start with base level positions
      std::vector<float> base_positions(refiner_->GetNumVertices(0) * 3);

      // TODO: Copy control cage positions to base_positions

      // Interpolate through levels
      for (int lvl = 1; lvl <= level; ++lvl) {
          int src_size = refiner_->GetNumVertices(lvl - 1);
          int dst_size = refiner_->GetNumVertices(lvl);

          std::vector<float> src_data(src_size * 3);
          std::vector<float> dst_data(dst_size * 3);

          // Copy previous level
          if (lvl == 1) {
              src_data = base_positions;
          } else {
              src_data = vertex_positions;
          }

          // Interpolate
          primvarRefiner.Interpolate(lvl, src_data.data(), dst_data.data());

          if (lvl == level) {
              vertex_positions = dst_data;
          }
      }

      // Extract triangles from quads
      triangle_to_face_map_.clear();

      for (int face_id = 0; face_id < num_faces; ++face_id) {
          Far::ConstIndexArray face_verts = refiner_->GetFaceVertices(level, face_id);

          if (face_verts.size() == 4) {
              // Quad → 2 triangles
              result.triangles.push_back(face_verts[0]);
              result.triangles.push_back(face_verts[1]);
              result.triangles.push_back(face_verts[2]);
              triangle_to_face_map_.push_back(face_id);

              result.triangles.push_back(face_verts[0]);
              result.triangles.push_back(face_verts[2]);
              result.triangles.push_back(face_verts[3]);
              triangle_to_face_map_.push_back(face_id);
          } else if (face_verts.size() == 3) {
              // Already a triangle
              for (int i = 0; i < 3; ++i) {
                  result.triangles.push_back(face_verts[i]);
              }
              triangle_to_face_map_.push_back(face_id);
          }
      }

      // Copy vertex positions
      result.vertices = vertex_positions;

      // Compute normals
      result.normals.resize(num_verts * 3);
      // TODO: Implement normal computation

      // Store face parents
      result.face_parents = triangle_to_face_map_;

      return result;
  }
  ```

- [ ] Rebuild and test:
  ```bash
  cd cpp_core/build
  make -j$(sysctl -n hw.ncpu)
  ```

- [ ] Test full pipeline with `test_bridge.py`

**Tests**:
```bash
python3 test_bridge.py

# Should now show:
# ✅ Display mesh generated
#    Vertices: 242 (for level 2 of simple geometry)
#    Triangles: 480
```

**Success Metrics**:
- ✅ Tessellation generates non-empty vertex/triangle arrays
- ✅ Vertex count increases exponentially with subdivision level
- ✅ Triangle count = 2 × num_quads (approximately)
- ✅ No crashes or memory leaks
- ✅ Face parent mapping correct (all face_map indices valid)

**Deliverable**: Complete tessellation pipeline generating triangle meshes from SubD

**Milestone 0.2 Complete**: End-to-end data flow working (Rhino → HTTP → C++ → Tessellation)

---

### Day 11: Exact Limit Surface Evaluation

**Tasks**:
- [ ] Implement Stam limit surface evaluation in `subd_evaluator.cpp`
- [ ] Study OpenSubdiv `tutorials/far/tutorial_1_2` for limit evaluation
- [ ] Implement using `Far::PatchTable` and `Far::PatchMap`

**Tests**:
```python
# Test exact evaluation
evaluator = bridge.fetch_subd()

# Evaluate at face center
pt = evaluator.evaluate_limit_point(face_index=0, u=0.5, v=0.5)
print(f"Limit point: ({pt.x}, {pt.y}, {pt.z})")
```

**Success Metrics**:
- ✅ evaluate_limit_point returns valid Point3D
- ✅ Points lie on smooth surface (visual check in Rhino)
- ✅ Evaluation fast (<1ms per point)

**Deliverable**: Exact limit surface evaluation working

---

### Day 12: VTK Integration & Validation

**Tasks**:
- [ ] Update `ceramic_mold_analyzer/app/ui/viewport_3d.py` to use C++ tessellation
- [ ] Create method `display_cpp_subd(evaluator, subdivision_level=3)`
- [ ] Render tessellated mesh in VTK viewport
- [ ] Add controls for subdivision level (slider 1-5)

**Tests**:
1. Visual: SubD sphere should look smooth at level 3+
2. Performance: 4 viewports at 30 FPS with level 3
3. Accuracy: Compare Rhino vs Desktop display (should match)

**Success Metrics**:
- ✅ VTK displays tessellated SubD correctly
- ✅ Smooth shading working
- ✅ Can adjust subdivision level interactively
- ✅ No visual artifacts or gaps
- ✅ Performance acceptable (>30 FPS)

**Deliverable**: Complete visualization pipeline Rhino → C++ → VTK

---

### Day 13: Validation Testing

**Tasks**:
- [ ] **CRITICAL TEST**: Lossless verification
  - Create SubD sphere (radius=5.0) in Rhino
  - Evaluate limit point at (face=0, u=0.5, v=0.5) in Rhino
  - Fetch via bridge, evaluate same point in C++
  - Compare coordinates: error should be <1e-6
- [ ] Test with extraordinary vertices (valence 3, 5, 6)
- [ ] Test with edge creases
- [ ] Test with open vs closed SubD
- [ ] Performance profiling

**Tests**:
```python
#!/usr/bin/env python3
"""Lossless validation test"""

# Rhino evaluation (get from Grasshopper)
rhino_point = (4.33012, 2.16506, 3.06186)  # Example

# Desktop evaluation
evaluator = bridge.fetch_subd()
desktop_point = evaluator.evaluate_limit_point(0, 0.5, 0.5)

# Compare
error = math.sqrt(
    (desktop_point.x - rhino_point[0])**2 +
    (desktop_point.y - rhino_point[1])**2 +
    (desktop_point.z - rhino_point[2])**2
)

print(f"Error: {error:.10f}")
assert error < 1e-6, f"Lossless validation failed! Error = {error}"
print("✅ Lossless validation PASSED")
```

**Success Metrics**:
- ✅ Limit surface evaluation error <1e-6 vs Rhino
- ✅ Works with all valences (3, 4, 5, 6+)
- ✅ Edge creases preserved correctly
- ✅ Tessellation time <100ms for 10K control points
- ✅ Memory usage reasonable (<500MB for typical geometry)

**Deliverable**: Validated lossless SubD evaluation matching Rhino precision

---

## Phase 0 Success Metrics Summary

### Technical Validation
- [ ] ✅ OpenSubdiv 3.6+ installed with Metal backend
- [ ] ✅ C++ module builds without errors
- [ ] ✅ Python bindings load successfully
- [ ] ✅ Control cage transfers from Rhino via HTTP
- [ ] ✅ Topology refiner created correctly
- [ ] ✅ Tessellation generates valid triangle meshes
- [ ] ✅ **Exact limit surface evaluation: error <1e-6 vs Rhino** (CRITICAL)
- [ ] ✅ VTK displays tessellated SubD smoothly
- [ ] ✅ Works with extraordinary vertices (valence ≠ 4)
- [ ] ✅ Edge creases preserved

### Performance Benchmarks
- [ ] ✅ Tessellation: <100ms for 10K control points at level 3
- [ ] ✅ Limit evaluation: <1ms per point
- [ ] ✅ VTK rendering: >30 FPS with 4 viewports
- [ ] ✅ Memory: <500MB for typical geometry

### Integration Tests
- [ ] ✅ Fetch SubD from Rhino → Initialize evaluator → Tessellate → Display in VTK
- [ ] ✅ Change subdivision level → VTK updates in <100ms
- [ ] ✅ Modify SubD in Rhino → Desktop detects change → Re-tessellates
- [ ] ✅ Test with 5+ different SubD forms (sphere, torus, custom, open, closed)

### Deliverables
- [ ] ✅ `cpp_core/` directory with complete C++ module
- [ ] ✅ OpenSubdiv integration fully functional
- [ ] ✅ pybind11 bindings complete
- [ ] ✅ Grasshopper HTTP server operational
- [ ] ✅ Desktop bridge transfers control cage
- [ ] ✅ VTK visualization pipeline working
- [ ] ✅ Documentation of build process
- [ ] ✅ Test suite for validation

**Phase 0 Complete**: C++ foundation proven, lossless architecture validated ✅

---

# PHASE 1: INTERACTIVE FOUNDATION (3 months)

**Goal**: Build complete UI with mathematical analysis and mold generation

**Phase Success Criteria**:
- [ ] Multi-viewport system with independent cameras
- [ ] Edit modes (Solid/Panel/Edge/Vertex) working with C++ backend
- [ ] At least ONE mathematical lens discovers regions
- [ ] Constraint validation detects undercuts
- [ ] Can generate NURBS molds and export to Rhino
- [ ] Complete workflow: Rhino → Analyze → Edit → Generate → Export

---

## Month 1: UI Foundation & Region System

### Week 1: Multi-Viewport Integration

**Day 1-2: Viewport Manager with C++ Backend**

**Tasks**:
- [ ] Reuse existing `ViewportLayoutManager` from Week 2 (old roadmap)
- [ ] Update to use C++ tessellation instead of Python mesh
- [ ] Test 4-viewport layout with C++ SubDEvaluator
- [ ] Ensure each viewport can have different subdivision levels

**Tests**:
```python
# Test 4 viewports simultaneously
layout_manager.set_layout(ViewportLayout.FOUR_GRID)
for viewport in layout_manager.viewports:
    viewport.display_cpp_subd(evaluator, subdivision_level=3)

# Measure FPS
assert fps > 30, "Performance requirement not met"
```

**Success Metrics**:
- ✅ 4 viewports render simultaneously at >30 FPS
- ✅ Each viewport independent camera controls
- ✅ Subdivision level adjustable per viewport
- ✅ Memory usage <1GB with 4 viewports
- ✅ Smooth camera interaction (no lag)

**Deliverable**: Multi-viewport system functional with C++ backend

---

**Day 3-4: View Types & Display Modes**

**Tasks**:
- [ ] Implement orthographic views (Top, Front, Right)
- [ ] Add perspective and isometric views
- [ ] Implement display modes (Solid, Wireframe, X-ray)
- [ ] Add per-viewport view type selector

**Tests**:
- Visual check: Orthographic views show correct projections
- Visual check: Wireframe mode shows edges clearly
- Performance: Display mode changes <100ms

**Success Metrics**:
- ✅ All standard view types working
- ✅ Display modes render correctly
- ✅ Fast switching between modes
- ✅ View types labeled in UI

**Deliverable**: Professional CAD viewport system

---

**Day 5: Toolbar & Controls**

**Tasks**:
- [ ] Add subdivision level slider (1-5)
- [ ] Add viewport layout buttons (1/2H/2V/4)
- [ ] Add view type dropdown per viewport
- [ ] Add display mode toggles

**Tests**:
- All controls respond correctly
- Changes update viewports in real-time

**Success Metrics**:
- ✅ Intuitive UI controls
- ✅ Real-time updates (<100ms)
- ✅ Clear visual feedback

**Deliverable**: Complete viewport control system

**Week 1 Milestone**: Professional multi-viewport system with C++ rendering ✅

---

### Week 2: Edit Mode System

**Day 1-2: Edit Mode Integration with C++ face_map**

**Tasks**:
- [ ] Reuse existing `EditModeManager` from Week 4 (old roadmap)
- [ ] Update pickers to use `face_map` from C++ tessellation
- [ ] Map picked triangles back to SubD control faces
- [ ] Test Panel mode selection with C++ backend

**Code**:
```python
class SubDFacePicker:
    def __init__(self, evaluator, face_map):
        self.evaluator = evaluator
        self.face_map = face_map  # From TessellationResult

    def pick_at_screen(self, x, y):
        # Ray cast to tessellated mesh
        triangle_id = self.ray_cast(x, y)

        # Map back to SubD control face
        if triangle_id < len(self.face_map):
            control_face_id = self.face_map[triangle_id]
            return control_face_id

        return None
```

**Tests**:
- Click on tessellated mesh → Should select correct control face
- Visual: Highlight should match expected face

**Success Metrics**:
- ✅ Triangle→Face mapping works correctly
- ✅ Selection highlights correct control face
- ✅ Multi-select (Shift+Click) functional
- ✅ Selection toggle working

**Deliverable**: Face picking integrated with C++ backend

---

**Day 3: Edge & Vertex Modes**

**Tasks**:
- [ ] Implement edge selection using SubD edge topology
- [ ] Implement vertex selection on control vertices
- [ ] Update highlighting for edges and vertices

**Tests**:
- Edge mode: Click edge → Highlight entire edge
- Vertex mode: Click vertex → Highlight control vertex

**Success Metrics**:
- ✅ All edit modes (S/P/E/V) working
- ✅ Selection feedback clear and immediate
- ✅ Multi-select functional for all modes

**Deliverable**: Complete edit mode system

---

**Day 4-5: Region Definition from Selection**

**Tasks**:
- [ ] Create `ParametricRegion` from selected faces
- [ ] Store regions in `ApplicationState`
- [ ] Visualize regions with distinct colors
- [ ] Implement region selection (click region to select)

**Code**:
```python
@dataclass
class ParametricRegion:
    """Parametric region definition"""
    id: str
    face_indices: Set[int]  # SubD control face IDs
    color: Tuple[float, float, float]
    is_pinned: bool = False
    generation_method: str = "manual"
    unity_strength: float = 0.0
```

**Tests**:
- Select faces → Create region → Should visualize with color
- Multiple regions should have distinct colors

**Success Metrics**:
- ✅ Can create regions from face selection
- ✅ Regions visualized clearly
- ✅ Region selection working
- ✅ Region list UI updates

**Deliverable**: Manual region creation system

**Week 2 Milestone**: Edit modes fully integrated with C++ backend ✅

---

### Week 3: Region Visualization & State Management

**Day 1-2: Region Rendering**

**Tasks**:
- [ ] Color tessellated triangles by region
- [ ] Use `face_map` to determine triangle→region mapping
- [ ] Implement region boundary highlighting
- [ ] Add region hover effects

**Code**:
```python
def color_mesh_by_regions(tessellation_result, regions):
    """Color triangles based on region membership"""
    triangle_colors = []
    face_map = tessellation_result.face_parents

    for tri_id in range(len(face_map) // 3):
        control_face_id = face_map[tri_id]

        # Find which region this face belongs to
        region_color = (0.7, 0.7, 0.7)  # Default gray
        for region in regions:
            if control_face_id in region.face_indices:
                region_color = region.color
                break

        triangle_colors.extend(region_color)

    return triangle_colors
```

**Tests**:
- Regions should have distinct, vibrant colors
- Boundaries should be clearly visible

**Success Metrics**:
- ✅ Region coloring correct on tessellated mesh
- ✅ Boundaries highlighted clearly
- ✅ Hover feedback immediate
- ✅ Performance acceptable with 10+ regions

**Deliverable**: Clear region visualization

---

**Day 3: Pin/Unpin System**

**Tasks**:
- [ ] Implement region pinning in `ApplicationState`
- [ ] Visual indicator for pinned regions (lock icon)
- [ ] Prevent editing of pinned regions
- [ ] Add pin/unpin button to region list

**Tests**:
- Pin region → Should show lock icon
- Try to edit pinned region → Should be prevented

**Success Metrics**:
- ✅ Pin state persists correctly
- ✅ Visual feedback clear
- ✅ Pinned regions immutable
- ✅ Easy to pin/unpin from UI

**Deliverable**: Region pinning system operational

---

**Day 4-5: State Management & Undo/Redo**

**Tasks**:
- [ ] Store `SubDEvaluator` reference in `ApplicationState`
- [ ] Implement region state serialization
- [ ] Add undo/redo for region operations
- [ ] Test state transitions

**Tests**:
- Create region → Undo → Region disappears
- Pin region → Undo → Region unpinned
- Multiple undo/redo operations work correctly

**Success Metrics**:
- ✅ Undo/redo working for all region operations
- ✅ State persists correctly
- ✅ No memory leaks
- ✅ History limited to 100 items

**Deliverable**: Complete state management system

**Week 3 Milestone**: Region system fully functional ✅

---

### Week 4: Iteration System

**Day 1-2: Iteration Data Structure**

**Tasks**:
- [ ] Design iteration storage format
- [ ] Serialize `ParametricRegion` list
- [ ] Store control cage data (not full evaluator)
- [ ] Implement save/load iteration

**Code**:
```python
@dataclass
class DesignIteration:
    id: str
    name: str
    timestamp: datetime
    regions: List[ParametricRegion]
    control_cage_data: Dict  # Vertices, faces, creases
    thumbnail: Optional[bytes]
    lens_used: Optional[str]
    parameters: Dict
```

**Tests**:
- Save iteration → Load iteration → State should match

**Success Metrics**:
- ✅ Iterations save/load correctly
- ✅ Control cage preserved exactly
- ✅ Regions restored correctly
- ✅ No data loss

**Deliverable**: Iteration persistence system

---

**Day 3: Iteration UI Panel**

**Tasks**:
- [ ] Create iteration sidebar panel
- [ ] Display iteration list with thumbnails
- [ ] Add "New Iteration" button
- [ ] Add "Duplicate Iteration" button
- [ ] Add "Delete Iteration" button

**Tests**:
- UI responds correctly to all actions
- Thumbnails load quickly

**Success Metrics**:
- ✅ Professional UI design
- ✅ Fast iteration switching
- ✅ Thumbnails clear and useful
- ✅ Intuitive workflow

**Deliverable**: Iteration management UI

---

**Day 4-5: Thumbnail Generation & Iteration Switching**

**Tasks**:
- [ ] Capture viewport screenshot
- [ ] Generate 256x256 thumbnail
- [ ] Store thumbnail with iteration
- [ ] Implement iteration switching with full state restore

**Tests**:
- Switch between iterations quickly
- All state (regions, camera, settings) restores

**Success Metrics**:
- ✅ Thumbnails high quality
- ✅ Switching fast (<500ms)
- ✅ Complete state restoration
- ✅ Can manage 10+ iterations

**Deliverable**: Complete iteration system

**Week 4 Milestone**: Non-destructive design exploration enabled ✅

**Month 1 Milestone**: Complete UI foundation with region management ✅

---

## Month 2: Mathematical Analysis

### Week 5: Curvature Analysis (C++)

**Day 1-2: C++ Curvature Analyzer**

**Tasks**:
- [ ] Create `cpp_core/analysis/curvature_analyzer.h/cpp`
- [ ] Implement curvature computation using limit surface derivatives
- [ ] Reference OpenSubdiv limit evaluation for derivative computation
- [ ] Add Python bindings

**Code**:
```cpp
// cpp_core/analysis/curvature_analyzer.h
#pragma once
#include "../geometry/subd_evaluator.h"

namespace latent {

struct CurvatureData {
    float mean_curvature;      // H = (κ₁ + κ₂) / 2
    float gaussian_curvature;  // K = κ₁ × κ₂
    float principal_k1;        // Maximum principal curvature
    float principal_k2;        // Minimum principal curvature
    Point3D principal_dir1;    // Direction of κ₁
    Point3D principal_dir2;    // Direction of κ₂
};

class CurvatureAnalyzer {
public:
    // Compute curvature at face center
    CurvatureData compute_at_face(const SubDEvaluator& eval,
                                   int face_index);

    // Compute for all control faces
    std::vector<CurvatureData> compute_all_faces(const SubDEvaluator& eval);
private:
    void compute_shape_operator(const Point3D& du, const Point3D& dv,
                               const Point3D& duu, const Point3D& duv,
                               const Point3D& dvv, const Point3D& normal,
                               float& k1, float& k2);
};

}
```

**Implementation**:
```cpp
CurvatureData CurvatureAnalyzer::compute_at_face(
    const SubDEvaluator& eval, int face_index) {

    // Evaluate at face center (u=0.5, v=0.5)
    Point3D point, normal;
    Point3D du, dv;      // First derivatives
    Point3D duu, duv, dvv;  // Second derivatives

    // Use OpenSubdiv's derivative evaluation
    eval.evaluate_limit_with_derivatives(face_index, 0.5, 0.5,
                                        point, normal,
                                        du, dv, duu, duv, dvv);

    // Compute principal curvatures from derivatives
    float k1, k2;
    compute_shape_operator(du, dv, duu, duv, dvv, normal, k1, k2);

    CurvatureData result;
    result.principal_k1 = k1;
    result.principal_k2 = k2;
    result.mean_curvature = (k1 + k2) / 2.0f;
    result.gaussian_curvature = k1 * k2;

    // TODO: Compute principal directions

    return result;
}
```

**Tests**:
```python
# Test on sphere (radius r)
# Expected: H = 1/r, K = 1/r²
curvatures = analyzer.compute_all_faces(evaluator)
mean_curv = curvatures[0].mean_curvature
gauss_curv = curvatures[0].gaussian_curvature

assert abs(mean_curv - 1/r) < 0.01  # 1% tolerance
assert abs(gauss_curv - 1/(r*r)) < 0.01
```

**Success Metrics**:
- ✅ Curvature computation accurate on test geometries
- ✅ Sphere: H=1/r, K=1/r² (within 1%)
- ✅ Cylinder: H=1/(2r), K=0
- ✅ Saddle: K<0 everywhere
- ✅ Fast: <50ms for 1000 faces

**Deliverable**: Accurate curvature analyzer in C++

---

**Day 3: Python Curvature Bindings**

**Tasks**:
- [ ] Add pybind11 bindings for `CurvatureAnalyzer`
- [ ] Expose `CurvatureData` struct
- [ ] Test from Python

**Code**:
```cpp
// In py_bindings.cpp
py::class_<CurvatureData>(m, "CurvatureData")
    .def_readonly("mean_curvature", &CurvatureData::mean_curvature)
    .def_readonly("gaussian_curvature", &CurvatureData::gaussian_curvature)
    .def_readonly("principal_k1", &CurvatureData::principal_k1)
    .def_readonly("principal_k2", &CurvatureData::principal_k2);

py::class_<CurvatureAnalyzer>(m, "CurvatureAnalyzer")
    .def(py::init<>())
    .def("compute_at_face", &CurvatureAnalyzer::compute_at_face)
    .def("compute_all_faces", &CurvatureAnalyzer::compute_all_faces);
```

**Tests**:
```python
import cpp_core

analyzer = cpp_core.CurvatureAnalyzer()
curvatures = analyzer.compute_all_faces(evaluator)

print(f"Face 0: H={curvatures[0].mean_curvature:.4f}, "
      f"K={curvatures[0].gaussian_curvature:.4f}")
```

**Success Metrics**:
- ✅ Bindings compile correctly
- ✅ Curvature data accessible from Python
- ✅ No memory leaks
- ✅ Fast access (overhead <1ms)

**Deliverable**: Curvature analyzer accessible from Python

---

**Day 4-5: Curvature Visualization**

**Tasks**:
- [ ] Create `app/analysis/curvature_viz.py`
- [ ] Color mesh by mean curvature
- [ ] Color mesh by Gaussian curvature
- [ ] Add color map selector (rainbow, viridis, etc.)

**Code**:
```python
def visualize_curvature(evaluator, curvature_type='mean'):
    """Color mesh by curvature field"""
    analyzer = cpp_core.CurvatureAnalyzer()
    curvatures = analyzer.compute_all_faces(evaluator)

    # Extract curvature values
    if curvature_type == 'mean':
        values = [c.mean_curvature for c in curvatures]
    elif curvature_type == 'gaussian':
        values = [c.gaussian_curvature for c in curvatures]

    # Normalize to [0, 1]
    min_val, max_val = min(values), max(values)
    normalized = [(v - min_val) / (max_val - min_val) for v in values]

    # Map to colors
    colors = [colormap(n) for n in normalized]

    return colors
```

**Tests**:
- Visual: Sphere should show uniform color (constant curvature)
- Visual: Torus should show distinct regions (varying curvature)

**Success Metrics**:
- ✅ Curvature visualization clear and useful
- ✅ Color maps easy to understand
- ✅ Works with all geometry types
- ✅ Interactive updates fast

**Deliverable**: Curvature visualization system

**Week 5 Milestone**: Exact curvature computation working ✅

---

### Week 6: Differential Decomposition

**Day 1-2: Region Discovery Algorithm**

**Tasks**:
- [ ] Create `app/analysis/differential_decomposition.py`
- [ ] Implement curvature-based region growing
- [ ] Classify faces by curvature type
- [ ] Group connected faces with similar curvature

**Algorithm**:
```python
class DifferentialDecomposition:
    def analyze(self, evaluator, pinned_face_ids=set()):
        # Compute curvature for all faces
        analyzer = cpp_core.CurvatureAnalyzer()
        curvatures = analyzer.compute_all_faces(evaluator)

        # Classify faces by type
        face_types = []
        for c in curvatures:
            if abs(c.gaussian_curvature) < 0.001 and abs(c.mean_curvature) < 0.001:
                face_types.append('planar')
            elif c.gaussian_curvature > 0.01:
                face_types.append('elliptic')  # Bowl-like
            elif c.gaussian_curvature < -0.01:
                face_types.append('hyperbolic')  # Saddle-like
            else:
                face_types.append('parabolic')  # Cylindrical

        # Region growing: connected faces of same type
        regions = []
        visited = set(pinned_face_ids)

        for face_id in range(len(face_types)):
            if face_id in visited:
                continue

            # Start new region
            region_faces = set()
            stack = [face_id]
            region_type = face_types[face_id]

            while stack:
                fid = stack.pop()
                if fid in visited:
                    continue

                # Check if same type
                if face_types[fid] != region_type:
                    continue

                region_faces.add(fid)
                visited.add(fid)

                # Add neighbors
                neighbors = get_face_neighbors(evaluator, fid)
                stack.extend(neighbors)

            if len(region_faces) >= 3:  # Minimum region size
                regions.append(ParametricRegion(
                    id=f"diff_{len(regions)}",
                    face_indices=region_faces,
                    generation_method="differential",
                    unity_principle=f"Curvature type: {region_type}",
                    unity_strength=compute_coherence(curvatures, region_faces)
                ))

        return regions
```

**Tests**:
- Sphere: Should produce 1 elliptic region
- Torus: Should produce 2-3 regions (inner/outer surfaces)
- Saddle: Should produce hyperbolic regions

**Success Metrics**:
- ✅ Regions discovered automatically
- ✅ Curvature classification correct
- ✅ Connected components algorithm works
- ✅ Minimum region size enforced
- ✅ Resonance score computed

**Deliverable**: Working differential decomposition

---

**Day 3: UI Integration**

**Tasks**:
- [ ] Connect Differential lens to "Analyze" button
- [ ] Display discovered regions
- [ ] Show unity principle in region list
- [ ] Display resonance score

**Tests**:
- Click Analyze → Regions appear
- Region list shows correct metadata

**Success Metrics**:
- ✅ Analysis runs without errors
- ✅ Regions visualized immediately
- ✅ Region metadata displayed clearly
- ✅ Can re-analyze after edits

**Deliverable**: Differential lens integrated with UI

---

**Day 4-5: Parameter Tuning & Testing**

**Tasks**:
- [ ] Add parameter dialog for curvature thresholds
- [ ] Test on variety of forms
- [ ] Document which forms work well
- [ ] Tune default parameters

**Forms to Test**:
- Simple: Sphere, cylinder, cone
- Medium: Torus, saddle surface
- Complex: Organic blob, architectural form

**Success Metrics**:
- ✅ Parameters adjustable via UI
- ✅ Good defaults for most forms
- ✅ Resonance scores meaningful
- ✅ Documentation complete

**Deliverable**: Production-ready differential lens

**Week 6 Milestone**: First mathematical lens fully operational ✅

---

### Week 7: Spectral Analysis (Python/SciPy)

**Day 1-2: Laplacian Matrix Construction**

**Tasks**:
- [ ] Build cotangent-weight Laplacian from SubD topology
- [ ] Use SciPy sparse matrix format
- [ ] Implement mass matrix for generalized eigenvalue problem

**Code**:
```python
import scipy.sparse as sp
import scipy.sparse.linalg as spla

def build_laplacian(evaluator):
    """Build discrete Laplace-Beltrami operator"""
    n = evaluator.get_control_vertex_count()

    # Build adjacency from SubD topology
    # Use cotangent weights for accuracy

    L = sp.lil_matrix((n, n))
    M = sp.lil_matrix((n, n))  # Mass matrix

    # ... implement cotangent weight computation

    return L.tocsr(), M.tocsr()
```

**Tests**:
- Matrix should be symmetric
- Matrix should be negative semi-definite
- Smallest eigenvalue should be ~0

**Success Metrics**:
- ✅ Laplacian matrix correct topology
- ✅ Cotangent weights computed accurately
- ✅ Matrix properties validated

**Deliverable**: Discrete Laplacian operator

---

**Day 3-4: Eigenvalue Solver**

**Tasks**:
- [ ] Solve generalized eigenvalue problem L v = λ M v
- [ ] Extract first 10 eigenvectors
- [ ] Visualize eigenfunctions on mesh

**Code**:
```python
# Solve eigenvalue problem
L, M = build_laplacian(evaluator)
eigenvalues, eigenvectors = spla.eigsh(L, k=10, M=M, sigma=0)

# eigenvectors[:, i] is the i-th eigenfunction
```

**Tests**:
- Sphere: Should see harmonic spherical patterns
- First eigenvalue ~0 (constant function)
- Eigenvalues increasing order

**Success Metrics**:
- ✅ Eigenvalue solver converges
- ✅ Eigenfunctions smooth
- ✅ Computation fast (<5 seconds)

**Deliverable**: Spectral decomposition working

---

**Day 5: Nodal Domain Extraction**

**Tasks**:
- [ ] Extract zero-crossings of eigenfunctions (nodal lines)
- [ ] Create regions from nodal domains
- [ ] Test on various modes

**Tests**:
- Visual: Nodal lines should divide surface cleanly

**Success Metrics**:
- ✅ Nodal domains extracted correctly
- ✅ Regions coherent and connected
- ✅ Multiple modes available

**Deliverable**: Spectral lens operational

**Week 7 Milestone**: Two mathematical lenses working ✅

---

### Week 8: Region Management Polish

**Tasks**:
- [ ] Implement region merging
- [ ] Implement region splitting
- [ ] Add region editing tools
- [ ] Polish region list UI
- [ ] Add region search/filter

**Tests**:
- All region operations work smoothly
- UI responsive and intuitive

**Success Metrics**:
- ✅ Complete region manipulation toolkit
- ✅ Professional UI/UX
- ✅ All edge cases handled

**Deliverable**: Production-ready region management

**Month 2 Milestone**: Mathematical analysis fully functional ✅

---

## Month 3: Constraints & Mold Generation

### Week 9: Constraint Validation (C++)

**Day 1-3: Undercut Detection**

**Tasks**:
- [ ] Create `cpp_core/constraints/validator.h/cpp`
- [ ] Implement ray-casting undercut detection
- [ ] Check draft direction feasibility
- [ ] Add Python bindings

**Algorithm**:
```cpp
class UndercutDetector {
public:
    struct UndercutResult {
        bool has_undercuts;
        std::vector<int> undercut_faces;
        float severity;  // 0-1 score
    };

    UndercutResult detect(const SubDEvaluator& eval,
                         const ParametricRegion& region,
                         const Point3D& draft_direction);
private:
    bool face_has_undercut(const SubDEvaluator& eval,
                          int face_id,
                          const Point3D& draft_dir);
};
```

**Tests**:
- Simple box: No undercuts in Z direction
- Overhang: Should detect undercuts
- Sphere: No undercuts in any direction

**Success Metrics**:
- ✅ Undercut detection accurate
- ✅ False positive rate <5%
- ✅ Fast: <100ms for 1000 faces

**Deliverable**: Undercut detection working

---

**Day 4-5: Draft Angle Validation**

**Tasks**:
- [ ] Compute draft angles per face
- [ ] Check against minimum threshold (0.5°)
- [ ] Visualize problem areas
- [ ] Add to constraint panel

**Tests**:
- Vertical wall: Should show 0° draft (warning)
- Angled wall at 2°: Should pass

**Success Metrics**:
- ✅ Draft angle computation accurate
- ✅ Visualization clear
- ✅ Warnings actionable

**Deliverable**: Draft angle validation

**Week 9 Milestone**: Constraint validation operational ✅

---

### Week 10: NURBS Mold Generation

**Day 1-2: OpenCASCADE Installation**

**Tasks**:
- [ ] Install OpenCASCADE via Homebrew
  ```bash
  brew install opencascade
  ```
- [ ] Test OCCT installation
- [ ] Create minimal OCCT test program

**Tests**:
```cpp
#include <BRepPrimAPI_MakeBox.hxx>
#include <TopoDS_Shape.hxx>

// Create test box
TopoDS_Shape box = BRepPrimAPI_MakeBox(10, 10, 10).Shape();
```

**Success Metrics**:
- ✅ OCCT installs without errors
- ✅ Headers found by CMake
- ✅ Test program compiles and runs

**Deliverable**: OpenCASCADE ready for use

---

**Day 3-5: NURBS Surface Generation**

**Tasks**:
- [ ] Create `cpp_core/geometry/nurbs_generator.h/cpp`
- [ ] Sample limit surface at grid of (u,v) parameters
- [ ] Fit NURBS surface through sampled points
- [ ] Apply draft angle transformation
- [ ] Create solid Brep with wall thickness

**Algorithm**:
```cpp
class NURBSMoldGenerator {
public:
    struct MoldPiece {
        TopoDS_Shape solid;
        std::vector<TopoDS_Face> mold_surface;
        Point3D draft_direction;
        float draft_angle;
    };

    MoldPiece generate(const SubDEvaluator& eval,
                      const ParametricRegion& region,
                      const MoldParameters& params);
private:
    Handle(Geom_BSplineSurface) fit_nurbs(
        const std::vector<Point3D>& points,
        int u_samples, int v_samples);

    TopoDS_Shape apply_draft(const Handle(Geom_BSplineSurface)& surface,
                            const Point3D& draft_dir,
                            float draft_angle);
};
```

**Tests**:
- Generate mold from simple region
- Verify NURBS surface smooth
- Check draft angle correct

**Success Metrics**:
- ✅ NURBS generation successful
- ✅ Surface quality high (G1 continuity)
- ✅ Draft angle applied correctly
- ✅ Solid geometry valid

**Deliverable**: NURBS mold generation working

**Week 10 Milestone**: Mold generation functional ✅

---

### Week 11: Mold Export to Rhino

**Day 1-3: Rhino Export Format**

**Tasks**:
- [ ] Serialize NURBS Brep to Rhino format
- [ ] Create POST /molds endpoint in Grasshopper
- [ ] Test mold import in Rhino

**Grasshopper Server**:
```python
def do_POST(self):
    if self.path == '/molds':
        # Receive NURBS mold data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        mold_data = json.loads(post_data)

        # Import into Rhino
        # ... convert NURBS data to Rhino geometry

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success"}).encode())
```

**Tests**:
- Export mold → Import in Rhino → Geometry should match

**Success Metrics**:
- ✅ Molds export successfully
- ✅ Geometry preserved exactly
- ✅ Round-trip lossless

**Deliverable**: Rhino export working

---

**Day 4-5: Mold Generation UI**

**Tasks**:
- [ ] Create mold parameter dialog
- [ ] Add "Generate Molds" button
- [ ] Show progress during generation
- [ ] Display results in viewport
- [ ] Add "Send to Rhino" button

**Tests**:
- Full workflow: Analyze → Edit → Generate → Export

**Success Metrics**:
- ✅ Intuitive UI workflow
- ✅ Progress feedback clear
- ✅ Results preview useful

**Deliverable**: Complete mold generation UI

**Week 11 Milestone**: End-to-end mold pipeline working ✅

---

### Week 12: Testing & Polish

**Day 1-2: Unit Tests**

**Tasks**:
- [ ] Set up pytest framework
- [ ] Write C++ unit tests (Google Test)
- [ ] Write Python unit tests
- [ ] Test coverage >70%

**Test Categories**:
- SubDEvaluator: Initialization, tessellation, limit evaluation
- CurvatureAnalyzer: Accuracy on known geometries
- Region operations: Create, merge, split, pin
- Constraint validation: Undercut detection, draft angles
- NURBS generation: Surface quality, draft application

**Success Metrics**:
- ✅ >70% code coverage
- ✅ All critical paths tested
- ✅ No regressions

**Deliverable**: Comprehensive test suite

---

**Day 3-4: Integration Testing**

**Tasks**:
- [ ] Test complete workflow end-to-end
- [ ] Test with variety of SubD forms
- [ ] Test error handling
- [ ] Test edge cases

**Test Scenarios**:
- Simple sphere: Should produce 1 region, generate valid mold
- Complex organic form: Multiple regions, all constraints pass
- Form with undercuts: Should detect and warn
- Pinned regions: Should exclude from re-analysis

**Success Metrics**:
- ✅ All scenarios work correctly
- ✅ Error handling robust
- ✅ Edge cases handled gracefully

**Deliverable**: Validated system

---

**Day 5: Performance Profiling & Optimization**

**Tasks**:
- [ ] Profile C++ code with Instruments (Xcode)
- [ ] Profile Python code with cProfile
- [ ] Identify and fix bottlenecks
- [ ] Document performance characteristics

**Benchmarks**:
- SubD tessellation: <100ms for 10K control points
- Curvature analysis: <200ms for 10K faces
- Region discovery: <500ms typical
- NURBS generation: <1s per region

**Success Metrics**:
- ✅ All operations within performance targets
- ✅ No memory leaks
- ✅ Responsive UI (no blocking)

**Deliverable**: Optimized, production-ready system

**Week 12 Milestone**: Complete, tested, polished MVP ✅

**Month 3 Milestone**: Full mold generation pipeline operational ✅

---

# PHASE 1 SUCCESS METRICS SUMMARY

## Technical Validation
- [ ] ✅ Multi-viewport system: 4 views at >30 FPS
- [ ] ✅ Edit modes: All modes (S/P/E/V) working with C++ backend
- [ ] ✅ Mathematical analysis: 2+ lenses discovering regions
- [ ] ✅ Curvature computation: Accurate on test geometries
- [ ] ✅ Region management: Create, edit, merge, split, pin
- [ ] ✅ Iteration system: Save/load design snapshots
- [ ] ✅ Constraint validation: Undercuts and draft angles detected
- [ ] ✅ NURBS generation: Valid mold geometry created
- [ ] ✅ Rhino export: Lossless round-trip

## Performance Benchmarks
- [ ] ✅ Tessellation: <100ms for 10K control points at level 3
- [ ] ✅ Curvature analysis: <200ms for 10K faces
- [ ] ✅ Region discovery: <500ms typical forms
- [ ] ✅ NURBS generation: <1s per region
- [ ] ✅ UI responsiveness: All interactions <100ms

## Integration Tests
- [ ] ✅ Complete workflow: Rhino → Analyze → Edit → Generate → Export
- [ ] ✅ Tested with 10+ diverse SubD forms
- [ ] ✅ Error handling robust
- [ ] ✅ Edge cases handled

## Code Quality
- [ ] ✅ Unit test coverage >70%
- [ ] ✅ No memory leaks
- [ ] ✅ Clean architecture (C++ core, Python UI)
- [ ] ✅ Well-documented

## Deliverables
- [ ] ✅ Functional desktop application
- [ ] ✅ C++ core with OpenSubdiv + OpenCASCADE
- [ ] ✅ Python UI with PyQt6 + VTK
- [ ] ✅ Grasshopper HTTP server
- [ ] ✅ Comprehensive test suite
- [ ] ✅ User documentation
- [ ] ✅ Developer documentation

**Phase 1 Complete**: Production-ready MVP ✅

---

# PHASE 2: PRODUCTION HARDENING (3-4 months)

**Goal**: Polish, optimize, add advanced features

## Additional Mathematical Lenses
- Flow/Geodesic decomposition (heat method)
- Morse decomposition (critical point theory)
- Thermal gradient lens (heat equation)
- Slip flow dynamics lens (laminar flow simulation)

## Advanced Features
- Multi-part mold assembly with registration keys
- Automatic parting line optimization
- Dance zone documentation system
- Export to STL, STEP, IGES
- File I/O (save/load session)

## Performance Optimization
- GPU acceleration via OpenSubdiv Metal backend
- Adaptive tessellation (level-of-detail)
- Parallel analysis (OpenMP)
- Caching strategies

## Machine Learning Integration
- Pattern recognition in aesthetic choices
- Suggested decompositions by form type
- Automated parameter tuning

---

# APPENDIX: BUILD & DEVELOPMENT

## Daily Development Workflow

```bash
# 1. Build C++ module
cd cpp_core/build
cmake ..
make -j$(sysctl -n hw.ncpu)

# 2. Run Python app
cd ../../ceramic_mold_analyzer
python3 launch.py

# 3. Run tests
pytest tests/
cd ../cpp_core/build && ctest
```

## C++ Development
- **IDE**: Xcode or CLion
- **Debugger**: lldb
- **Profiler**: Instruments (Xcode)
- **Style**: clang-format with Google style

## Python Development
- **IDE**: VS Code
- **Linter**: pylint, mypy
- **Formatter**: black
- **Style**: PEP 8 with type hints

## Dependencies

### System Requirements
- macOS 12+ (Monterey or later)
- Xcode Command Line Tools
- Python 3.11+
- 16GB RAM minimum (32GB recommended)
- Apple Silicon or Intel x86_64

### C++ Dependencies
```bash
brew install cmake
brew install pybind11
brew install tbb
brew install opensubdiv
brew install opencascade  # Phase 1, Month 3
```

### Python Dependencies
```bash
pip install PyQt6==6.9.1
pip install vtk==9.3.0
pip install numpy==1.26.2
pip install scipy==1.11.4
pip install requests==2.31.0
pip install pytest pytest-cov  # Testing
```

---

# CONCLUSION

This roadmap provides a **complete, detailed plan** with:

✅ **Phase 0 (3 weeks)**: C++ foundation with OpenSubdiv
  - Daily tasks, tests, and success metrics
  - Lossless architecture validated

✅ **Phase 1 (3 months)**: Full application with UI, analysis, molds
  - Month-by-month, week-by-week breakdown
  - Detailed tasks, tests, and deliverables
  - Clear success criteria at each milestone

✅ **Phase 2 (3-4 months)**: Production hardening
  - Advanced features and optimization

**Total timeline**: 4 months to MVP, 7-8 months to production v1.0

**The hybrid C++/Python architecture is not optional** - it's required for:
1. True lossless SubD limit surface evaluation (Stam eigenanalysis)
2. Real-time performance (10-100x faster than pure Python)
3. GPU acceleration via OpenSubdiv Metal backend
4. Production-grade mathematical fidelity

This is a **proven architecture** (FreeCAD, Blender, Rhino) adapted for ceramic mold generation with exact mathematical analysis.

---

*Document Version: 3.0 (Detailed Milestones & Metrics)*
*Last Updated: November 2025*
*Based on: v5.0 Specification + Technical Implementation Guide*
