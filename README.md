# Python C++ extension
A template for a standalone C++ library with dependencies managed by
[vcpkg](https://github.com/microsoft/vcpkg) accessible through Python using
[pybind11](https://github.com/pybind/pybind11).

## Why should I use this template?
- You want to write a C++ library that can be accessed through Python.
- You want to use `cmake` to build your C++ code.
- You want to use some C++ dependencies and manage them with `vcpkg`. Otherwise
  you should check other [scikit-build sample
  projects](https://github.com/scikit-build/scikit-build-sample-projects).
- You are not specially concerned about build and install optimizations, it is
  not a problem if they are long running.

If you want to distribute your extension using `pip` or `conda` and you mind
that your users take a long time to install it, then it might be better to
build some binaries instead of optimizing the build process. This template
might still be useful for you but you should extend it with
[cuibuildwheel](https://github.com/pypa/cibuildwheel).

## Requirements
Similarly to [`vcpkg`](https://github.com/microsoft/vcpkg) with the addition of
`cmake`:
- [git](https://git-scm.com/downloads)
- Build tools (Visual Studio on Windows or `gcc` on Linux for example)
- [cmake](https://cmake.org/download/)

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

### Test that the C++ code is working
Our simple project contains a `add` function that adds two numbers together.
```
python -c "import myproject; print(myproject.add(1, 2))"
```

It also makes use of the C++ library
[fftw3](https://github.com/FFTW/fftw3.git) that is available through `vcpkg`
in order to perform a Fast Fourier Transform over a generated signal, printing
its results.
```
python -c "import myproject; myproject.hello_fft()"
```

## Setup
### Install CMake
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

### [Add `vcpkg` to the repository](https://vcpkg.io/en/getting-started.html)

Navigate to where this repository is cloned and clone `vcpkg` there.
```
git clone https://github.com/Microsoft/vcpkg.git
```

Bootstrap it in Windows. Make sure you have [installed the
prerequisites](https://github.com/microsoft/vcpkg).
```
.\vcpkg\bootstrap-vcpkg.bat
```

Or in Linux/MacOS. Make sure you have [installed developer
tools](https://github.com/microsoft/vcpkg)
```
./vcpkg/bootstrap-vcpkg.sh
```

### Test building locally with Python

It is recommended to use a clean virtual environment

Install the required Python build dependencies

```
pip install setuptools wheel pybind11 cmake scikit-build GitPython
```

```
python setup.py install
```
