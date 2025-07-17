class RxivMaker < Formula
  desc "Automated LaTeX article generation from Markdown with figure creation"
  homepage "https://github.com/henriqueslab/rxiv-maker"
  url "https://files.pythonhosted.org/packages/source/r/rxiv-maker/rxiv_maker-1.3.0.tar.gz"
  sha256 "placeholder_sha256_to_be_updated_by_automation"
  license "MIT"
  version "1.3.0"

  head "https://github.com/henriqueslab/rxiv-maker.git", branch: "main"

  # Core dependencies for local (non-Docker) development
  depends_on "python@3.11"
  depends_on "node@20"
  depends_on "r"
  depends_on "make"

  # LaTeX distribution - prefer BasicTeX for smaller footprint
  # Users can upgrade to full MacTeX if needed
  depends_on "basictex"

  # Python dependencies will be installed via pip

  def install
    # Create a virtual environment in the formula's prefix
    system "python3.11", "-m", "venv", libexec/"venv"

    # Install the package using pip in the virtual environment
    system libexec/"venv/bin/pip", "install", "--upgrade", "pip"
    system libexec/"venv/bin/pip", "install", buildpath

    # Create wrapper script for the CLI
    (bin/"rxiv").write_env_script libexec/"venv/bin/rxiv", PATH: "#{libexec}/venv/bin:$PATH"

    # Install additional LaTeX packages commonly needed
    system "sudo", "tlmgr", "update", "--self"
    system "sudo", "tlmgr", "install", "latexdiff", "biber", "biblatex", "pgfplots", "adjustbox", "collectbox"
  end

  def post_install
    # Verify core dependencies
    puts "🎉 rxiv-maker installed successfully!"
    puts ""
    puts "📋 Verifying dependencies..."

    # Check Python
    system_python = which("python3.11")
    if system_python
      puts "  ✅ Python 3.11: #{system_python}"
    else
      puts "  ❌ Python 3.11 not found"
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
      📦 Additional Setup Notes:

      1. LaTeX Packages:
         BasicTeX is installed with essential packages. For additional LaTeX packages:
         sudo tlmgr install <package-name>

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
         any missing Python dependencies.

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
