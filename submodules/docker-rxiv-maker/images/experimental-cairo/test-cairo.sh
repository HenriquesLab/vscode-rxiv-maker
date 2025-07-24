#!/bin/bash
# ======================================================================
# Rxiv-Maker Experimental Cairo Functionality Test Script
# ======================================================================
# This script tests Cairo/SVG processing capabilities in the experimental
# Docker image to ensure all enhancements are working correctly.
# ======================================================================

set -euo pipefail

# Color output functions
print_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

print_test() {
    echo -e "\033[1;36m[TEST]\033[0m $1"
}

# Test Cairo SVG to PNG conversion
test_cairo_svg_conversion() {
    print_test "Testing Cairo SVG to PNG conversion..."

    python3 -c "
import cairosvg
import io
from pathlib import Path

# Create test SVG with various elements
svg_content = '''<?xml version='1.0' encoding='UTF-8'?>
<svg width='400' height='200' xmlns='http://www.w3.org/2000/svg'>
  <defs>
    <linearGradient id='grad1' x1='0%' y1='0%' x2='100%' y2='0%'>
      <stop offset='0%' style='stop-color:rgb(255,255,0);stop-opacity:1' />
      <stop offset='100%' style='stop-color:rgb(255,0,0);stop-opacity:1' />
    </linearGradient>
  </defs>
  <rect width='400' height='200' fill='url(#grad1)' stroke='navy' stroke-width='2'/>
  <circle cx='100' cy='100' r='50' fill='lightblue' stroke='darkblue' stroke-width='3'/>
  <text x='200' y='50' text-anchor='middle' font-family='Liberation Sans' font-size='18' fill='darkred'>Cairo Test</text>
  <text x='200' y='100' text-anchor='middle' font-family='DejaVu Sans' font-size='14' fill='darkblue'>SVG Conversion</text>
  <path d='M 50 150 Q 100 120 150 150 T 250 150' stroke='green' stroke-width='3' fill='none'/>
</svg>'''

# Test SVG to PNG conversion
try:
    png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
    print(f'✓ SVG to PNG conversion successful ({len(png_data)} bytes)')
except Exception as e:
    print(f'✗ SVG to PNG conversion failed: {e}')
    exit(1)

# Test SVG to PDF conversion
try:
    pdf_data = cairosvg.svg2pdf(bytestring=svg_content.encode('utf-8'))
    print(f'✓ SVG to PDF conversion successful ({len(pdf_data)} bytes)')
except Exception as e:
    print(f'✗ SVG to PDF conversion failed: {e}')
    exit(1)
"

    if [[ $? -eq 0 ]]; then
        print_success "Cairo SVG conversion test passed"
    else
        print_error "Cairo SVG conversion test failed"
        return 1
    fi
}

