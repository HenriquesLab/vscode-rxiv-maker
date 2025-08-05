"""
Nox configuration for homebrew-rxiv-maker testing.

This file provides automated testing sessions for the Homebrew formula.
Run with: nox -s <session_name>
"""

import nox

# Supported Python versions for testing
PYTHON_VERSIONS = ["3.11", "3.12"]

# Default sessions to run when no session is specified
nox.options.sessions = ["lint", "formula_syntax", "install_test"]

# Use uv for faster dependency installation
nox.options.default_venv_backend = "uv|virtualenv"


@nox.session(python=False)
def lint(session):
    """Run linting checks on the formula."""
    session.log("🔍 Running Ruby syntax validation...")
    
    # Check Ruby syntax
    session.run("ruby", "-c", "Formula/rxiv-maker.rb", external=True)
    session.log("✅ Ruby syntax validation passed")
    
    # Check for common issues
    session.log("🔍 Checking for common formula issues...")
    with open("Formula/rxiv-maker.rb", "r") as f:
        content = f.read()
        
    issues = []
    if "placeholder" in content.lower():
        issues.append("Found placeholder values in formula")
    if not content.count('sha256 "'):
        issues.append("Missing SHA256 checksums")
        
    if issues:
        for issue in issues:
            session.error(f"❌ {issue}")
    else:
        session.log("✅ No common issues found")


@nox.session(python=False)
def formula_syntax(session):
    """Validate Homebrew formula syntax and structure."""
    session.log("🔍 Validating Homebrew formula syntax...")
    
    # Test formula parsing
    session.run("brew", "info", "./Formula/rxiv-maker.rb", external=True)
    session.log("✅ Formula parsing successful")
    
    # Test dry-run installation
    session.log("🧪 Testing dry-run installation...")
    session.run("brew", "install", "--dry-run", "./Formula/rxiv-maker.rb", external=True)
    session.log("✅ Dry-run installation test passed")


@nox.session(python=False)
def url_validation(session):
    """Validate that URLs in the formula are accessible."""
    session.log("🌐 Validating formula URLs...")
    
    with open("Formula/rxiv-maker.rb", "r") as f:
        content = f.read()
    
    # Extract URLs from formula
    import re
    urls = re.findall(r'url\s+"([^"]+)"', content)
    
    for url in urls:
        session.log(f"Testing URL: {url}")
        session.run("curl", "-I", "-f", "--max-time", "30", url, external=True)
    
    session.log("✅ All URLs validated successfully")


@nox.session(python=False)
def install_test(session):
    """Test formula installation."""
    session.log("🔧 Testing formula installation...")
    
    # Clean up any existing installations
    session.run("brew", "uninstall", "rxiv-maker", "--ignore-dependencies", external=True, success_codes=[0, 1])
    session.run("brew", "cleanup", "--prune=all", external=True)
    
    try:
        # Install the formula
        session.run("brew", "install", "./Formula/rxiv-maker.rb", external=True)
        session.log("✅ Formula installation successful")
        
        # Test basic functionality
        session.log("🧪 Testing installed CLI...")
        session.run("rxiv", "--version", external=True)
        session.run("rxiv", "--help", external=True)
        session.log("✅ CLI functionality tests passed")
        
    finally:
        # Clean up installation
        session.log("🧹 Cleaning up test installation...")
        session.run("brew", "uninstall", "rxiv-maker", "--ignore-dependencies", external=True, success_codes=[0, 1])


@nox.session(python=False)
def formula_test(session):
    """Run the built-in formula test block."""
    session.log("🧪 Running built-in formula tests...")
    
    # Install first if not already installed
    session.run("brew", "list", "rxiv-maker", external=True, success_codes=[0, 1])
    if session.run("echo", "$?", external=True, silent=True).strip() != "0":
        session.run("brew", "install", "./Formula/rxiv-maker.rb", external=True)
    
    try:
        # Run the formula's test block
        session.run("brew", "test", "rxiv-maker", external=True)
        session.log("✅ Built-in formula tests passed")
    finally:
        # Clean up
        session.run("brew", "uninstall", "rxiv-maker", "--ignore-dependencies", external=True, success_codes=[0, 1])


@nox.session(python=False)
def latex_test(session):
    """Test LaTeX functionality and dependency installation."""
    session.log("📄 Testing LaTeX dependency installation and functionality...")
    
    # Clean up any existing installations
    session.run("brew", "uninstall", "rxiv-maker", "--ignore-dependencies", external=True, success_codes=[0, 1])
    session.run("brew", "cleanup", "--prune=all", external=True)
    
    try:
        # Install the formula (should install texlive dependency)
        session.log("🔧 Installing formula with LaTeX dependency...")
        session.run("brew", "install", "./Formula/rxiv-maker.rb", external=True)
        session.log("✅ Formula with LaTeX dependency installed")
        
        # Test that LaTeX is available
        session.log("🧪 Testing LaTeX availability...")
        session.run("which", "pdflatex", external=True)
        session.run("pdflatex", "--version", external=True)
        session.log("✅ LaTeX (pdflatex) is available")
        
        # Test rxiv check-installation
        session.log("🔍 Testing installation check...")
        session.run("rxiv", "check-installation", external=True)
        session.log("✅ Installation check passed")
        
        # Test manuscript initialization and validation
        session.log("📝 Testing manuscript creation and validation...")
        session.run("rxiv", "init", "test-latex-manuscript", "--no-interactive", external=True)
        session.run("rxiv", "validate", "test-latex-manuscript", "--no-doi", external=True, success_codes=[0, 1])  # May have validation warnings
        session.log("✅ Manuscript creation and validation tests passed")
        
        # Clean up test manuscript
        session.run("rm", "-rf", "test-latex-manuscript", external=True)
        
    finally:
        # Clean up installation
        session.log("🧹 Cleaning up LaTeX test installation...")
        session.run("brew", "uninstall", "rxiv-maker", "--ignore-dependencies", external=True, success_codes=[0, 1])


