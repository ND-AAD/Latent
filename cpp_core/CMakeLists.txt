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

message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")

# Add common install prefixes to search path
set(CMAKE_PREFIX_PATH
    ${CMAKE_PREFIX_PATH}
    "/usr/local"
    "/opt/local"
    "$ENV{HOME}/.local"
)

# Try manual search for OpenSubdiv first (to avoid broken system configs)
message(STATUS "Searching for OpenSubdiv...")

# Check for headers
find_path(OPENSUBDIV_INCLUDE_DIR
    NAMES opensubdiv/far/topologyRefiner.h
    PATHS /usr/include /usr/local/include
)

# Check for libraries
find_library(OPENSUBDIV_CPU_LIBRARY
    NAMES osdCPU
    PATHS /usr/lib /usr/local/lib /usr/lib/x86_64-linux-gnu
)

find_library(OPENSUBDIV_GPU_LIBRARY
    NAMES osdGPU
    PATHS /usr/lib /usr/local/lib /usr/lib/x86_64-linux-gnu
)

if(OPENSUBDIV_INCLUDE_DIR AND OPENSUBDIV_CPU_LIBRARY)
    message(STATUS "Found OpenSubdiv via manual search")
    message(STATUS "  Include: ${OPENSUBDIV_INCLUDE_DIR}")
    message(STATUS "  CPU Library: ${OPENSUBDIV_CPU_LIBRARY}")

    set(OPENSUBDIV_INCLUDE_DIRS ${OPENSUBDIV_INCLUDE_DIR})
    set(OPENSUBDIV_LIBRARIES ${OPENSUBDIV_CPU_LIBRARY})

    if(OPENSUBDIV_GPU_LIBRARY)
        message(STATUS "  GPU Library: ${OPENSUBDIV_GPU_LIBRARY}")
        list(APPEND OPENSUBDIV_LIBRARIES ${OPENSUBDIV_GPU_LIBRARY})
    else()
        message(STATUS "  GPU Library: Not found (CPU only)")
    endif()

    set(OPENSUBDIV_FOUND TRUE)
    set(OpenSubdiv_FOUND TRUE)  # Set both variables for compatibility
else()
    message(FATAL_ERROR
        "OpenSubdiv not found!\n"
        "Please install OpenSubdiv:\n"
        "  - On macOS: brew install opensubdiv\n"
        "  - On Linux: apt-get install libosd-dev\n"
        "  - Or build from source (see Day 0 checklist)\n"
        "  - Or set CMAKE_PREFIX_PATH to OpenSubdiv install directory"
    )
endif()

# Try to find pybind11
find_package(pybind11 QUIET)

if(NOT pybind11_FOUND)
    # Try to find it via Python
    execute_process(
        COMMAND python3 -c "import pybind11; print(pybind11.get_cmake_dir())"
        OUTPUT_VARIABLE PYBIND11_CMAKE_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
    )

    if(PYBIND11_CMAKE_DIR)
        message(STATUS "Found pybind11 via Python: ${PYBIND11_CMAKE_DIR}")
        list(APPEND CMAKE_PREFIX_PATH ${PYBIND11_CMAKE_DIR})
        find_package(pybind11 REQUIRED)
    else()
        message(FATAL_ERROR
            "pybind11 not found!\n"
            "Please install pybind11:\n"
            "  - pip3 install pybind11\n"
            "  - Or: brew install pybind11 (macOS)\n"
            "  - Or: apt install pybind11-dev (Linux)"
        )
    endif()
endif()

message(STATUS "Found pybind11: ${pybind11_VERSION}")

# Try to find OpenCASCADE
find_package(OpenCASCADE QUIET)