# Test pycairo functionality
test_pycairo_functionality() {
    print_test "Testing pycairo direct functionality..."

    python3 -c "
import cairo
import math

# Create a simple PNG using pycairo
width, height = 200, 100
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
ctx = cairo.Context(surface)

# Draw background
ctx.set_source_rgb(0.9, 0.9, 1.0)
ctx.rectangle(0, 0, width, height)
ctx.fill()

# Draw circle
ctx.set_source_rgb(0.2, 0.6, 0.9)
ctx.arc(width/2, height/2, 30, 0, 2 * math.pi)
ctx.fill()

# Draw text
ctx.set_source_rgb(0.1, 0.1, 0.1)
ctx.select_font_face('Liberation Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
ctx.set_font_size(14)
ctx.move_to(width/2 - 35, height/2 + 5)
ctx.show_text('pycairo')

print('✓ pycairo direct drawing successful')
"

    if [[ $? -eq 0 ]]; then
        print_success "pycairo functionality test passed"
    else
        print_error "pycairo functionality test failed"
        return 1
    fi
}

# Test font availability
test_font_availability() {
    print_test "Testing font availability for Cairo..."

    python3 -c "
import subprocess
import re

# Get list of available fonts
try:
    result = subprocess.run(['fc-list'], capture_output=True, text=True, check=True)
    fonts = result.stdout

    # Check for key font families
    required_fonts = [
        'Liberation Sans',
        'DejaVu Sans',
        'Liberation Serif',
        'Liberation Mono',
        'Noto Color Emoji'
    ]

    found_fonts = []
    for font in required_fonts:
        if font.lower() in fonts.lower():
            found_fonts.append(font)
            print(f'✓ Found font: {font}')
        else:
            print(f'⚠ Missing font: {font}')

    print(f'\\n✓ Found {len(found_fonts)}/{len(required_fonts)} required fonts')

    # Count total fonts
    font_count = len([line for line in fonts.split('\\n') if line.strip()])
    print(f'✓ Total fonts available: {font_count}')

except subprocess.CalledProcessError as e:
    print(f'✗ Font check failed: {e}')
    exit(1)
"

    if [[ $? -eq 0 ]]; then
        print_success "Font availability test passed"
    else
        print_error "Font availability test failed"
        return 1
    fi
}

# Test SVG library integration
test_svg_libraries() {
    print_test "Testing SVG library integration..."

    python3 -c "
# Test svglib
try:
    from svglib.svglib import renderSVG
    from reportlab.graphics import renderPDF, renderPM
    print('✓ svglib import successful')
except ImportError as e:
    print(f'✗ svglib import failed: {e}')

# Test lxml for SVG parsing
try:
    from lxml import etree
    svg_text = '''<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'>
        <circle cx='50' cy='50' r='40' fill='red'/>
    </svg>'''
    root = etree.fromstring(svg_text.encode())
    print(f'✓ lxml SVG parsing successful (found {root.tag} element)')
except ImportError as e:
    print(f'✗ lxml import failed: {e}')
except Exception as e:
    print(f'✗ lxml SVG parsing failed: {e}')

# Test cssselect2 for CSS parsing
try:
    import cssselect2
    print('✓ cssselect2 import successful')
except ImportError as e:
    print(f'✗ cssselect2 import failed: {e}')

# Test tinycss2 for CSS parsing
try:
    import tinycss2
    print('✓ tinycss2 import successful')
except ImportError as e:
    print(f'✗ tinycss2 import failed: {e}')
"

    if [[ $? -eq 0 ]]; then
        print_success "SVG library integration test passed"
    else
        print_error "SVG library integration test failed"
        return 1
    fi
}

# Test Mermaid to SVG to PNG workflow
test_mermaid_cairo_workflow() {
    print_test "Testing Mermaid to SVG to PNG workflow..."

    # Create temporary directory
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"

    # Create test Mermaid diagram
    cat > test.mmd << 'EOF'
graph TD
    A[Start] --> B{Is Cairo working?}
    B -->|Yes| C[Convert SVG to PNG]
    B -->|No| D[Debug Cairo]
    C --> E[Success!]
    D --> B
EOF

    # Generate SVG with Mermaid
    if ! mmdc -i test.mmd -o test.svg -t default; then
        print_error "Mermaid SVG generation failed"
        cd - >/dev/null
        rm -rf "$temp_dir"
        return 1
    fi

    # Convert SVG to PNG using CairoSVG
    python3 -c "
import cairosvg
from pathlib import Path

svg_file = Path('test.svg')
if not svg_file.exists():
    print('✗ SVG file not found')
    exit(1)

svg_content = svg_file.read_text()
png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))

with open('test.png', 'wb') as f:
    f.write(png_data)

print(f'✓ Mermaid SVG converted to PNG ({len(png_data)} bytes)')
"

    local result=$?

    # Clean up
    cd - >/dev/null
    rm -rf "$temp_dir"

    if [[ $result -eq 0 ]]; then
        print_success "Mermaid to Cairo workflow test passed"
    else
        print_error "Mermaid to Cairo workflow test failed"
        return 1
    fi
}

# Test R Cairo integration
test_r_cairo_integration() {
    print_test "Testing R Cairo integration..."

    R --slave --no-restore << 'EOF'
# Test Cairo device in R
if (!require("Cairo", quietly = TRUE)) {
    cat("✗ Cairo package not available in R\n")
    quit(status = 1)
}

# Test basic Cairo PNG output
Cairo(width = 200, height = 100, file = "/tmp/test_r_cairo.png", type = "png", bg = "white")
plot(1:10, 1:10, main = "R Cairo Test", col = "blue", pch = 19)
dev.off()

if (file.exists("/tmp/test_r_cairo.png")) {
    cat("✓ R Cairo PNG generation successful\n")
    file.remove("/tmp/test_r_cairo.png")
} else {
    cat("✗ R Cairo PNG generation failed\n")
    quit(status = 1)
}

# Test svglite integration
if (require("svglite", quietly = TRUE)) {
    cat("✓ R svglite package available\n")
} else {
    cat("⚠ R svglite package not available\n")
}
EOF

    if [[ $? -eq 0 ]]; then
        print_success "R Cairo integration test passed"
    else
        print_error "R Cairo integration test failed"
        return 1
    fi
}

# Main test execution
main() {
    print_info "Starting Rxiv-Maker Experimental Cairo functionality tests..."
    echo ""

    local failed_tests=0

    # Run all tests
    test_cairo_svg_conversion || ((failed_tests++))
    echo ""

    test_pycairo_functionality || ((failed_tests++))
    echo ""

    test_font_availability || ((failed_tests++))
    echo ""

    test_svg_libraries || ((failed_tests++))
    echo ""

    test_mermaid_cairo_workflow || ((failed_tests++))
    echo ""

    test_r_cairo_integration || ((failed_tests++))
    echo ""

    # Summary
    if [[ $failed_tests -eq 0 ]]; then
        print_success "All Cairo functionality tests passed! ✨"
        print_info "The experimental Cairo image is ready for enhanced SVG processing."
    else
        print_error "$failed_tests test(s) failed"
        print_info "Please review the failed tests and fix issues before using the image."
        return 1
    fi
}

# Execute main function
main "$@"