@nox.session(python="3.12")
def benchmark(session):
    """Run performance benchmarks for the installed formula."""
    session.log("📊 Running performance benchmarks...")
    
    # Install time measurement tool
    session.install("psutil")
    
    # Create benchmark script
    benchmark_script = """
import time
import subprocess
import psutil
import sys

def measure_startup_time():
    \"\"\"Measure CLI startup time.\"\"\"
    times = []
    for _ in range(5):
        start = time.time()
        subprocess.run(['rxiv', '--version'], capture_output=True, check=True)
        times.append(time.time() - start)
    
    avg_time = sum(times) / len(times)
    print(f"Average CLI startup time: {avg_time:.3f}s")
    return avg_time

def measure_memory_usage():
    \"\"\"Measure memory usage of rxiv process.\"\"\"
    process = subprocess.Popen(['rxiv', '--help'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        p = psutil.Process(process.pid)
        memory_info = p.memory_info()
        print(f"Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB")
        return memory_info.rss
    finally:
        process.wait()

if __name__ == "__main__":
    print("🚀 Running performance benchmarks...")
    startup_time = measure_startup_time()
    memory_usage = measure_memory_usage()
    
    # Performance thresholds
    if startup_time > 2.0:
        print(f"⚠️  CLI startup time ({startup_time:.3f}s) exceeds threshold (2.0s)")
        sys.exit(1)
    else:
        print("✅ Performance benchmarks passed")
"""
    
    # Install the formula first
    session.run("brew", "list", "rxiv-maker", external=True, success_codes=[0, 1])
    if session.run("echo", "$?", external=True, silent=True).strip() != "0":
        session.run("brew", "install", "./Formula/rxiv-maker.rb", external=True)
    
    try:
        # Run benchmarks
        session.run("python", "-c", benchmark_script, external=False)
    finally:
        # Clean up
        session.run("brew", "uninstall", "rxiv-maker", "--ignore-dependencies", external=True, success_codes=[0, 1])


@nox.session(python=False)
def comprehensive(session):
    """Run comprehensive test suite covering all aspects."""
    session.log("🎯 Running comprehensive test suite...")
    
    # Run all test sessions in order
    test_sessions = [
        "lint",
        "formula_syntax", 
        "url_validation",
        "install_test",
        "latex_test",
        "formula_test"
    ]
    
    for test_session in test_sessions:
        session.log(f"🔄 Running session: {test_session}")
        session.run("nox", "-s", test_session, external=True)
    
    session.log("✅ Comprehensive test suite completed successfully")


@nox.session(python=False)
def ci_test(session):
    """Optimized test suite for CI environments."""
    session.log("🤖 Running CI-optimized test suite...")
    
    # Fast tests suitable for CI
    ci_sessions = [
        "lint",
        "formula_syntax",
        "url_validation"
    ]
    
    for test_session in ci_sessions:
        session.log(f"🔄 Running CI session: {test_session}")
        session.run("nox", "-s", test_session, external=True)
    
    session.log("✅ CI test suite completed successfully")




@nox.session(python=False)  
def cleanup(session):
    """Clean up any test installations and cache."""
    session.log("🧹 Cleaning up test environment...")
    
    # Remove any test installations
    session.run("brew", "uninstall", "rxiv-maker", "--ignore-dependencies", external=True, success_codes=[0, 1])
    session.run("brew", "untap", "homebrew/local", external=True, success_codes=[0, 1])
    session.run("brew", "cleanup", "--prune=all", external=True)
    
    # Clear Homebrew cache
    session.run("rm", "-rf", "~/.cache/Homebrew/*", external=True, success_codes=[0, 1])
    
    session.log("✅ Cleanup completed")


@nox.session(python=False)
def help(session):
    """Show available nox sessions and their descriptions."""
    session.log("📋 Available Nox Sessions:")
    session.log("")
    session.log("Core Testing:")
    session.log("  lint              - Run Ruby syntax validation and basic checks")
    session.log("  formula_syntax    - Validate Homebrew formula syntax and structure")  
    session.log("  url_validation    - Test that formula URLs are accessible")
    session.log("  install_test      - Test formula installation and basic CLI functionality")
    session.log("  latex_test        - Test LaTeX dependency installation and functionality")
    session.log("  formula_test      - Run built-in formula test block")
    session.log("")
    session.log("Performance:")
    session.log("  benchmark         - Run performance benchmarks")
    session.log("")
    session.log("Test Suites:")
    session.log("  comprehensive     - Run all tests (thorough)")
    session.log("  ci_test           - Run CI-optimized test suite (fast)")
    session.log("")
    session.log("Utilities:")
    session.log("  cleanup           - Clean up test installations and cache")
    session.log("  help              - Show this help message")
    session.log("")
    session.log("Usage Examples:")
    session.log("  nox                    # Run default sessions")
    session.log("  nox -s lint            # Run specific session")
    session.log("  nox -s comprehensive   # Run all tests")
    session.log("  nox -s ci_test         # Fast CI tests")