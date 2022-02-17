# WIP
A template for a Python extension module written in C++ that also works as a
standalone C++ library using `vcpkg` to manage dependencies.
## Setup
We will use CMake to build our project, and
[`vcpkg`](https://github.com/microsoft/vcpkg) to manage the dependencies.

### Install CMake ?
WIP ?

### [Install `vcpkg`](https://vcpkg.io/en/getting-started.html)

Navigate to where this repository is cloned and clone `vcpkg` there as a
submodule.
```
git clone https://github.com/Microsoft/vcpkg.git
```

Bootstrap it in Windows. Make sure you have [installed the
prerequisites](https://github.com/microsoft/vcpkg).
```
./vcpkg/bootstrap-vcpkg.bat
```

Or in Linux/MacOS. Make sure you have [installed developer
tools](https://github.com/microsoft/vcpkg)
```
./vcpkg/bootstrap-vcpkg.sh
```

## Development  
Test builds

```
python -m venv venv
```

On Windows
```
.\venv\Scripts\activate
```
otherwise
```
source ./venv/bin/activate
```

```
pip install setuptools wheel pybind11 cmake scikit-build
```

```
python setup.py install
```

```
python -c "import myproject; print(myproject.add(1, 2))"
```