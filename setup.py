"""
Setup script for Ceramic Mold Analyzer with C++ extension module.

This builds the cpp_core C++ extension using CMake and makes it available
for Python import.

Usage:
    python3 setup.py build_ext --inplace  # Build in-place for development
    python3 setup.py install                # Install system-wide
    pip3 install -e .                       # Editable install
"""

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
import subprocess
import os
import sys
import platform


class CMakeExtension(Extension):
    """Extension class that indicates this extension should be built with CMake."""

    def __init__(self, name, sourcedir=''):
        super().__init__(name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    """Custom build_ext command that builds C++ extensions using CMake."""

    def run(self):
        # Check that CMake is available
        try:
            subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the C++ extension. "
                "Install it via 'pip install cmake' or your system package manager."
            )

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        """Build a single C++ extension using CMake."""
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        # Create build directory
        build_dir = os.path.join(ext.sourcedir, 'build')
        os.makedirs(build_dir, exist_ok=True)

        # CMake configuration arguments
        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DPYTHON_EXECUTABLE={sys.executable}',
        ]

        # Platform-specific configuration
        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        # Determine number of parallel build jobs
        if platform.system() == "Darwin":
            # macOS
            try:
                cpu_count = int(subprocess.check_output(['sysctl', '-n', 'hw.ncpu']).decode().strip())
            except:
                cpu_count = 4
        else:
            # Linux and others
            try:
                cpu_count = os.cpu_count() or 4
            except:
                cpu_count = 4

        build_args += ['--', f'-j{cpu_count}']

        cmake_args += [f'-DCMAKE_BUILD_TYPE={cfg}']

        # Run CMake configuration
        print(f"Configuring CMake in {build_dir}...")
        subprocess.check_call(
            ['cmake', ext.sourcedir] + cmake_args,
            cwd=build_dir
        )

        # Run CMake build
        print(f"Building C++ extension with {cpu_count} parallel jobs...")
        subprocess.check_call(
            ['cmake', '--build', '.'] + build_args,
            cwd=build_dir
        )

        print("C++ extension built successfully!")


# Read long description from README if available
long_description = ""
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()

# Read requirements from requirements.txt if available
requirements = []
requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
if os.path.exists(requirements_path):
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="ceramic_mold_analyzer",
    version="0.5.0",
    author="Ceramic Mold Analyzer Team",
    description="Desktop application for discovering mathematical decompositions of SubD surfaces for ceramic molds",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ceramic-mold-analyzer",

    # Python packages
    packages=find_packages(include=['app', 'app.*']),

    # C++ extension
    ext_modules=[CMakeExtension('cpp_core', sourcedir='cpp_core')],
    cmdclass={"build_ext": CMakeBuild},

    # Dependencies
    install_requires=requirements,
    python_requires=">=3.11",

    # Entry points
    entry_points={
        'console_scripts': [
            'ceramic-mold-analyzer=main:main',
        ],
    },

    # Classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Visualization",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
    ],

    # Include package data
    include_package_data=True,
    zip_safe=False,
)
