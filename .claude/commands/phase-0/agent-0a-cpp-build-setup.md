# Agent 0A: C++ Build System Setup

## Objective

Configure CMake to build a shared library with C bindings for P/Invoke compatibility.

## Working Directory

`/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Read First

- `cpp_core/CMakeLists.txt` - understand current build configuration
- `CLAUDE.md` - project principles (especially lossless architecture)

## Files to Modify

1. `cpp_core/CMakeLists.txt` - add shared library target

## Files to Create

1. `cpp_core/c_bindings/CMakeLists.txt` - build config for C bindings
2. `cpp_core/c_bindings/exports.h` - export macro definitions

## Tasks

### 1. Update Main CMakeLists.txt

Add shared library target alongside existing static library:

```cmake
# Shared library for P/Invoke (Rhino plugin)
add_library(latent_core SHARED
    ${GEOMETRY_SOURCES}
    ${ANALYSIS_SOURCES}
    ${CONSTRAINTS_SOURCES}
)

# Platform-specific export settings
if(WIN32)
    target_compile_definitions(latent_core PRIVATE LATENT_EXPORTS)
endif()

# Include c_bindings subdirectory
add_subdirectory(c_bindings)
```

### 2. Create exports.h

```cpp
// cpp_core/c_bindings/exports.h
#ifndef LATENT_EXPORTS_H
#define LATENT_EXPORTS_H

#ifdef _WIN32
    #ifdef LATENT_EXPORTS
        #define LATENT_API __declspec(dllexport)
    #else
        #define LATENT_API __declspec(dllimport)
    #endif
#else
    #define LATENT_API __attribute__((visibility("default")))
#endif

#endif // LATENT_EXPORTS_H
```

### 3. Create c_bindings/CMakeLists.txt

```cmake
# cpp_core/c_bindings/CMakeLists.txt

# C bindings will be added in Phase 1
# This file sets up the directory structure

set(C_BINDINGS_SOURCES
    # rhino_wrapper.cpp will be added by Agent 1C
)

# For now, just ensure the directory is recognized
message(STATUS "C bindings directory configured")
```

### 4. Set Installation Rules

Add to main CMakeLists.txt:

```cmake
# Installation rules for shared library
install(TARGETS latent_core
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(FILES c_bindings/exports.h
    DESTINATION include/latent
)
```

## Success Criteria

- [ ] `cmake ..` configures without errors
- [ ] `make` produces both `libcpp_core.a` and `liblatent_core.dylib` (or `.dll` on Windows)
- [ ] `exports.h` exists with correct platform macros
- [ ] No build warnings related to visibility/exports

## Verification Commands

```bash
cd cpp_core/build
cmake ..
make -j4

# Verify outputs
ls -la libcpp_core.a
ls -la liblatent_core.dylib  # or .dll on Windows

# Verify exports header
cat ../c_bindings/exports.h | grep LATENT_API
```

## Do Not Modify

- Any files in `geometry/`, `analysis/`, or `constraints/` directories
- Python bindings in `python_bindings/`
- Existing test files

## Skills to Use

- `superpowers:verification-before-completion` - verify build before reporting done

## Report

When complete, provide:
1. CMake configuration output (key lines)
2. List of generated library files with sizes
3. Any platform-specific notes
