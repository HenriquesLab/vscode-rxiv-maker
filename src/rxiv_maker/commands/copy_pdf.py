"""Standalone script to copy PDF with custom filename.

This script can be called from the Makefile or other build systems.
"""

from ..processors.yaml_processor import extract_yaml_metadata
from ..utils import copy_pdf_to_manuscript_folder, find_manuscript_md


def copy_pdf_with_custom_filename(output_dir: str = "output") -> bool:
    """Copy PDF to manuscript directory with custom filename.

    Args:
        output_dir: Output directory containing MANUSCRIPT.pdf

    Returns:
        True if successful, False otherwise
    """
    try:
        # Find and parse the manuscript markdown
        manuscript_md = find_manuscript_md()

        print(f"Reading metadata from: {manuscript_md}")
        yaml_metadata = extract_yaml_metadata(manuscript_md)

        # Copy PDF with custom filename
        result = copy_pdf_to_manuscript_folder(output_dir, yaml_metadata)

        if result:
            print("PDF copying completed successfully!")
            return True
        else:
            print("PDF copying failed!")
            return False

    except Exception as e:
        import traceback

        print(f"Error: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False
