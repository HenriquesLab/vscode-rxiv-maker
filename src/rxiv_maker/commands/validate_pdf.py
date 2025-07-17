#!/usr/bin/env python3
"""Command-line tool for PDF validation.

This script validates PDF output quality by extracting text and checking
for common issues like unresolved citations, malformed equations, and
missing references.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from validators.pdf_validator import PDFValidator, ValidationLevel


def main():
    """Main entry point for PDF validation command."""
    parser = argparse.ArgumentParser(description="Validate PDF output quality")
    parser.add_argument("manuscript_path", help="Path to manuscript directory")
    parser.add_argument("--pdf-path", help="Path to PDF file (optional)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--detailed", "-d", action="store_true", help="Detailed output with statistics"
    )

    args = parser.parse_args()

    try:
        # Create validator
        validator = PDFValidator(args.manuscript_path, args.pdf_path)

        # Run validation
        result = validator.validate()

        # Display results
        if args.detailed:
            print(f"\nPDF Validation Results for {args.manuscript_path}")
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

                if args.verbose:
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
        if args.detailed and result.metadata:
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
        if args.detailed:
            print("\n📋 Summary:")
            print(f"   Errors: {error_count}")
            print(f"   Warnings: {warning_count}")
            print(f"   Success: {success_count}")

        # Exit with appropriate code
        return 1 if error_count > 0 else 0

    except Exception as e:
        print(f"❌ PDF validation failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
