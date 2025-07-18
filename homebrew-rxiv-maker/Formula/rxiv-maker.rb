class RxivMaker < Formula
  include Language::Python::Virtualenv

  desc "Automated LaTeX article generation from Markdown with figure creation"
  homepage "https://github.com/henriqueslab/rxiv-maker"
  url "https://files.pythonhosted.org/packages/8e/e0/87fe31c8e57b8638077a945fb31dd3878201058b04f35a569ec5f2969e23/rxiv_maker-1.4.0.tar.gz"
  sha256 "15d9e9fbc1ad0ca42b6c64d487088fdaa0f365c3884781b918bf56af8787a2ed"
  license "MIT"
  version "1.4.0"

  # Remove deprecated options - Homebrew no longer supports build options

  head "https://github.com/henriqueslab/rxiv-maker.git", branch: "main"

  # Core dependencies for local (non-Docker) development
  depends_on "python@3.12"  # Use current Homebrew Python
  depends_on "node"         # Use current Node.js
  depends_on "r"
  depends_on "make"

  # LaTeX distribution - prefer BasicTeX for smaller footprint
  # Users can upgrade to full MacTeX if needed
  # Note: basictex is a cask, not a formula

  # Python dependencies will be installed automatically by pip
  # when installing the main package with its dependencies

  def install
    # Create virtual environment using Homebrew's helper
    venv = virtualenv_create(libexec, "python3.12")

    # Install the main package from the source tarball with dependencies
    venv.pip_install_and_link buildpath

    # Note: LaTeX packages installation removed - should be handled by user
    # as it requires sudo and may fail in sandboxed environments
  end

  def post_install
    # Verify core dependencies
    puts "🎉 rxiv-maker installed successfully!"
    puts ""
    puts "📋 Verifying dependencies..."

    # Check Python
    system_python = which("python3.12")
    if system_python
      puts "  ✅ Python 3.12: #{system_python}"
    else
      puts "  ❌ Python 3.12 not found"
    end

    # Check Node.js
    system_node = which("node")
    if system_node
      node_version = `node --version`.strip
      puts "  ✅ Node.js: #{node_version}"
    else
      puts "  ❌ Node.js not found"
    end

    # Check R
    system_r = which("R")
    if system_r
      puts "  ✅ R: #{system_r}"
    else
      puts "  ❌ R not found"
    end

    # Check LaTeX
    system_latex = which("pdflatex")
    if system_latex
      puts "  ✅ LaTeX (pdflatex): #{system_latex}"
    else
      puts "  ❌ LaTeX not found"
    end

    puts ""
    puts "🚀 Getting Started:"
    puts "  1. Initialize a new manuscript:"
    puts "     rxiv init my-paper/"
    puts "     cd my-paper/"
    puts ""
    puts "  2. Edit your manuscript files:"
    puts "     - 00_CONFIG.yml (metadata)"
    puts "     - 01_MAIN.md (main content)"
    puts "     - 03_REFERENCES.bib (bibliography)"
    puts ""
    puts "  3. Generate your PDF:"
    puts "     rxiv build"
    puts ""
    puts "📚 Documentation: https://github.com/henriqueslab/rxiv-maker#readme"
    puts "🆘 Issues: https://github.com/henriqueslab/rxiv-maker/issues"
  end

  def caveats
    <<~EOS
      📦 Additional Setup Required:

      1. LaTeX Installation:
         Install LaTeX manually (required for PDF generation):
         brew install --cask basictex
         sudo tlmgr update --self
         sudo tlmgr install latexdiff biber biblatex pgfplots adjustbox collectbox

      2. R Packages:
         Install R packages as needed for your figure scripts:
         R -e "install.packages(c('ggplot2', 'dplyr', 'readr'))"

      3. Node.js Packages:
         Mermaid CLI will be installed automatically when needed.

      4. Environment Variables:
         You can customize behavior with:
         export MANUSCRIPT_PATH=my-custom-path/
         export RXIV_ENGINE=LOCAL  # (default, vs DOCKER)

      5. First Run:
         Run 'rxiv setup' to verify your environment and install
         any missing dependencies.

      🔧 Troubleshooting:
         - Run 'rxiv setup --check-all' to diagnose issues
         - Use 'rxiv validate' to check manuscript before building
         - Check documentation at: https://github.com/henriqueslab/rxiv-maker

      🎯 Quick Test:
         rxiv init test-paper/ && cd test-paper/ && rxiv build
    EOS
  end

  test do
    # Test that the CLI is accessible and responds
    assert_match version.to_s, shell_output("#{bin}/rxiv --version")

    # Test help command
    assert_match "Automated LaTeX article generation", shell_output("#{bin}/rxiv --help")

    # Test that we can import the package
    system libexec/"venv/bin/python", "-c", "import rxiv_maker; print('✅ rxiv_maker module imported successfully')"
  end
end
