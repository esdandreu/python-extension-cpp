from gettext import find
import json
import sys

from setuptools import find_packages
from pathlib import Path
from shutil import rmtree

try:
    from skbuild import setup
except ImportError:
    print(
        "Please update pip, you need pip 10 or greater,\n or you need to "
        "install the PEP 518 requirements in pyproject.toml yourself",
        file=sys.stderr,
    )
    raise

PROJECT_SOURCE_DIR = Path(__file__).parent

# For some reason, running this file twice in a row causes the build to fail:
# fatal error C1083: Cannot open include file: 'io.h'
# Therefore the workaround is to clean the `_skbuild` directory before running
SKBUILD_DIR = PROJECT_SOURCE_DIR / "_skbuild"
if SKBUILD_DIR.exists():
    print(f'Removing previous installation: {SKBUILD_DIR}')
    rmtree(str(SKBUILD_DIR))

# Make sure that `vcpkg` package manager is available as a submodule
VCPKG_DIR = PROJECT_SOURCE_DIR / "vcpkg"
VCPKG_CMAKE_TOOLCHAIN = VCPKG_DIR / "scripts" / "buildsystems" / "vcpkg.cmake"
if not VCPKG_CMAKE_TOOLCHAIN.is_file():
    from git import Git
    print("Cloning `vcpkg`...")
    vcpkg = Git(PROJECT_SOURCE_DIR).clone('https://github.com/microsoft/vcpkg')

# In order to avoid specifying package name and version in multiple files, we
# will use `vcpkg.json` in the repository root as reference and extract the
# apropiate variables from there.
with open(PROJECT_SOURCE_DIR / "vcpkg.json") as f:
    vcpkg_json = json.load(f)
    # Required
    PROJECT_NAME = vcpkg_json["name"]
    PROJECT_VERSION_STRING = vcpkg_json["version-string"]

setup(
    # Python package information, can be edited
    name=PROJECT_NAME,
    version=PROJECT_VERSION_STRING,
    description="A minimal C++ extension using pybind11 and vcpkg",
    author="Andreu Gimenez",
    license="MIT",
    # All Python code that is placed in `src/python` will be available to be
    # imported as `import $PROJECT_NAME`
    # ! if `src/python` or its `__init__.py` is refactored, the following 
    # ! arguments should be modified accordingly
    packages=[PROJECT_NAME],
    package_dir={PROJECT_NAME: str(PROJECT_SOURCE_DIR / "src" / "python")},
    # package_dir={PROJECT_NAME: "src/python"},
    cmake_install_dir=PROJECT_NAME,
    # CMake must be used allways, otherwise C++ dependencies won't be installed
    cmake_with_sdist=True, 
    # Signal cmake to use `vcpkg`
    cmake_args=[
        f"-DCMAKE_TOOLCHAIN_FILE:PATH={str(VCPKG_CMAKE_TOOLCHAIN.resolve())}",
        "-DBUILD_PYTHON_API=ON",
        ],
    # Extra setuptools keywords:
    # https://setuptools.pypa.io/en/latest/userguide/keywords.html
    python_requires=">=3.7",
    # tests_require=["pytest"], # ! Is it needed?
)
