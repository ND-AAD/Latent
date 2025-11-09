# Agent 3: CMakeLists.txt Build System

**Day**: 1
**Phase**: Phase 0 - C++ Core Foundation
**Duration**: 2-3 hours
**Estimated Cost**: $2-4 (40K tokens, Sonnet)

---

## Mission

Create complete CMake build system that:
- Links OpenSubdiv
- Creates static library (`latent_core`)
- Creates Python module via pybind11
- Works on macOS with Metal backend

---

## Context

You are setting up the C++ build system for a SubD geometry kernel. The build must:
1. Find and link OpenSubdiv (installed via Homebrew/source)
2. Find and link pybind11
3. Build static library for C++ code
4. Build Python extension module
5. Support Metal backend on macOS

**Project Root**: `Latent/`
**C++ Source**: `cpp_core/`

---

## Deliverables

**Files to Create**:
1. `cpp_core/CMakeLists.txt` - Main build configuration
2. `setup.py` - Python package with C++ extension (project root)

---

## Requirements

### CMakeLists.txt Structure

```cmake
cmake_minimum_required(VERSION 3.20)
project(latent_cpp_core VERSION 0.5.0 LANGUAGES CXX)

# C++17 required
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Release by default
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Find dependencies
find_package(OpenSubdiv REQUIRED)
find_package(pybind11 REQUIRED)

# Core static library
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

# Python module
pybind11_add_module(cpp_core python_bindings/py_bindings.cpp)
target_link_libraries(cpp_core PRIVATE latent_core)

# Install
install(TARGETS cpp_core LIBRARY DESTINATION .)
```

### setup.py (Optional - for pip install)

```python
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import subprocess
import os

class CMakeBuild(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_cmake(ext)

    def build_cmake(self, ext):
        cwd = os.path.abspath(os.path.dirname(__file__))
        build_dir = os.path.join(cwd, 'cpp_core', 'build')
        os.makedirs(build_dir, exist_ok=True)

        subprocess.check_call(['cmake', '..'], cwd=build_dir)
        subprocess.check_call(['make', '-j4'], cwd=build_dir)

class CMakeExtension(Extension):
    def __init__(self, name):
        super().__init__(name, sources=[])

setup(
    name="ceramic_mold_analyzer",
    version="0.5.0",
    ext_modules=[CMakeExtension('cpp_core')],
    cmdclass={"build_ext": CMakeBuild},
    packages=['ceramic_mold_analyzer'],
    python_requires=">=3.11",
)
```

---

## Build Instructions

Provide these in your output:

```bash
# Build C++ module
cd cpp_core
mkdir build && cd build
cmake ..
make -j$(sysctl -n hw.ncpu)

# Should produce:
# - liblatent_core.a (static library)
# - cpp_core.so (Python module)

# Test Python import
cd ..
python3 -c "import sys; sys.path.insert(0, 'build'); import cpp_core; print('✅ Import successful')"
```

---

## Success Criteria

- [ ] CMake configuration succeeds
- [ ] Finds OpenSubdiv
- [ ] Finds pybind11
- [ ] Builds without errors
- [ ] Produces `liblatent_core.a`
- [ ] Produces `cpp_core.so`
- [ ] Python can import module

---

## Common Issues

**OpenSubdiv not found**:
```cmake
# Add to CMakeLists.txt if needed:
set(CMAKE_PREFIX_PATH "/usr/local")
find_package(PkgConfig)
pkg_check_modules(OPENSUBDIV REQUIRED opensubdiv)
```

**pybind11 not found**:
```bash
# Install via homebrew if missing:
brew install pybind11
```

**Metal not enabled**:
```cmake
# Verify Metal support:
if(APPLE)
    message(STATUS "Enabling Metal backend for OpenSubdiv")
    target_compile_definitions(latent_core PUBLIC OPENSUBDIV_HAS_METAL)
endif()
```

---

## Testing

Create simple test to verify build:

```bash
# Test that symbols are present
nm cpp_core/build/liblatent_core.a | grep SubDEvaluator

# Test Python module loads
python3 -c "import sys; sys.path.insert(0, 'cpp_core/build'); import cpp_core; print(dir(cpp_core))"
```

---

## Integration Notes

**Dependencies**:
- Requires OpenSubdiv installed (Day 0)
- Requires pybind11 installed (Day 0)

**Used by**:
- All subsequent C++ agents will build on this
- Agent 5 will add to python_bindings/py_bindings.cpp

---

## Output Format

Provide:
1. Complete `CMakeLists.txt`
2. Complete `setup.py`
3. Build instructions
4. Test commands
5. Any troubleshooting notes

---

**Ready to begin!**
