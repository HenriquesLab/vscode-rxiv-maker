class RxivMaker < Formula
  desc "Automated LaTeX article generation with modern CLI and figure support"
  homepage "https://github.com/HenriquesLab/rxiv-maker"
  url "https://files.pythonhosted.org/packages/71/67/bc3e0b800eadb28658d280b87c6b8f542824adc7187c788b34f3f1f9dfea/rxiv_maker-1.4.11.tar.gz"
  sha256 "903d9b9b1e18decf10f983ab63e878ee77c1593b1062c970006a9f79f75563d9"
  license "MIT"

  depends_on "python@3.11"
  depends_on "texlive"

  def install
    # Create virtual environment
    venv = virtualenv_create(libexec, "python3.11")
    venv.pip_install resources
    
    # Create executable wrapper
    (bin/"rxiv").write <<~EOS
      #!/bin/bash
      exec "#{libexec}/bin/python" -m rxiv_maker.cli "$@"
    EOS
  end

  test do
    # Test CLI is working
    assert_match "rxiv-maker", shell_output("#{bin}/rxiv --version")
    
    # Test initialization
    system bin/"rxiv", "init", "test_manuscript", "--no-interactive"
    assert_predicate testpath/"test_manuscript/00_CONFIG.yml", :exist?
    assert_predicate testpath/"test_manuscript/01_MAIN.md", :exist?
    assert_predicate testpath/"test_manuscript/03_REFERENCES.bib", :exist?
    
    # Test validation
    system bin/"rxiv", "validate", "test_manuscript", "--no-doi"
  end
end