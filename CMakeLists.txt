# Installing RUNTIME_DEPENDENCIES requires at least CMake version 3.21
cmake_minimum_required(VERSION 3.21)

# Compliler flags
set( CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -Wall --std=c++17 -O3 -fPIC" )
set( CMAKE_C_FLAGS  "${CMAKE_C_FLAGS} -Wall -O3 -fPIC" )

# Set CMake to use `vcpkg` to install dependencies. I avoids the need of
# passing it as an argument to `cmake`.
# https://github.com/microsoft/vcpkg/blob/master/docs/users/integration.md#using-an-environment-variable-instead-of-a-command-line-option
if (NOT DEFINED CMAKE_TOOLCHAIN_FILE)
    if(DEFINED ENV{VCPKG_ROOT})
        set(CMAKE_TOOLCHAIN_FILE 
            "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" CACHE STRING ""
        )
    elseif(EXISTS "${CMAKE_SOURCE_DIR}/vcpkg/scripts/buildsystems/vcpkg.cmake")
        set(CMAKE_TOOLCHAIN_FILE 
            "${CMAKE_SOURCE_DIR}/vcpkg/scripts/buildsystems/vcpkg.cmake"
            CACHE STRING ""
        )
    endif()
endif()
if (DEFINED CMAKE_TOOLCHAIN_FILE) # Print useful information
    message(STATUS "Using toolchain: ${CMAKE_TOOLCHAIN_FILE}")
else()
    message(STATUS "\
Not using `vcpkg`. Consider adding it to manage \
dependencies https://github.com/microsoft/vcpkg.git"
    )
endif()

# In order to avoid specifying package name and version in multiple files, we
# will use `vcpkg.json` in the repository root as reference and extract the
# apropiate variables from there.
file(READ ${CMAKE_SOURCE_DIR}/vcpkg.json vcpkg_json)
string(JSON PROJECT_NAME GET ${vcpkg_json} "name")
string(JSON VERSION_STRING GET ${vcpkg_json} "version-string")

project(${PROJECT_NAME} VERSION ${VERSION_STRING})

# It is recommended to split this file into multiple files and use
# `add_submodule` if it starts to grow too large.

# ------------------------- Build the project library -------------------------
# Recomended refactor into src/${PROJECT_NAME}/CMakeLists.txt

# It is important that the library is static in order to build its Python
# wrapper
find_package(FFTW3 CONFIG REQUIRED)

add_library(${PROJECT_NAME} STATIC 
    src/${PROJECT_NAME}/my_cpp_project.cpp
)

target_include_directories(${PROJECT_NAME} 
    PUBLIC
        src/${PROJECT_NAME}
)

target_link_libraries(${PROJECT_NAME} 
    PRIVATE
        FFTW3::fftw3
)

# ---------------------------- Build library tests ----------------------------
# Recomended refactor into tests/CMakeLists.txt

option(BUILD_TESTS "Build tests" ON)
if(BUILD_TESTS)
    message(STATUS "Build tests")
    find_package(GTest CONFIG REQUIRED)

    enable_testing()

    # Tests can be run with `ctest` or by directly running the test executable
    # that will be named as `${PROJECT_TESTS_NAME}`. The name of the executable
    # is not really relevant as `ctest` will find it anyway thanks to Google
    # Test.
    set(PROJECT_TESTS_NAME test_${PROJECT_NAME})

    # A possible extension here is to add all `.cpp` files under the `tests`
    # folder.
    add_executable(${PROJECT_TESTS_NAME} 
        tests/test_my_cpp_project.cpp
    )

    target_link_libraries(${PROJECT_TESTS_NAME} 
        PRIVATE
            ${PROJECT_NAME}
            GTest::gtest_main
    )

    include(GoogleTest)
    gtest_discover_tests(${PROJECT_TESTS_NAME})

endif()

# ----------------------------- Build python api ------------------------------
# Recomended refactor into src/python/CMakeLists.txt

# Option for building the project Python API, `setup.py` defines this variable
option(BUILD_PYTHON_API "Build Python API" OFF)
if(BUILD_PYTHON_API)
    message(STATUS "Build Python API")

    message(STATUS "Python executable: ${PYTHON_EXECUTABLE}")

    if(SKBUILD)
        # Scikit-Build does not add your site-packages to the search path
        # automatically, so we need to add the pybind11 specific directory
        # here.
        execute_process(
            COMMAND "${PYTHON_EXECUTABLE}" -c
                    "import pybind11; print(pybind11.get_cmake_dir())"
            OUTPUT_VARIABLE _tmp_dir
            OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ECHO STDOUT
        )
        list(APPEND CMAKE_PREFIX_PATH "${_tmp_dir}")
    endif()

    # Now we can find pybind11
    find_package(pybind11 CONFIG REQUIRED)

    # Take into account that this name should be consistent with the contents
    # of the `__init__.py` file and when calling PYBIND11_MODULE() in the
    # python API code. This could be avoided with some code generation but it
    # would be too complicated for this simple example.
    set(PROJECT_PYTHON_API_NAME _python_api)

    # This function behaves very much like CMake’s builtin `add_library`
    pybind11_add_module(${PROJECT_PYTHON_API_NAME} 
        MODULE 
            src/python/api.cpp
    )

    target_link_libraries(${PROJECT_PYTHON_API_NAME} 
        PRIVATE
            ${PROJECT_NAME}
    )

    target_compile_definitions(${PROJECT_PYTHON_API_NAME} 
        PRIVATE 
            VERSION_INFO=${PROJECT_VERSION}
    )

    # Extract the `vcpkg` dependencies from `vckpkg.json` so we can install
    # them together with the python API.
    string(JSON VCPKG_DEPENDENCIES_LENGTH LENGTH ${vcpkg_json} "dependencies")
    math(EXPR _LIMIT "${VCPKG_DEPENDENCIES_LENGTH} - 1")
    foreach(_IDX RANGE 0 ${_LIMIT})
        string(JSON VCPKG_DEPENDENCY GET ${vcpkg_json} "dependencies" ${_IDX})
        list(APPEND VCPKG_DEPENDENCIES ${VCPKG_DEPENDENCY})
    endforeach()

    # Install the `vcpkg` dependencies that are used in our ${PROJECT_NAME}
    # library in the same DESTINATION as the python API. Google Test and
    # `pybind11` are `vcpkg` dependencies but they are not used at runtime,
    # only when building and therefore they won't be installed. Note that it
    # only supports collecting the runtime dependencies for Windows, Linux and
    # macOS platforms.
    install(TARGETS ${PROJECT_PYTHON_API_NAME}
        RUNTIME_DEPENDENCIES 
            PRE_INCLUDE_REGEXES ${VCPKG_DEPENDENCIES}
            PRE_EXCLUDE_REGEXES ".*"
        DESTINATION .
    )
endif()