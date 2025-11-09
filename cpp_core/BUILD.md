# Building cpp_core C++ Extension

This document describes how to build the `cpp_core` C++ extension module.

## Prerequisites

### Required Dependencies

1. **CMake** (>= 3.20)
   ```bash
   # macOS
   brew install cmake

   # Ubuntu/Debian
   sudo apt-get install cmake

   # Or via pip
   pip3 install cmake
   ```

2. **OpenSubdiv** (3.6.0+)

   **macOS:**
   ```bash
   brew install opensubdiv
   ```

   **Linux (build from source):**
   ```bash
   # Install dependencies
   sudo apt-get install libglfw3-dev libxinerama-dev libxcursor-dev libxi-dev

   # Clone OpenSubdiv
   git clone https://github.com/PixarAnimationStudios/OpenSubdiv.git
   cd OpenSubdiv
   git checkout v3_6_0

   # Build and install
   mkdir build && cd build
   cmake -DCMAKE_BUILD_TYPE=Release \
         -DNO_EXAMPLES=ON \
         -DNO_TUTORIALS=ON \
         -DNO_REGRESSION=ON \
         -DNO_DOC=ON \
         -DNO_OMP=ON \
         -DNO_TBB=ON \
         -DNO_CUDA=ON \
         -DNO_OPENCL=ON \
         -DNO_GLFW=ON \
         ..
   make -j$(nproc)
   sudo make install
   ```

3. **pybind11** (2.11.0+)
   ```bash
   # Via pip (recommended)
   pip3 install pybind11

   # Or via package manager
   brew install pybind11  # macOS
   sudo apt-get install pybind11-dev  # Linux
   ```

4. **Python Development Headers** (3.11+)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-dev

   # macOS (usually included with Python installation)
   ```

### Optional Dependencies

- **Metal Framework** (macOS only) - Automatically detected and linked for GPU acceleration

## Building

### Method 1: Using CMake directly (Recommended for Development)

```bash
# Navigate to cpp_core directory
cd cpp_core

# Create build directory
mkdir build && cd build

# Configure with CMake
cmake ..

# Build (use all available CPU cores)
# macOS:
make -j$(sysctl -n hw.ncpu)

# Linux:
make -j$(nproc)

# Install (optional - copies to system directories)
sudo make install
```

**Build outputs:**
- `libcpp_core.a` - Static library
- `cpp_core.so` (Linux) or `cpp_core.dylib` (macOS) - Python module

### Method 2: Using setup.py (For Installation)

```bash
# From project root
cd /home/user/Latent

# Build in-place (for development)
python3 setup.py build_ext --inplace

# Or install system-wide
python3 setup.py install

# Or editable install (recommended for development)
pip3 install -e .
```

## Testing the Build

### Test 1: Verify Build Outputs

```bash
# Check that static library was created
ls -lh cpp_core/build/libcpp_core.a

# Check that Python module was created
ls -lh cpp_core/build/cpp_core*.so
```

### Test 2: Verify Static Library Symbols

```bash
# Check for expected symbols (SubDEvaluator class)
nm cpp_core/build/libcpp_core.a | grep SubDEvaluator | head -10

# Expected output should show SubDEvaluator methods:
# - initialize
# - tessellate
# - evaluate_limit_point
# etc.
```

### Test 3: Test Python Import

```bash
# Add build directory to Python path and import module
cd /home/user/Latent
python3 -c "import sys; sys.path.insert(0, 'cpp_core/build'); import cpp_core; print('✅ Import successful'); print('Version:', cpp_core.__version__)"

# Expected output:
# ✅ Import successful
# Version: 0.5.0
```

### Test 4: Check Python Module Contents

```bash
# List all exported symbols from Python module
python3 -c "import sys; sys.path.insert(0, 'cpp_core/build'); import cpp_core; print(dir(cpp_core))"

# Expected to see at least:
# - __version__
# - Point3D
# - SubDControlCage
# - SubDEvaluator
# - TessellationResult
```

## Common Build Issues

### Issue: OpenSubdiv not found

**Error:**
```
CMake Error: OpenSubdiv not found!
```

**Solution:**
1. Make sure OpenSubdiv is installed (see Prerequisites)
2. If installed in non-standard location, set CMAKE_PREFIX_PATH:
   ```bash
   cmake -DCMAKE_PREFIX_PATH=/path/to/opensubdiv/install ..
   ```

### Issue: pybind11 not found

**Error:**
```
CMake Error: pybind11 not found!
```

**Solution:**
1. Install pybind11 via pip: `pip3 install pybind11`
2. Or install via package manager (see Prerequisites)
3. Verify installation: `python3 -c "import pybind11; print(pybind11.get_cmake_dir())"`

### Issue: Python.h not found

**Error:**
```
fatal error: Python.h: No such file or directory
```

**Solution:**
Install Python development headers:
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev

# macOS
# Usually included, but if missing:
xcode-select --install
```