if(OpenCASCADE_FOUND)
    message(STATUS "Found OpenCASCADE via find_package")
    message(STATUS "  Include: ${OpenCASCADE_INCLUDE_DIR}")
    message(STATUS "  Library: ${OpenCASCADE_LIBRARY_DIR}")

    # Set up include directories
    set(OPENCASCADE_INCLUDE_DIRS ${OpenCASCADE_INCLUDE_DIR})

    # Find all required OpenCASCADE libraries
    set(OCCT_LIBS TKernel TKMath TKG2d TKG3d TKGeomBase TKBRep TKGeomAlgo
                  TKTopAlgo TKPrim TKBO TKBool TKOffset TKHLR TKFillet)

    foreach(LIB ${OCCT_LIBS})
        find_library(OPENCASCADE_${LIB}_LIBRARY
            NAMES ${LIB}
            PATHS ${OpenCASCADE_LIBRARY_DIR} /usr/lib /usr/local/lib /usr/lib/x86_64-linux-gnu
            NO_DEFAULT_PATH
        )
        if(OPENCASCADE_${LIB}_LIBRARY)
            list(APPEND OPENCASCADE_LIBRARIES ${OPENCASCADE_${LIB}_LIBRARY})
        else()
            message(STATUS "  Warning: ${LIB} not found")
        endif()
    endforeach()

    message(STATUS "  Found ${OPENCASCADE_LIBRARIES}")
else()
    # Try manual search for OpenCASCADE
    find_path(OPENCASCADE_INCLUDE_DIR
        NAMES Standard_Version.hxx
        PATHS /usr/include/opencascade /usr/local/include/opencascade
    )

    find_library(OPENCASCADE_TKernel_LIBRARY
        NAMES TKernel
        PATHS /usr/lib /usr/local/lib /usr/lib/x86_64-linux-gnu
    )

    if(OPENCASCADE_INCLUDE_DIR AND OPENCASCADE_TKernel_LIBRARY)
        message(STATUS "Found OpenCASCADE via manual search")
        message(STATUS "  Include: ${OPENCASCADE_INCLUDE_DIR}")

        set(OPENCASCADE_INCLUDE_DIRS ${OPENCASCADE_INCLUDE_DIR})

        # Find all required OpenCASCADE libraries
        set(OCCT_LIBS TKernel TKMath TKG2d TKG3d TKGeomBase TKBRep TKGeomAlgo
                      TKTopAlgo TKPrim TKBO TKBool TKOffset TKHLR TKFillet)

        foreach(LIB ${OCCT_LIBS})
            find_library(OPENCASCADE_${LIB}_LIBRARY
                NAMES ${LIB}
                PATHS /usr/lib /usr/local/lib /usr/lib/x86_64-linux-gnu
            )
            if(OPENCASCADE_${LIB}_LIBRARY)
                list(APPEND OPENCASCADE_LIBRARIES ${OPENCASCADE_${LIB}_LIBRARY})
            endif()
        endforeach()

        set(OpenCASCADE_FOUND TRUE)
        message(STATUS "  Found ${OPENCASCADE_LIBRARIES} OpenCASCADE libraries")
    else()
        message(WARNING
            "OpenCASCADE not found - NURBS mold generation features will be disabled!\n"
            "Please install OpenCASCADE:\n"
            "  - On macOS: brew install opencascade\n"
            "  - On Linux: apt-get install libocct-*-dev\n"
            "  - Or build from source"
        )
    endif()
endif()

# Core static library
add_library(cpp_core_static STATIC
    geometry/subd_evaluator.cpp
    utils/mesh_mapping.cpp
    analysis/curvature_analyzer.cpp
    constraints/constraint_report.cpp
    constraints/constraint_validator.cpp
    constraints/draft_checker.cpp
    constraints/undercut_detector.cpp
)

# Add NURBS generator sources if OpenCASCADE is available
if(OpenCASCADE_FOUND)
    target_sources(cpp_core_static PRIVATE
        geometry/nurbs_fitting.cpp
        geometry/draft_transform.cpp
        geometry/mold_solid.cpp
    )
    target_compile_definitions(cpp_core_static PUBLIC HAVE_OPENCASCADE)
endif()

# Set output name to cpp_core (without _static suffix)
# Enable Position Independent Code for linking into shared library
set_target_properties(cpp_core_static PROPERTIES
    OUTPUT_NAME cpp_core
    POSITION_INDEPENDENT_CODE ON
)

