# Installing RUNTIME_DEPENDENCIES requires at least CMake version 3.21
cmake_minimum_required(VERSION 3.21)

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

message(STATUS "CMAKE Python Libdir: ${CMAKE_INSTALL_PYTHON_LIBDIR}")
message(STATUS "CMAKE Install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "CMAKE Install libdir: ${CMAKE_INSTALL_LIBDIR}")
message(STATUS "project binary dir: ${myproject_BINARY_DIR}")

# In order to avoid specifying package name and version in multiple files, we
# will use `vcpkg.json` in the repository root as reference and extract the
# apropiate variables from there.
file(READ ${CMAKE_SOURCE_DIR}/vcpkg.json vcpkg_json)
string(JSON PROJECT_NAME GET ${vcpkg_json} "name")
string(JSON VERSION_STRING GET ${vcpkg_json} "version-string")
# Additionally, we will extract the `vcpkg` dependencies from `vckpkg.json` so
# we can install them in together with the python API.
string(JSON VCPKG_DEPENDENCIES_LENGTH LENGTH ${vcpkg_json} "dependencies")
math(EXPR _LIMIT "${VCPKG_DEPENDENCIES_LENGTH} - 1")
foreach(_IDX RANGE 0 ${_LIMIT})
    string(JSON VCPKG_DEPENDENCY GET ${vcpkg_json} "dependencies" ${_IDX})
    list(APPEND VCPKG_DEPENDENCIES ${VCPKG_DEPENDENCY})
endforeach()

project(${PROJECT_NAME} VERSION ${VERSION_STRING})

# It is recommended to split this file into multiple files and use
# `add_submodule` if it starts to grow too large.

# ------------------------- Build the project library -------------------------
# Recomended refactor into src/${PROJECT_NAME}/CMakeLists.txt

# It is important that the library is static in order to build its Python
# wrapper
find_package(FFTW3 CONFIG REQUIRED)

add_library(${PROJECT_NAME} STATIC 
    src/${PROJECT_NAME}/myproject.cpp
)

target_include_directories(${PROJECT_NAME} 
    PUBLIC
        src/${PROJECT_NAME}
)

target_link_libraries(${PROJECT_NAME} 
    PRIVATE
        FFTW3::fftw3
)

# ----------------------------- Build python api ------------------------------
# Recomended refactor into src/python/CMakeLists.txt

# Option for building the project Python API, `setup.py` defines this variable
option(BUILD_PYTHON_API "Build the python API" OFF)
if(BUILD_PYTHON_API)
    message(STATUS "Build Python API")

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

    # Install the `vcpkg` dependencies in the same DESTINATION as the python
    # API. Note that it only supports collecting the runtime dependencies for
    # Windows, Linux and macOS platforms.
    install(TARGETS ${PROJECT_PYTHON_API_NAME}
        RUNTIME_DEPENDENCIES 
            PRE_INCLUDE_REGEXES ${VCPKG_DEPENDENCIES}
            PRE_EXCLUDE_REGEXES ".*"
        DESTINATION .
    )

    # The extension module must load the hello library as a dependency when the
    # extension module is loaded. The easiest way to locate the hello library
    # is via RPATH. Absolute RPATHs are possible, but they make the resulting
    # binaries not redistributable to other Python installations (conda is
    # broke, wheel reuse is broke, and more!).
    #
    # Placing the python API in the package and using relative RPATHs that
    # doesn't point outside of the package means that the built package is
    # relocatable. This allows for safe binary redistribution.
    # if(APPLE)
    #     set_target_properties(${PROJECT_PYTHON_API_NAME} PROPERTIES 
    #         INSTALL_RPATH "@loader_path/${CMAKE_INSTALL_LIBDIR}"
    #     )
    # else()
    #     set_target_properties(${PROJECT_PYTHON_API_NAME} PROPERTIES 
    #         INSTALL_RPATH "$ORIGIN/${CMAKE_INSTALL_LIBDIR}"
    #     )
    # endif()
endif()