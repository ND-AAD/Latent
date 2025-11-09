cmake_minimum_required(VERSION 3.20)

# Google Test Integration
include(FetchContent)
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG release-1.12.1
)

# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

# Enable testing
enable_testing()

# Helper function to add a test
function(add_cpp_test TEST_NAME)
    add_executable(${TEST_NAME} ${TEST_NAME}.cpp)
    target_link_libraries(${TEST_NAME}
        PRIVATE
        cpp_core_static
        GTest::gtest_main
    )
    # Add to CTest
    add_test(NAME ${TEST_NAME} COMMAND ${TEST_NAME})
endfunction()

# Add all test executables
add_cpp_test(test_subd_evaluator)
add_cpp_test(test_curvature)
add_cpp_test(test_constraints)

# Add NURBS tests only if OpenCASCADE is available
if(OpenCASCADE_FOUND)
    add_cpp_test(test_nurbs)
endif()

# Discover all tests for CTest integration
include(GoogleTest)
gtest_discover_tests(test_subd_evaluator)
gtest_discover_tests(test_curvature)
gtest_discover_tests(test_constraints)

if(OpenCASCADE_FOUND)
    gtest_discover_tests(test_nurbs)
endif()

message(STATUS "Configured C++ unit tests with Google Test")
