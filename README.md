# Python C++ extension
A template for a standalone C++ library with dependencies managed by
[vcpkg](https://github.com/microsoft/vcpkg) accessible through Python using
[pybind11](https://github.com/pybind/pybind11).

## Why should I use this template?
- You want to write a C++ library that can be accessed through Python.
- You want to use `cmake` to build your C++ code.
- You want to use `pybind11` to expose your C++ library as a Python module.
- You want to use some C++ dependencies and manage them with `vcpkg`. Otherwise
  you should check other [scikit-build sample
  projects](https://github.com/scikit-build/scikit-build-sample-projects).
- You are not specially concerned about build and install optimizations, it is
  not a problem if they are long running.

If you want to distribute your extension using `pip` or `conda` and you mind
that your users take a long time to install it, then it might be better to
distribute some built binaries instead of optimizing the build process. This
template might still be useful for you as it has a
[release](.github/workflows/release.yml) workflow for building python wheels
with [cibuildwheel](https://github.com/pypa/cibuildwheel) and distributing them
to [PyPI](https://pypi.org/).

## Example usage

### Create a clean Python virtual environment
```
python -m venv venv
```
Activate it on Windows
```
.\venv\Scripts\activate
```
otherwise
```
source ./venv/bin/activate
```

### Install this project
```
pip install git+https://github.com/esdandreu/python-extension-cpp
```
It will take a while to build as it will build the C++ dependencies as well,
but it will work. It is definitely not the most optimal way of installing a
package as we are installing as well the `vcpkg` package manager and building
from source dependencies that might as well be installed on the system. But
this allows a fast development environment where adding or removing C++
dependencies should be easy.

Alternatively, you can install the package from the binaries distributed in [PyPI](https://pypi.org/project/example-python-extension-cpp/).
```
pip install example-python-extension-cpp
```

### Test that the C++ code is working in the Python package
Our simple project contains a `add` function that adds two numbers together.
```
python -c "import my_python_api; print(my_python_api.add(1, 2))"
```

It also makes use of the C++ library
[fftw3](https://github.com/FFTW/fftw3.git) that is available through `vcpkg`
in order to perform a Fast Fourier Transform over a generated signal, printing
its results.
```
python -c "import my_python_api; my_python_api.hello_fft()"
```

## Setup
### Install the requirements
Install [vcpkg](https://github.com/microsoft/vcpkg) requirements with the
addition of `cmake` and Python. It could be summarized as:
- [git](https://git-scm.com/downloads)
- Build tools ([Visual
  Studio](https://docs.microsoft.com/en-us/visualstudio/install/install-visual-studio)
  on Windows or `gcc` on Linux for example)
- [cmake](#cmake)
- Python. Make sure to have development tools installed (`python3.X-dev` on
  Linux, being `X` your version of Python).

If running on a clean linux environment (like a container or Windows Subsystem
for Linux) you will need to install some additional tools as it is stated in
`vcpkg`.
```
sudo apt-get install build-essential curl zip unzip tar pkg-config libssl-dev python3-dev
```
#### CMake
Follow the [official instructions](https://cmake.org/install/).

The required `cmake` version is quite high, if you are using a Linux
distribution and installing `cmake` from the repositories take into account
that they might not be updated to the latest version. However there are options
to [install the latest version of `cmake` from the command
line](https://askubuntu.com/a/865294).

Make sure that when you run `cmake --version` the output is `3.21` or higher.
The reason for this is that we are using some of the `3.21` features to install
runtime dependencies (managed with `vcpkg`) together with our project so they
are available to Python when using its API.

#### Formatters
This project uses `clang-format` to format the C++ code. There is a
`.clang-format` file with options that I personally like. Download
`clang-format` as part of `LLVM` from the official [release
page](https://github.com/llvm/llvm-project/releases).

I als recommend using `yapf` to format python code.

### Clone this repository with `vcpkg`

Cone this repository with `vcpkg` as a submodule and navigate into it.
```
git clone --recursive git@github.com:esdandreu/python-extension-cpp.git
cd python-extension-cpp
```

Bootstrap `vcpkg` in Windows. Make sure you have [installed the
prerequisites](https://github.com/microsoft/vcpkg).
```
.\vcpkg\bootstrap-vcpkg.bat
```

Or in Linux/MacOS. Make sure you have [installed developer
tools](https://github.com/microsoft/vcpkg)
```
./vcpkg/bootstrap-vcpkg.sh
```

## Building

### Build locally with CMake
Navigate to the root of the repository and create a build directory.
```
mkdir build
```

Configure `cmake` to use `vcpkg`.
```
cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE="$pwd/vcpkg/scripts/buildsystems/vcpkg.cmake"
```

Build the project.
```
cmake --build build
```
### Build locally with Python

It is recommended to use a [clean virtual
environment](#create-a-clean-python-virtual-environment).

`scikit-build` is required before running the installer, as it is the package
that takes care of the installation. The rest of dependencies will be installed
automatically.

```
pip install scikit-build git
```

Install the repository. By adding `[test]` to our install command we can
install additionally the test dependencies.
```
pip install .[test]
```


## Testing

### Test the C++ library with Google Test

```
ctest --test-dir build
```

### Test the python extension

```
pytest
```

## CI/CD

This template contains a continuous integration workflow that builds and tests
the C++ library and the python extension
[test.yml](.github/workflows/test.yml).

It also contains a continuous deployment workflow that builds wheels and source
distributions for the python extension, then creates a github release with it
and uploads it to [PyPI](https://pypi.org/). That workflow is activated when
pushing a version tag to the repository:
```
git tag -a v0.0.1 -m "First release"
git push origin --tags
```