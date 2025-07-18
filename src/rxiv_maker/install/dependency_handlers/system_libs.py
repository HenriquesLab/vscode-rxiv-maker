"""System libraries dependency handler."""

import subprocess
import sys

from ..utils.logging import InstallLogger


class SystemLibsHandler:
    """Handler for system libraries verification."""

    def __init__(self, logger: InstallLogger):
        """Initialize system libraries handler.

        Args:
            logger: Logger instance
        """
        self.logger = logger

    def verify_installation(self) -> bool:
        """Verify system libraries installation."""
        try:
            # Test key Python packages that depend on system libraries
            import matplotlib
            import numpy
            import pandas
            import PIL
            import scipy

            return True
        except ImportError as e:
            self.logger.debug(f"Missing Python package: {e}")
            return False

    def get_missing_packages(self) -> list[str]:
        """Get list of missing Python packages."""
        packages_to_check = ["matplotlib", "PIL", "numpy", "pandas", "scipy", "seaborn"]

        missing = []
        for package in packages_to_check:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)

        return missing

    def verify_build_tools(self) -> bool:
        """Verify build tools are available."""
        try:
            # Check for gcc/clang
            result = subprocess.run(
                ["gcc", "--version"], capture_output=True, timeout=10
            )

            if result.returncode != 0:
                # Try clang
                result = subprocess.run(
                    ["clang", "--version"], capture_output=True, timeout=10
                )

            return result.returncode == 0
        except:
            return False

    def get_python_version(self) -> str:
        """Get Python version."""
        version = sys.version_info
        return f"{version.major}.{version.minor}.{version.micro}"

    def check_python_compatibility(self) -> bool:
        """Check if Python version is compatible."""
        version = sys.version_info
        return version.major == 3 and version.minor >= 11
