# Installing RUNTIME_DEPENDENCIES requires at least CMake version 3.21
cmake_minimum_required(VERSION 3.21)

set(CMAKE_CXX_STANDARD 17)

# vcpkg dependency manager
option(CMAKE_FETCH_VCPKG "Whether to fetch vcpkg if VCPKG_ROOT is not set." ON)

if(DEFINED CMAKE_TOOLCHAIN_FILE) # Print toolchain information
    message(STATUS "Using toolchain: ${CMAKE_TOOLCHAIN_FILE}")
elseif(NOT DEFINED CMAKE_PROJECT_NAME)
    if(DEFINED ENV{VCPKG_ROOT})
        message(STATUS "Using vcpkg installed in $ENV{VCPKG_ROOT}")
        set(CMAKE_TOOLCHAIN_FILE
            "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake"
            CACHE FILEPATH ""
        )
    elseif(CMAKE_FETCH_VCPKG)
        message(STATUS "Fetching vcpkg")
        include(FetchContent)
        FetchContent_Declare(vcpkg
            GIT_REPOSITORY https://github.com/microsoft/vcpkg/
            GIT_TAG 2022.09.27
        )
        FetchContent_MakeAvailable(vcpkg)
        set(CMAKE_TOOLCHAIN_FILE
            "${vcpkg_SOURCE_DIR}/scripts/buildsystems/vcpkg.cmake"
            CACHE FILEPATH ""
        )
        message(STATUS "Fetching vcpkg -- done")
    else()
        message(STATUS
            "Not using `vcpkg`. Consider setting CMAKE_FETCH_VCPKG=ON"
        )
    endif()
endif()

option(BUILD_TESTS "Build tests" ON)

if(BUILD_TESTS)
    list(APPEND VCPKG_MANIFEST_FEATURES "tests")
endif()

# Avoid specifying package name and version in multiple files by extracting
# them from `vcpkg.json` in the repository root.
file(READ ${CMAKE_SOURCE_DIR}/vcpkg.json vcpkg_json)
string(JSON PROJECT_NAME GET ${vcpkg_json} "name")
string(JSON VERSION_STRING GET ${vcpkg_json} "version-semver")
project(${PROJECT_NAME} VERSION ${VERSION_STRING} LANGUAGES CXX)

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
if(DEFINED SKBUILD)
    message(STATUS "Build Python API")

    message(STATUS "Python executable: ${PYTHON_EXECUTABLE}")

    # prevent an unused variable warning
    set(ignoreMe "${SKBUILD}")

    # call pybind11-config to obtain the root of the cmake package
    execute_process(COMMAND ${PYTHON_EXECUTABLE} -m pybind11 --cmakedir
        OUTPUT_VARIABLE pybind11_ROOT_RAW)
    string(STRIP ${pybind11_ROOT_RAW} pybind11_ROOT)
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

    # List `vcpkg` dependencies from VCPKG_INSTALLED_DIR so we can install them
    # together with the python API.
    file(GLOB VCPKG_DEPENDENCIES
        RELATIVE "${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/bin/"
        "${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/bin/*"
    )

    # Install the `vcpkg` dependencies that are used in our ${PROJECT_NAME}
    # library in the same DESTINATION as the python API. Note that it
    # only supports collecting the runtime dependencies for Windows, Linux and
    # macOS platforms.
    install(TARGETS ${PROJECT_PYTHON_API_NAME}
        RUNTIME_DEPENDENCIES
        PRE_INCLUDE_REGEXES ${VCPKG_DEPENDENCIES}
        PRE_EXCLUDE_REGEXES ".*"
        DESTINATION .
    )
endif()