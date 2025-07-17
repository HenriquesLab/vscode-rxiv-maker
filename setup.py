"""Setup script for rxiv-maker with automatic system dependency installation."""

import os
import platform
import sys
from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.install import install


class PostInstallCommand(install):
    """Custom install command that runs post-install hooks."""

    def run(self):
        """Run the installation."""
        # Run standard installation first
        install.run(self)

        # Check if system dependency installation should be skipped
        if self._should_skip_system_deps():
            print("🔄 Skipping system dependency installation")
            return

        # Run system dependency installation
        self._install_system_dependencies()

    def _should_skip_system_deps(self) -> bool:
        """Check if system dependency installation should be skipped."""
        # Check environment variables
        if os.environ.get("RXIV_SKIP_SYSTEM_DEPS", "").lower() in ("1", "true", "yes"):
            return True

        # Check for Docker environment
        if os.path.exists("/.dockerenv"):
            return True

        # Check for CI environment
        if os.environ.get("CI", "").lower() in ("1", "true", "yes"):
            return True

        # Check for virtual environment without system access
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            # In virtual environment - check if we can access system package managers
            if not self._has_system_access():
                return True

        return False

    def _has_system_access(self) -> bool:
        """Check if we have access to system package managers."""
        import shutil

        system_name = platform.system()

        if system_name == "Darwin":  # macOS
            return shutil.which("brew") is not None or os.access(
                "/usr/local/bin", os.W_OK
            )
        elif system_name == "Linux":
            return (
                shutil.which("apt") is not None
                or shutil.which("yum") is not None
                or shutil.which("dnf") is not None
                or shutil.which("pacman") is not None
            )
        elif system_name == "Windows":
            return (
                shutil.which("winget") is not None or shutil.which("choco") is not None
            )

        return False

    def _install_system_dependencies(self):
        """Install system dependencies."""
        try:
            print("🚀 Installing system dependencies...")
            print(
                "   This may take a few minutes and might require administrator privileges."
            )

            # Import and run the installation manager
            from rxiv_maker.install.manager import InstallManager

            # Determine installation mode
            install_mode = self._get_install_mode()

            # Create installation manager
            manager = InstallManager(mode=install_mode, verbose=True, interactive=True)

            # Run installation
            success = manager.install()

            if success:
                print("✅ System dependencies installed successfully!")
                print("   Run 'rxiv --check-installation' to verify your setup.")
            else:
                print("⚠️  Some system dependencies failed to install.")
                print("   rxiv-maker will still work with reduced functionality.")
                print(
                    "   Run 'python -m rxiv_maker.install.manager --repair' to fix issues."
                )

        except Exception as e:
            print(f"⚠️  Error during system dependency installation: {e}")
            print("   rxiv-maker Python package installed successfully.")
            print(
                "   Run 'python -m rxiv_maker.install.manager' to install system dependencies manually."
            )

    def _get_install_mode(self) -> "InstallMode":
        """Get installation mode from environment or arguments."""
        from rxiv_maker.install.manager import InstallMode

        # Check environment variable
        mode_env = os.environ.get("RXIV_INSTALL_MODE", "").lower()
        if mode_env == "minimal":
            return InstallMode.MINIMAL
        elif mode_env == "core":
            return InstallMode.CORE
        elif mode_env == "skip-system":
            return InstallMode.SKIP_SYSTEM

        # Check command line arguments
        if "--minimal" in sys.argv:
            return InstallMode.MINIMAL
        elif "--core" in sys.argv:
            return InstallMode.CORE
        elif "--no-system-deps" in sys.argv:
            return InstallMode.SKIP_SYSTEM

        # Default to full installation
        return InstallMode.FULL


def get_long_description():
    """Get long description from README."""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return ""


def get_version():
    """Get version from _version.py."""
    try:
        # Try to import version from installed package
        from rxiv_maker._version import __version__

        return __version__
    except ImportError:
        # Fallback version for development
        return "1.4.0.dev0"


# Define requirements
requirements = [
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "scipy>=1.10.0",
    "Pillow>=9.0.0",
    "pypdf>=3.0.0",
    "PyYAML>=6.0.0",
    "python-dotenv>=1.0.0",
    "crossref-commons>=0.0.7",
    "lazydocs>=0.4.8",
    "types-requests>=2.32.4.20250611",
    "pytest>=7.4.4",
    "ruff>=0.12.2",
    "pre-commit>=4.2.0",
    "folder2md4llms>=0.3.0",
    "click>=8.0.0",
    "rich>=13.0.0",
    "rich-click>=1.6.0",
    "typing-extensions>=4.0.0",
    "packaging>=21.0.0",
]

# Define optional requirements
extras_require = {
    "dev": [
        "pytest>=7.4,<8.0",
        "py>=1.11.0",
        "ruff>=0.8.0",
        "mypy>=1.0",
        "types-PyYAML>=6.0.0",
        "nox>=2023.0.0",
        "pytest-cov>=4.0",
        "coverage[toml]>=7.0",
        "pytest-notebook>=0.10.0",
        "nbstripout>=0.7.1",
        "pre-commit>=4.0.0",
        "lazydocs>=0.4.8",
    ],
    "minimal": requirements,  # Same as base requirements
    "full": requirements,  # Same as base requirements (system deps handled separately)
}

setup(
    name="rxiv-maker",
    version=get_version(),
    author="Rxiv-Maker Contributors",
    author_email="rxiv.maker@gmail.com",
    description="Automated LaTeX article generation with universal system dependency installation",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/henriqueslab/rxiv-maker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Text Processing :: Markup :: LaTeX",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "rxiv=rxiv_maker.cli:main",
            "rxiv-install-deps=rxiv_maker.install.manager:main",
        ],
    },
    cmdclass={
        "install": PostInstallCommand,
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "latex",
        "markdown",
        "scientific-writing",
        "publishing",
        "automation",
        "cli",
        "command-line",
        "system-dependencies",
    ],
    project_urls={
        "Bug Reports": "https://github.com/henriqueslab/rxiv-maker/issues",
        "Source": "https://github.com/henriqueslab/rxiv-maker",
        "Documentation": "https://github.com/henriqueslab/rxiv-maker#readme",
    },
)
