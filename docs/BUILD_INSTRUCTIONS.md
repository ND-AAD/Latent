# Ceramic Mold Analyzer - Build Instructions

**Version**: 0.5.0 (Phase 0 Complete)
**Last Updated**: November 9, 2025
**Platform Support**: macOS 12+, Linux (Ubuntu 20.04+, Debian 11+)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Platform-Specific Setup](#platform-specific-setup)
4. [Building C++ Core](#building-c-core)
5. [Python Package Installation](#python-package-installation)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Development Workflow](#development-workflow)
9. [CI/CD Integration](#cicd-integration)

---

## Quick Start

**For impatient developers (assumes dependencies installed):**

```bash
# Clone repository
git clone https://github.com/yourusername/latent.git
cd latent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Build C++ core
cd cpp_core
mkdir -p build && cd build
cmake ..
make -j$(nproc)
cd ../..

# Launch application
python3 launch.py
```

**If dependencies are missing, continue reading for complete setup.**

---

## Prerequisites

### System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| **OS** | macOS 12, Ubuntu 20.04, Debian 11 | macOS 14, Ubuntu 22.04 |
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 4 GB | 8+ GB |
| **Disk** | 1 GB | 2 GB |
| **Python** | 3.11 | 3.12 |
| **CMake** | 3.20 | 3.28+ |

### Required Dependencies

#### 1. Python 3.11+

**macOS:**
```bash
# Check version
python3 --version  # Should be >= 3.11

# If needed, install via Homebrew
brew install python@3.12
```

**Linux (Ubuntu/Debian):**
```bash
# Check version
python3 --version

# If needed, install
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3.11-dev
```

#### 2. CMake 3.20+

**macOS:**
```bash
# Check version
cmake --version

# Install via Homebrew
brew install cmake
```

**Linux:**
```bash
# Check version
cmake --version

# Option 1: System package (may be old)
sudo apt-get install cmake

# Option 2: pip (always latest)
pip3 install cmake

# Option 3: Official binary (latest)
wget https://github.com/Kitware/CMake/releases/download/v3.28.1/cmake-3.28.1-linux-x86_64.sh
sudo sh cmake-3.28.1-linux-x86_64.sh --prefix=/usr/local --skip-license
```

#### 3. OpenSubdiv 3.6.0+

**Critical dependency for exact SubD evaluation.**

**macOS:**
```bash
# Install via Homebrew (easiest)
brew install opensubdiv

# Verify
pkg-config --modversion opensubdiv
# Should output: 3.6.0 or higher

# Check library location
ls /opt/homebrew/lib/libosd* || ls /usr/local/lib/libosd*
```

**Linux (Ubuntu/Debian):**

*Option 1: System packages (recommended for Ubuntu 22.04+)*
```bash
sudo apt-get update
sudo apt-get install \
    libosd-dev \
    libosdcpu3.5.0t64 \
    libosdgpu3.5.0t64

# Verify
pkg-config --modversion opensubdiv
dpkg -l | grep libosd
```

*Option 2: Build from source (Ubuntu 20.04 or if packages unavailable)*
```bash
# Install build dependencies
sudo apt-get install \
    build-essential \
    git \
    cmake \
    libglfw3-dev \
    libxinerama-dev \
    libxcursor-dev \
    libxi-dev \
    libeigen3-dev

# Clone OpenSubdiv
cd /tmp
git clone https://github.com/PixarAnimationStudios/OpenSubdiv.git
cd OpenSubdiv
git checkout v3_6_0

# Configure (CPU backend only, no GPU/examples)
mkdir build && cd build
cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DNO_EXAMPLES=ON \
    -DNO_TUTORIALS=ON \
    -DNO_REGRESSION=ON \
    -DNO_DOC=ON \
    -DNO_OMP=ON \
    -DNO_TBB=ON \
    -DNO_CUDA=ON \
    -DNO_OPENCL=ON \
    -DNO_METAL=ON \
    -DNO_GLFW=ON \
    -DNO_PTEX=ON \
    ..

# Build and install
make -j$(nproc)
sudo make install

# Verify installation
ls /usr/local/lib/libosd*
ls /usr/local/include/opensubdiv/

# Update library cache
sudo ldconfig
```

#### 4. pybind11 2.11.0+

**Python/C++ binding library.**

**All platforms:**
```bash
# Check if already installed
python3 -c "import pybind11; print(pybind11.__version__)"

# Install via pip
pip3 install pybind11

# Verify CMake can find it
python3 -c "import pybind11; print(pybind11.get_cmake_dir())"

# Install development headers (Linux only)
sudo apt-get install pybind11-dev  # Ubuntu/Debian
```

#### 5. Python Packages

```bash
# Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install all Python dependencies
pip install -r requirements.txt

# Or install individually
pip install \
    numpy>=2.0 \
    PyQt6>=6.9.0 \
    vtk>=9.3.0 \
    requests>=2.32.0 \
    matplotlib>=3.10.0
```

**requirements.txt contents:**
```
numpy>=2.0.0
PyQt6>=6.9.0
vtk>=9.3.0
requests>=2.32.0
matplotlib>=3.10.0
pybind11>=2.11.0
```

---

## Platform-Specific Setup

### macOS 12+ (Monterey, Ventura, Sonoma)

```bash
# Install Xcode Command Line Tools (if not already installed)
xcode-select --install

# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies via Homebrew
brew install \
    python@3.12 \
    cmake \
    opensubdiv

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Ready to build!
```

**macOS-Specific Notes:**
- **Metal Backend**: OpenSubdiv can use Metal for GPU acceleration on Apple Silicon
- **Library Paths**: Homebrew installs to `/opt/homebrew` (Apple Silicon) or `/usr/local` (Intel)
- **Python**: Use `python3.12` explicitly if multiple Python versions installed

### Ubuntu 22.04 LTS (Jammy)

```bash
# Update package list
sudo apt-get update

# Install build tools
sudo apt-get install \
    build-essential \
    git \
    cmake \
    python3.11 \
    python3.11-venv \
    python3.11-dev

# Install OpenSubdiv (available in Ubuntu 22.04+)
sudo apt-get install \
    libosd-dev \
    libosdcpu3.5.0t64 \
    libosdgpu3.5.0t64

# Install pybind11
sudo apt-get install pybind11-dev

# Install VTK dependencies
sudo apt-get install \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libxt-dev

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Ready to build!
```

### Ubuntu 20.04 LTS (Focal)

```bash
# Update package list
sudo apt-get update

# Install build tools
sudo apt-get install \
    build-essential \
    git \
    cmake \
    python3.11 \
    python3.11-venv \
    python3.11-dev

# Build OpenSubdiv from source (see Prerequisites section)
# ... follow OpenSubdiv build instructions above ...

# Install pybind11
pip3 install pybind11

# Install VTK dependencies
sudo apt-get install \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libxt-dev

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Ready to build!
```

### Debian 11 (Bullseye)

```bash
# Update package list
sudo apt-get update

# Install build tools
sudo apt-get install \
    build-essential \
    git \
    cmake \
    python3.11 \
    python3.11-venv \
    python3.11-dev

# Build OpenSubdiv from source (not in Debian repos)
# ... follow OpenSubdiv build instructions above ...

# Install pybind11
pip3 install pybind11

# Install VTK dependencies
sudo apt-get install \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libxt-dev

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Ready to build!
```

---

## Building C++ Core

### Standard Build (Recommended)

```bash
# Navigate to project root
cd /path/to/latent

# Navigate to cpp_core directory
cd cpp_core

# Create build directory
mkdir -p build
cd build

# Configure with CMake
cmake ..

# Expected output:
# -- Build type: Release
# -- Found OpenSubdiv: /usr/local/lib/libosdCPU.a
# -- Found pybind11: 2.11.1
# -- Configuring done
# -- Generating done
# -- Build files written to: /path/to/latent/cpp_core/build

# Build all targets (parallel)
# macOS:
make -j$(sysctl -n hw.ncpu)

# Linux:
make -j$(nproc)

# Expected output:
# [  8%] Building CXX object CMakeFiles/cpp_core_static.dir/geometry/subd_evaluator.cpp.o
# [ 16%] Building CXX object CMakeFiles/cpp_core_static.dir/utils/mesh_mapping.cpp.o
# [ 25%] Linking CXX static library libcpp_core.a
# [ 33%] Built target cpp_core_static
# [ 41%] Building CXX object CMakeFiles/cpp_core_py.dir/python_bindings/bindings.cpp.o
# [ 50%] Linking CXX shared module cpp_core.so
# [ 58%] Built target cpp_core_py
# [ 66%] Building CXX object CMakeFiles/test_subd_evaluator.dir/test_subd_evaluator.cpp.o
# [ 75%] Linking CXX executable test_subd_evaluator
# [100%] Built target test_subd_evaluator

# Verify build outputs
ls -lh libcpp_core.a cpp_core*.so test_subd_evaluator

# Expected files:
# libcpp_core.a          (~60 KB)  - Static library
# cpp_core.so           (~280 KB)  - Python module
# test_subd_evaluator    (~68 KB)  - Test executable
```

### Build Targets

CMake creates three targets:

1. **cpp_core_static** → `libcpp_core.a`
   - Static library with core geometry code
   - Used by Python module and test executable

2. **cpp_core_py** → `cpp_core.so` (or `.dylib` on macOS)
   - Python extension module
   - Import with `import cpp_core`

3. **test_subd_evaluator** → executable
   - C++ unit tests
   - Run with `./test_subd_evaluator`

### Build Specific Target

```bash
# Build only static library
make cpp_core_static

# Build only Python module
make cpp_core_py

# Build only tests
make test_subd_evaluator
```

### Clean Build

```bash
# Remove all build artifacts
cd cpp_core/build
rm -rf *

# Reconfigure and rebuild
cmake ..
make -j$(nproc)
```

### Build Configuration Options

#### Debug Build

```bash
cmake -DCMAKE_BUILD_TYPE=Debug ..
make -j$(nproc)

# Enables:
# - Debug symbols (-g)
# - No optimization (-O0)
# - Assertions enabled
```

#### Release Build (Default)

```bash
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)

# Enables:
# - Full optimization (-O3)
# - No debug symbols
# - Assertions disabled
```

#### Custom OpenSubdiv Location

```bash
# If OpenSubdiv installed in non-standard location
cmake -DCMAKE_PREFIX_PATH=/custom/path/to/opensubdiv ..
make -j$(nproc)
```

#### Verbose Build (See Full Commands)

```bash
make VERBOSE=1
```

---

## Python Package Installation

### Development Installation (Recommended)

**Editable install** - changes to Python code take effect immediately.

```bash
# From project root
cd /path/to/latent

# Activate virtual environment
source venv/bin/activate

# Install in development mode
pip install -e .

# This runs CMake build automatically and installs package
# C++ module will be available at: cpp_core/build/cpp_core.so
# Python app will be available as: from app import ...
```

### Production Installation

```bash
# From project root
cd /path/to/latent

# Activate virtual environment
source venv/bin/activate

# Install (not editable)
pip install .

# Builds C++ core and installs everything to site-packages
```

### Manual Python Module Build

```bash
# Build C++ extension without installing package
python3 setup.py build_ext --inplace

# Creates: cpp_core/build/cpp_core.so in project directory
```

---

## Verification

### 1. Verify C++ Build

```bash
cd cpp_core/build

# Check files exist
ls -lh libcpp_core.a cpp_core*.so test_subd_evaluator

# Check library symbols
nm libcpp_core.a | grep SubDEvaluator | head -5

# Expected output:
# 0000000000000000 T _ZN6latent13SubDEvaluator10initializeERKNS_15SubDControlCageE
# 0000000000000000 T _ZN6latent13SubDEvaluator10tessellateEib
# ...

# Run C++ tests
./test_subd_evaluator

# Expected output:
# Running C++ SubDEvaluator tests...
# Test 1: Create evaluator... PASSED
# Test 2: Initialize with cube... PASSED
# Test 3: Tessellation... PASSED
# Test 4: Limit evaluation... PASSED
# All tests passed!
```

### 2. Verify Python Import

```bash
# From project root
cd /path/to/latent

# Test import (add build path)
python3 << 'EOF'
import sys
sys.path.insert(0, 'cpp_core/build')
import cpp_core

print(f"✅ cpp_core imported successfully")
print(f"Available classes: {[x for x in dir(cpp_core) if not x.startswith('_')]}")

# Test basic functionality
cage = cpp_core.SubDControlCage()
print(f"✅ Created SubDControlCage: {cage}")

evaluator = cpp_core.SubDEvaluator()
print(f"✅ Created SubDEvaluator")

point = cpp_core.Point3D(1.0, 2.0, 3.0)
print(f"✅ Created Point3D: {point}")

print("\n🎉 All verification tests passed!")
EOF
```

**Expected Output:**
```
✅ cpp_core imported successfully
Available classes: ['Point3D', 'SubDControlCage', 'SubDEvaluator', 'TessellationResult']
✅ Created SubDControlCage: SubDControlCage(0 vertices, 0 faces)
✅ Created SubDEvaluator
✅ Created Point3D: Point3D(1.000000, 2.000000, 3.000000)

🎉 All verification tests passed!
```

### 3. Verify Integration Tests

```bash
# Run full integration test suite
cd /path/to/latent
python3 tests/test_day1_integration.py

# Expected output:
# ======================================================================
# Day 1 Integration Tests
# ======================================================================
# test_point3d ... ok
# test_control_cage ... ok
# test_subd_evaluator_initialization ... ok
# test_tessellation ... ok
# test_limit_evaluation ... ok
# test_create_mesh_actor ... ok
# test_create_control_cage_actor ... ok
# test_bounding_box ... ok
# test_server_availability ... ok
# test_fetch_geometry ... skipped (no server)
# test_metadata ... skipped (no server)
# test_full_pipeline ... skipped (no server)
#
# Ran 12 tests in 0.019s
# OK (skipped=3)
# ✅ ALL TESTS PASSED!
```

### 4. Verify Desktop Application

```bash
# Launch application
python3 launch.py

# Application should:
# ✅ Open main window
# ✅ Show 4 viewports (default layout)
# ✅ Display menus (File, Edit, Analysis, View, Help)
# ✅ Show status bar with "Disconnected" (no Rhino)

# Test geometry visualization:
# 1. Click View → Show Test Cube
# 2. Right-drag to orbit camera
# 3. Shift+Right-drag to pan
# 4. Mouse wheel to zoom

# If all works: build successful! ✅
```

---

## Troubleshooting

### CMake Can't Find OpenSubdiv

**Error:**
```
CMake Error: Could not find OpenSubdiv
```

**Solution 1: Install OpenSubdiv**
```bash
# macOS
brew install opensubdiv

# Ubuntu 22.04+
sudo apt-get install libosd-dev

# Or build from source (see Prerequisites)
```

**Solution 2: Specify OpenSubdiv Location**
```bash
# Find OpenSubdiv
find /usr -name "libosd*" 2>/dev/null
find /opt -name "libosd*" 2>/dev/null

# Tell CMake where to look
cmake -DCMAKE_PREFIX_PATH=/usr/local ..
# or
cmake -DCMAKE_PREFIX_PATH=/opt/homebrew ..
```

**Solution 3: Use pkg-config**
```bash
# Check if pkg-config can find it
pkg-config --modversion opensubdiv
pkg-config --cflags opensubdiv
pkg-config --libs opensubdiv

# If found, CMake should use pkg-config automatically
```

### CMake Can't Find pybind11

**Error:**
```
CMake Error: Could not find pybind11
```

**Solution:**
```bash
# Install pybind11
pip3 install pybind11

# Verify Python can find it
python3 -c "import pybind11; print(pybind11.get_cmake_dir())"

# If still fails, tell CMake explicitly
cmake -Dpybind11_DIR=$(python3 -c "import pybind11; print(pybind11.get_cmake_dir())") ..
```

### Python Module Import Fails

**Error:**
```python
ModuleNotFoundError: No module named 'cpp_core'
```

**Solution 1: Add Build Directory to Path**
```python
import sys
sys.path.insert(0, '/absolute/path/to/latent/cpp_core/build')
import cpp_core
```

**Solution 2: Install Package**
```bash
pip install -e .
```

**Solution 3: Check Module Exists**
```bash
ls cpp_core/build/cpp_core*.so

# If missing, rebuild
cd cpp_core/build
cmake ..
make cpp_core_py
```

### Symbol Undefined Errors

**Error:**
```
ImportError: undefined symbol: _ZN10OpenSubdiv5...
```

**Cause**: OpenSubdiv libraries not linked or not in library search path.

**Solution (Linux):**
```bash
# Find OpenSubdiv libraries
find /usr -name "libosd*.so*" 2>/dev/null

# Add to library path
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Update library cache
sudo ldconfig

# Rebuild module
cd cpp_core/build
rm -rf *
cmake ..
make -j$(nproc)
```

**Solution (macOS):**
```bash
# Find OpenSubdiv libraries
find /opt /usr -name "libosd*.dylib" 2>/dev/null

# Add to library path
export DYLD_LIBRARY_PATH=/usr/local/lib:$DYLD_LIBRARY_PATH
# or
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH

# Rebuild module
cd cpp_core/build
rm -rf *
cmake ..
make -j$(nproc)
```

### Position Independent Code Error

**Error:**
```
relocation R_X86_64_PC32 against symbol can not be used when making a shared object;
recompile with -fPIC
```

**Solution**: Already fixed in `CMakeLists.txt`. If you encounter this, update CMakeLists.txt:

```cmake
set_target_properties(cpp_core_static PROPERTIES
    OUTPUT_NAME cpp_core
    POSITION_INDEPENDENT_CODE ON  # Add this line
)
```

Then rebuild:
```bash
cd cpp_core/build
rm -rf *
cmake ..
make -j$(nproc)
```

### Qt Plugin Path Issues

**Error when launching app:**
```
qt.qpa.plugin: Could not find the Qt platform plugin "cocoa" in ""
```

**Solution**: Use `launch.py` instead of `main.py`:
```bash
# ✅ Correct
python3 launch.py

# ❌ May fail
python3 main.py
```

`launch.py` automatically configures Qt plugin paths.

### VTK Import Fails

**Error:**
```python
ModuleNotFoundError: No module named 'vtkmodules'
```

**Solution:**
```bash
# Install VTK
pip install vtk

# Verify
python3 -c "import vtk; print(vtk.VTK_VERSION)"

# If system package conflicts, use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install vtk
```

---

## Development Workflow

### Incremental C++ Changes

```bash
# After modifying C++ code:
cd cpp_core/build
make -j$(nproc)

# Python module automatically updated
# No need to reinstall Python package
```

### Adding New C++ Files

```cpp
// 1. Create new file: cpp_core/analysis/curvature.cpp

// 2. Update CMakeLists.txt:
add_library(cpp_core_static STATIC
    geometry/subd_evaluator.cpp
    utils/mesh_mapping.cpp
    analysis/curvature.cpp  # Add this
)

// 3. Rebuild
cd build
cmake ..
make -j$(nproc)
```

### Adding Python Bindings

```cpp
// Edit: cpp_core/python_bindings/bindings.cpp

PYBIND11_MODULE(cpp_core, m) {
    // ... existing bindings ...

    // Add new function
    m.def("new_function", &new_function,
          "Brief description",
          py::arg("param1"), py::arg("param2"));

    // Add new class
    py::class_<NewClass>(m, "NewClass")
        .def(py::init<>())
        .def("method", &NewClass::method);
}
```

Rebuild:
```bash
cd cpp_core/build
make cpp_core_py
```

Test in Python:
```python
import sys
sys.path.insert(0, 'cpp_core/build')
import cpp_core

result = cpp_core.new_function(arg1, arg2)
obj = cpp_core.NewClass()
```

### Running Tests During Development

```bash
# Quick C++ test
cd cpp_core/build
./test_subd_evaluator

# Quick Python test
python3 tests/test_day1_integration.py

# Full test suite
./tests/run_all_tests.sh
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  build-linux:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            build-essential \
            cmake \
            libosd-dev \
            python3.11 \
            python3.11-venv

      - name: Setup Python
        run: |
          python3.11 -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt

      - name: Build C++ core
        run: |
          cd cpp_core
          mkdir build && cd build
          cmake ..
          make -j$(nproc)

      - name: Run tests
        run: |
          source venv/bin/activate
          python3 tests/test_day1_integration.py

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: |
          brew install opensubdiv cmake python@3.12

      - name: Setup Python
        run: |
          python3.12 -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt

      - name: Build C++ core
        run: |
          cd cpp_core
          mkdir build && cd build
          cmake ..
          make -j$(sysctl -n hw.ncpu)

      - name: Run tests
        run: |
          source venv/bin/activate
          python3 tests/test_day1_integration.py
```

---

## Performance Notes

### Build Times

| Operation | Time | Notes |
|-----------|------|-------|
| **Clean build** | 2-5 min | First build, all files |
| **Incremental build** | 10-30s | After small change |
| **C++ only** | 1-2 min | `make cpp_core_static` |
| **Python bindings only** | 30s | `make cpp_core_py` |

### Optimization Levels

```bash
# Debug: No optimization, full symbols
cmake -DCMAKE_BUILD_TYPE=Debug ..
# Compilation: slower
# Runtime: 5-10x slower
# Debugging: easy

# Release: Full optimization, no symbols
cmake -DCMAKE_BUILD_TYPE=Release ..
# Compilation: faster
# Runtime: fastest
# Debugging: difficult

# RelWithDebInfo: Optimization + symbols
cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo ..
# Compilation: slower
# Runtime: fast (near Release)
# Debugging: possible but tricky
```

---

## Slash Command

For convenience, use the `/build-cpp` slash command:

```bash
/build-cpp
```

This command:
1. Navigates to `cpp_core/build`
2. Runs `cmake ..`
3. Runs `make -j$(nproc)`
4. Shows build status

---

## Summary Checklist

Before considering build complete, verify:

- [ ] CMake configuration succeeds without errors
- [ ] All three targets build: `libcpp_core.a`, `cpp_core.so`, `test_subd_evaluator`
- [ ] C++ tests pass: `./test_subd_evaluator`
- [ ] Python can import module: `import cpp_core`
- [ ] Integration tests pass: `python3 tests/test_day1_integration.py`
- [ ] Desktop app launches: `python3 launch.py`
- [ ] Test geometry displays in viewports

If all checked: **Build successful!** ✅

---

## Next Steps

After successful build:

1. **Run the application**: `python3 launch.py`
2. **Read API documentation**: `docs/API_REFERENCE.md`
3. **Explore examples**: `tests/test_day1_integration.py`
4. **Set up Rhino bridge**: `docs/RHINO_BRIDGE_SETUP.md`
5. **Review Phase 0 summary**: `docs/PHASE_0_COMPLETE.md`

---

## Getting Help

If you encounter issues not covered in troubleshooting:

1. Check existing build logs in `cpp_core/build/CMakeFiles/`
2. Verify all prerequisites are installed
3. Try clean build: `rm -rf cpp_core/build && mkdir cpp_core/build`
4. Check GitHub Issues for similar problems
5. Review `cpp_core/BUILD.md` for additional details

**Common Issue?** Please contribute to this document by submitting a pull request with the solution!

---

*Build Instructions v0.5.0*
*Phase 0 Complete - November 9, 2025*
*Ceramic Mold Analyzer Project*
