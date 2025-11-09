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
    message(STATUS "  GPU Library: ${OPENSUBDIV_GPU_LIBRARY}")
    set(OPENSUBDIV_INCLUDE_DIRS ${OPENSUBDIV_INCLUDE_DIR})
    set(OPENSUBDIV_LIBRARIES ${OPENSUBDIV_CPU_LIBRARY} ${OPENSUBDIV_GPU_LIBRARY})
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

# Core static library
add_library(cpp_core_static STATIC
    geometry/subd_evaluator.cpp
    utils/mesh_mapping.cpp
)

# Set output name to cpp_core (without _static suffix)
set_target_properties(cpp_core_static PROPERTIES OUTPUT_NAME cpp_core)

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

# Test executable
add_executable(test_subd_evaluator test_subd_evaluator.cpp)
target_link_libraries(test_subd_evaluator PRIVATE cpp_core_static)

# Install targets
install(TARGETS cpp_core_static ARCHIVE DESTINATION lib)
install(TARGETS cpp_core_py LIBRARY DESTINATION .)

message(STATUS "Configuration complete!")
message(STATUS "  Static library: libcpp_core.a")
message(STATUS "  Python module: cpp_core.so (or .pyd on Windows)")
message(STATUS "  Test executable: test_subd_evaluator")
