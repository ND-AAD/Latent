---
description: Build C++ core module and run tests
---

Build the C++ core geometry module and verify it's working correctly.

**Build Steps:**

1. Navigate to build directory:
   ```bash
   cd cpp_core/build || { echo "Error: cpp_core/build directory not found"; exit 1; }
   ```

2. Run CMake configuration:
   ```bash
   cmake ..
   ```

3. Build with all CPU cores:
   ```bash
   make -j$(sysctl -n hw.ncpu)
   ```

4. Run C++ unit tests (if available):
   ```bash
   ./test_subd_evaluator
   ```

5. Test Python module import:
   ```bash
   cd .. || exit 1
   python3 -c "import sys; sys.path.insert(0, 'build'); import cpp_core; print('✅ cpp_core module loads successfully')"
   ```

**Report:**
- Build output (successes/errors)
- Test results
- Any warnings or issues
- Confirmation that latent_core.so was created

**Success Criteria:**
- [ ] CMake configuration successful
- [ ] C++ code compiles without errors
- [ ] latent_core.so (or .dylib) created
- [ ] Unit tests pass
- [ ] Python can import module
