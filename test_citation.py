#!/usr/bin/env python3
"""Test citation conversion issue."""

from src.py.converters.citation_processor import convert_citations_to_latex

# Test the specific text that's causing issues
test_text = "The system also integrates Mermaid.js [@Mermaid2023_documentation] for generating diagrams"

print("Original text:")
print(test_text)
print("\nConverted text:")
print(convert_citations_to_latex(test_text))

# Test with just the citation
test_citation = "[@Mermaid2023_documentation]"
print(f"\nJust citation: {test_citation}")
print(f"Converted: {convert_citations_to_latex(test_citation)}")

# Test multiple citations
test_multiple = "[@Donoho2010;@Sandve2013_reproducible_research;@Wilson2014_software_carpentry]"
print(f"\nMultiple citations: {test_multiple}")
print(f"Converted: {convert_citations_to_latex(test_multiple)}")