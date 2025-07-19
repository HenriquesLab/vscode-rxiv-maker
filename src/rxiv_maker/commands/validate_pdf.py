"""Command-line tool for PDF validation.

This script validates PDF output quality by extracting text and checking
for common issues like unresolved citations, malformed equations, and
missing references.
"""

import os
import sys

# Add the parent directory to the path to allow imports when run as a script
if __name__ == "__main__":
    sys.path.insert(
        0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

from rxiv_maker.validators.pdf_validator import PDFValidator, ValidationLevel


def validate_pdf_output(
    manuscript_path: str,
    pdf_path: str = None,
    verbose: bool = False,
    detailed: bool = False,
) -> int:
    """Validate PDF output quality.

    Args:
        manuscript_path: Path to manuscript directory
        pdf_path: Path to PDF file (optional)
        verbose: Enable verbose output
        detailed: Enable detailed output with statistics

    Returns:
        0 if successful, 1 if errors found
    """
    try:
        # Create validator
        validator = PDFValidator(manuscript_path, pdf_path)

        # Run validation
        result = validator.validate()

        # Display results
        if detailed:
            print(f"\nPDF Validation Results for {manuscript_path}")
            print("=" * 60)

        # Count issues by level
        error_count = sum(1 for e in result.errors if e.level == ValidationLevel.ERROR)
        warning_count = sum(
            1 for e in result.errors if e.level == ValidationLevel.WARNING
        )
        success_count = sum(
            1 for e in result.errors if e.level == ValidationLevel.SUCCESS
        )

        # Print errors and warnings
        if result.errors:
            for error in result.errors:
                if error.level == ValidationLevel.ERROR:
                    print(f"❌ ERROR: {error.message}")
                elif error.level == ValidationLevel.WARNING:
                    print(f"⚠️  WARNING: {error.message}")
                elif error.level == ValidationLevel.SUCCESS:
                    print(f"✅ SUCCESS: {error.message}")
                elif error.level == ValidationLevel.INFO:
                    print(f"ℹ️  INFO: {error.message}")

                if verbose:
                    if error.context:
                        print(f"   Context: {error.context}")
                    if error.suggestion:
                        print(f"   Suggestion: {error.suggestion}")
                    if error.file_path:
                        print(f"   File: {error.file_path}")
                    if error.line_number:
                        print(f"   Line: {error.line_number}")
                    print()

        # Print statistics if detailed mode
        if detailed and result.metadata:
            print("\n📊 PDF Statistics:")
            print("-" * 30)
            for key, value in result.metadata.items():
                if key == "pdf_file":
                    print(f"📄 PDF File: {value}")
                elif key == "total_pages":
                    print(f"📑 Total Pages: {value}")
                elif key == "total_words":
                    print(f"📝 Total Words: {value}")
                elif key == "citations_found":
                    print(f"📚 Citations Found: {value}")
                elif key == "figure_references":
                    print(f"🖼️  Figure References: {value}")
                elif key == "table_references":
                    print(f"📊 Table References: {value}")
                elif key == "equation_references":
                    print(f"🔢 Equation References: {value}")
                elif key == "section_references":
                    print(f"📖 Section References: {value}")
                elif (
                    key.startswith("avg_")
                    or key.startswith("min_")
                    or key.startswith("max_")
                ):
                    print(f"📏 {key.replace('_', ' ').title()}: {value:.0f}")

        # Summary
        if detailed:
            print("\n📋 Summary:")
            print(f"   Errors: {error_count}")
            print(f"   Warnings: {warning_count}")
            print(f"   Success: {success_count}")

        # Exit with appropriate code
        return 1 if error_count > 0 else 0

    except Exception as e:
        print(f"❌ PDF validation failed: {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        return 1
