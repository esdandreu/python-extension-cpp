import sys

from setuptools import find_packages
from pathlib import Path
from shutil import rmtree

try:
    from skbuild import setup
except ImportError:
    print(
        "Please update pip, you need pip 10 or greater,\n"
        " or you need to install the PEP 518 requirements in pyproject.toml yourself",
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
    raise RuntimeError(
        'Could not find `vcpkg`. Make sure to add it to this repository'
        )

setup(
    name="myproject",
    version="0.0.1",
    description="A minimal example package with pybind11 and vcpkg",
    author="Andreu Gimenez",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    cmake_install_dir="src/myproject",
    cmake_args=[f"-DCMAKE_TOOLCHAIN_FILE:PATH={VCPKG_CMAKE_TOOLCHAIN}"],
    include_package_data=True,
    extras_require={"test": ["pytest"]},
    python_requires=">=3.6",
)