target_include_directories(cpp_core_static PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# Link OpenSubdiv
if(OpenSubdiv_FOUND)
    target_include_directories(cpp_core_static PUBLIC ${OPENSUBDIV_INCLUDE_DIR})
    target_link_libraries(cpp_core_static PUBLIC ${OPENSUBDIV_LIBRARIES})
else()
    target_include_directories(cpp_core_static PUBLIC ${OPENSUBDIV_INCLUDE_DIRS})
    target_link_libraries(cpp_core_static PUBLIC ${OPENSUBDIV_LIBRARIES})
endif()

# Link OpenCASCADE if found
if(OpenCASCADE_FOUND)
    target_include_directories(cpp_core_static PUBLIC ${OPENCASCADE_INCLUDE_DIRS})
    target_link_libraries(cpp_core_static PUBLIC ${OPENCASCADE_LIBRARIES})
endif()

# Enable Metal on macOS
if(APPLE)
    message(STATUS "Enabling Metal backend for OpenSubdiv")
    target_compile_definitions(cpp_core_static PUBLIC OPENSUBDIV_HAS_METAL)
    # Link Metal framework on macOS
    find_library(METAL_LIBRARY Metal)
    if(METAL_LIBRARY)
        target_link_libraries(cpp_core_static PUBLIC ${METAL_LIBRARY})
        message(STATUS "Linked Metal framework: ${METAL_LIBRARY}")
    endif()
endif()

# Python module
pybind11_add_module(cpp_core_py python_bindings/bindings.cpp)

# Link the Python module to the static library
target_link_libraries(cpp_core_py PRIVATE cpp_core_static)

# Set output name to cpp_core (Python import name)
set_target_properties(cpp_core_py PROPERTIES OUTPUT_NAME cpp_core)

# Standalone test executables (legacy - use BUILD_TESTS=OFF if using Google Test)
option(BUILD_STANDALONE_TESTS "Build standalone test executables" OFF)
if(BUILD_STANDALONE_TESTS)
    add_executable(test_subd_evaluator_standalone test_subd_evaluator.cpp)
    target_link_libraries(test_subd_evaluator_standalone PRIVATE cpp_core_static)

    add_executable(test_limit_evaluation test_limit_evaluation.cpp)
    target_link_libraries(test_limit_evaluation PRIVATE cpp_core_static)

    add_executable(test_curvature_standalone test_curvature.cpp)
    target_link_libraries(test_curvature_standalone PRIVATE cpp_core_static)

    add_executable(test_validator_header test_validator_header.cpp)
    target_link_libraries(test_validator_header PRIVATE cpp_core_static)

    add_executable(test_draft_checker test_draft_checker.cpp)
    target_link_libraries(test_draft_checker PRIVATE cpp_core_static)

    # Add NURBS tests if OpenCASCADE is available
    if(OpenCASCADE_FOUND)
        add_executable(test_nurbs_fitting test_nurbs_fitting.cpp)
        target_link_libraries(test_nurbs_fitting PRIVATE cpp_core_static)

        add_executable(test_mold_solid test_mold_solid.cpp)
        target_link_libraries(test_mold_solid PRIVATE cpp_core_static)

        add_executable(test_draft_transform test_draft_transform.cpp)
        target_link_libraries(test_draft_transform PRIVATE cpp_core_static)

        # Standalone draft test (no dependencies on other modules)
        add_executable(test_draft_simple test_draft_simple.cpp)
        target_link_libraries(test_draft_simple PRIVATE ${OPENCASCADE_LIBRARIES})
        target_include_directories(test_draft_simple PRIVATE ${OPENCASCADE_INCLUDE_DIRS})
    endif()
endif()

# Install targets
install(TARGETS cpp_core_static ARCHIVE DESTINATION lib)
install(TARGETS cpp_core_py LIBRARY DESTINATION .)

# Enable testing with Google Test
option(BUILD_TESTS "Build unit tests" ON)
if(BUILD_TESTS)
    add_subdirectory(tests)
endif()

message(STATUS "Configuration complete!")
message(STATUS "  Static library: libcpp_core.a")
message(STATUS "  Python module: cpp_core.so (or .pyd on Windows)")
message(STATUS "  Test executable: test_subd_evaluator")
if(BUILD_TESTS)
    message(STATUS "  Unit tests: Enabled (use -DBUILD_TESTS=OFF to disable)")
endif()
