# Installing RUNTIME_DEPENDENCIES requires at least CMake version 3.21
cmake_minimum_required(VERSION 3.21)

# Set CMake to use `vcpkg` to install dependencies. I avoids the need of
# passing it as an argument to `cmake`.
# https://github.com/microsoft/vcpkg/blob/master/docs/users/integration.md#using-an-environment-variable-instead-of-a-command-line-option
if(DEFINED ENV{VCPKG_ROOT} AND NOT DEFINED CMAKE_TOOLCHAIN_FILE)
    set(CMAKE_TOOLCHAIN_FILE 
        "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" CACHE STRING ""
    )
endif()
if (DEFINED CMAKE_TOOLCHAIN_FILE) # Print useful information
    message(STATUS "Using toolchain: ${CMAKE_TOOLCHAIN_FILE}")
endif()

# TODO read vcpkg.json

project(myproject VERSION "0.0.1")


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

if(SKBUILD)
  # Scikit-Build does not add your site-packages to the search path
  # automatically, so we need to add it _or_ the pybind11 specific directory
  # here.
  execute_process(
    COMMAND "${PYTHON_EXECUTABLE}" -c
            "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE _tmp_dir
    OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ECHO STDOUT)
  list(APPEND CMAKE_PREFIX_PATH "${_tmp_dir}")
endif()

# Now we can find pybind11
find_package(pybind11 CONFIG REQUIRED)

# Take into account that this name should be consistent with the contents of
# the __init__.py file and when calling PYBIND11_MODULE() in the python API
# code. This could be avoided with some code generation but it would be too
# complicated for this simple example.
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

install(TARGETS ${PROJECT_PYTHON_API_NAME}
    RUNTIME_DEPENDENCY_SET _python_api_dependencies
    DESTINATION .
)

# Install our library dependencies in the same DESTINATION as the python API.
# Note that it only supports collecting the runtime dependencies for Windows,
# Linux and macOS platforms
install (RUNTIME_DEPENDENCY_SET _python_api_dependencies
    PRE_INCLUDE_REGEXES "fftw3"
    PRE_EXCLUDE_REGEXES ".*"
    DESTINATION .
)