### Issue: Undefined symbols at link time

**Error:**
```
undefined reference to `OpenSubdiv::Far::TopologyRefiner::...`
```

**Solution:**
This usually means OpenSubdiv libraries aren't being linked properly. Check:
1. OpenSubdiv installation is complete
2. Libraries are in standard locations (/usr/local/lib)
3. Try setting LD_LIBRARY_PATH (Linux) or DYLD_LIBRARY_PATH (macOS)

### Issue: Metal framework not found (macOS)

**Warning:**
```
Could not find Metal framework
```

**Solution:**
This is only a performance optimization. If Metal isn't found:
1. Make sure you have Xcode Command Line Tools: `xcode-select --install`
2. Metal should be in `/System/Library/Frameworks/Metal.framework`
3. Build will work without Metal, just without GPU acceleration

## Build Configuration Options

### Debug vs Release Build

```bash
# Debug build (with symbols, no optimization)
cmake -DCMAKE_BUILD_TYPE=Debug ..

# Release build (optimized, no symbols) - DEFAULT
cmake -DCMAKE_BUILD_TYPE=Release ..
```

### Custom Install Prefix

```bash
# Install to custom location instead of /usr/local
cmake -DCMAKE_INSTALL_PREFIX=/custom/path ..
make install
```

### Verbose Build Output

```bash
# See full compiler commands
make VERBOSE=1
```

## Integration with Python Application

Once built, the `cpp_core` module can be imported in Python:

```python
# Add build directory to path (development)
import sys
sys.path.insert(0, 'cpp_core/build')

# Or if installed system-wide, just import directly
import cpp_core

# Use the module
print(f"cpp_core version: {cpp_core.__version__}")

# Create SubD control cage
cage = cpp_core.SubDControlCage()
cage.vertices = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
cage.faces = [[0, 1, 2, 3]]

# Initialize evaluator
evaluator = cpp_core.SubDEvaluator()
evaluator.initialize(cage)

# Tessellate for display
mesh = evaluator.tessellate(subdivision_level=3)
print(f"Generated {len(mesh.triangles) // 3} triangles")

# Evaluate exact limit surface point
point = evaluator.evaluate_limit_point(face_index=0, u=0.5, v=0.5)
print(f"Limit point: ({point.x}, {point.y}, {point.z})")
```

## Performance Notes

### Compilation Time

- First build: ~2-5 minutes (depending on CPU)
- Incremental rebuilds: ~10-30 seconds

### Runtime Performance

- OpenSubdiv with Metal (macOS): ~10-100x faster than CPU-only
- Tessellation: Typically <100ms for surfaces with <10K control vertices
- Limit point evaluation: ~1-10 microseconds per point

### Optimization Tips

1. **Use Release builds** for production (already default)
2. **Enable Metal** on macOS for GPU acceleration (automatic)
3. **Cache tessellation results** when possible
4. **Use adaptive subdivision** for large surfaces

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Install dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y cmake python3-dev pybind11-dev
    pip3 install pybind11

- name: Build OpenSubdiv
  run: |
    git clone https://github.com/PixarAnimationStudios/OpenSubdiv.git
    cd OpenSubdiv && mkdir build && cd build
    cmake -DCMAKE_BUILD_TYPE=Release -DNO_EXAMPLES=ON ..
    make -j$(nproc) && sudo make install

- name: Build cpp_core
  run: |
    cd cpp_core && mkdir build && cd build
    cmake .. && make -j$(nproc)

- name: Test
  run: |
    python3 -c "import sys; sys.path.insert(0, 'cpp_core/build'); import cpp_core"
```

## Next Steps

After successful build:

1. **Run tests**: See `tests/` directory for test suite
2. **Import in application**: Use `import cpp_core` in Python code
3. **Day 1 Integration**: Proceed with Day 1 evening agents (7-9)

## Support

For build issues:
1. Check this BUILD.md file
2. Review CMakeLists.txt for configuration details
3. Check Day 0 checklist in sprint documentation
4. Verify all prerequisites are installed

---

**Build system created by Agent 3 - Day 1 Morning**
