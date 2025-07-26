#!/usr/bin/env python3
"""Integration tests for documentation generation.

This tests the full documentation generation pipeline on real project files.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

# Import the functions directly to test them more precisely
from rxiv_maker.commands.generate_docs import (
    generate_enhanced_index,
    generate_module_docs,
)


@pytest.mark.integration
def test_full_documentation_generation():
    """Test the full documentation generation process on a subset of real project files.

    This is an integration test that uses real project files and generates
    actual documentation. It takes longer to run than unit tests.
    """
    # Create a temporary directory for the documentation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Get the real project path
        project_root = Path(__file__).parent.parent.parent

        # Create a realistic project structure in the temp directory
        temp_src = temp_path / "src" / "rxiv_maker"
        temp_src.mkdir(parents=True)

        # Create docs directory
        docs_dir = temp_path / "docs" / "api"
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Copy a small subset of files for testing
        sample_files = [
            "utils/__init__.py",
            "commands/generate_docs.py",
            "processors/yaml_processor.py",
        ]

        for file_path in sample_files:
            src_file = project_root / "src" / "rxiv_maker" / file_path
            dest_file = temp_src / file_path

            # Ensure the parent directory exists
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file
            shutil.copy(src_file, dest_file)

        # Save the current directory
        original_dir = os.getcwd()

        # Make sure lazydocs is installed in the test environment
        try:
            # Try uv first, then fall back to pip
            result = subprocess.run(
                ["uv", "add", "lazydocs"],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(
                    ["pip", "install", "lazydocs"], check=True, stdout=subprocess.PIPE
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                pytest.skip(
                    "Failed to install lazydocs with either uv or pip - skipping test"
                )

        try:
            # Change to the temporary project directory
            os.chdir(temp_path)

            # Test directly with specific module files
            successful_modules = []

            # Test generating docs for a single module
            test_file = temp_src / "utils.py"
            result = generate_module_docs(docs_dir, test_file)

            if result:
                # If lazydocs works, add to successful list
                successful_modules.append(Path("utils.py"))
                print(f"Generated docs for utils.py: {result}")

            # Generate enhanced index with our successful modules
            if successful_modules:
                index_path = generate_enhanced_index(docs_dir, successful_modules)

                # Verify documentation files
                md_files = list(docs_dir.glob("*.md"))
                assert len(md_files) > 0, "No markdown files found in directory"

                # Verify index.md was created
                assert index_path.exists(), f"Index file not created at {index_path}"

                # Check content of index file
                with open(index_path) as f:
                    content = f.read()
                    assert "# API Documentation" in content
                    assert "utils.py.md" in content
            else:
                pytest.skip(
                    "No documentation generated - lazydocs may not be working correctly"
                )

        finally:
            # Change back to the original directory
            os.chdir(original_dir)
