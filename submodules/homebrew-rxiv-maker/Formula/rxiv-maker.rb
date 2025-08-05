class RxivMaker < Formula
  include Language::Python::Virtualenv

  desc "Automated LaTeX article generation with modern CLI and figure support"
  homepage "https://github.com/henriqueslab/rxiv-maker"
  url "https://files.pythonhosted.org/packages/f2/a7/07c8c68c8e44cda429c1aae3ef1520d46402590ea86a5c84800eaac87505/rxiv_maker-1.4.5.tar.gz"
  sha256 "f1ccdce643de014ad17b78f9632b4ee72b725000d82315fe59c0f05cc9af2d00"
  license "MIT"

  depends_on "python@3.12"

  on_linux do
    depends_on "libyaml"
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/60/6c/8ca2efa64cf75a977a0d7fac081354553ebe483345c734fb6b6515d96bbc/click-8.2.1.tar.gz"
    sha256 "27c491cc05d968d271d5a1db13e3b5a184636d9d930f148c50b038f0d0646202"
  end

  resource "crossref-commons" do
    url "https://files.pythonhosted.org/packages/8a/9d/a69673e371afa0d77edcb0cc8dfb6b05ccd9e1ffe879ca7804cf32e7851c/crossref_commons-0.0.7.tar.gz"
    sha256 "4b8ae35d48acc4fe62da1662525396477e4f8c76fdb00cd42d5334c68713c4b6"
  end

  resource "folder2md4llms" do
    url "https://files.pythonhosted.org/packages/08/1b/1f44e02a32cf6d9c837c0c7aa87df741f328ba00517d52b7010b6eb00757/folder2md4llms-0.4.35.tar.gz"
    sha256 "a18b59884c060a7923ec1d71682d0f65e8886e9e4150cb56e3ea82581df0bcb2"
  end

  resource "lazydocs" do
    url "https://files.pythonhosted.org/packages/10/d2/ff630536151c8f5aaf03aebbc963f570dc9f2af0b3f35c11774e0c4c75af/lazydocs-0.4.8.tar.gz"
    sha256 "8ac1fda05f03e0c5ae1d30b81eaeb785476efa161194a5e8bfa8630e14af9562"
  end

  resource "matplotlib" do
    url "https://files.pythonhosted.org/packages/26/91/d49359a21893183ed2a5b6c76bec40e0b1dcbf8ca148f864d134897cfc75/matplotlib-3.10.3.tar.gz"
    sha256 "2f82d2c5bb7ae93aaaa4cd42aca65d76ce6376f83304fa3a630b569aca274df0"
  end

  resource "numpy" do
    url "https://files.pythonhosted.org/packages/2e/19/d7c972dfe90a353dbd3efbbe1d14a5951de80c99c9dc1b93cd998d51dc0f/numpy-2.3.1.tar.gz"
    sha256 "1ec9ae20a4226da374362cca3c62cd753faf2f951440b0e3b98e93c235441d2b"
  end

  resource "packaging" do
    url "https://files.pythonhosted.org/packages/a1/d4/1fc4078c65507b51b96ca8f8c3ba19e6a61c8253c72794544580a7b6c24d/packaging-25.0.tar.gz"
    sha256 "d443872c98d677bf60f6a1f2f8c1cb748e8fe762d2bf9d3148b5599295b0fc4f"
  end

  resource "pandas" do
    url "https://files.pythonhosted.org/packages/d1/6f/75aa71f8a14267117adeeed5d21b204770189c0a0025acbdc03c337b28fc/pandas-2.3.1.tar.gz"
    sha256 "0a95b9ac964fe83ce317827f80304d37388ea77616b1425f0ae41c9d2d0d7bb2"
  end

  resource "pillow" do
    url "https://files.pythonhosted.org/packages/f3/0d/d0d6dea55cd152ce3d6767bb38a8fc10e33796ba4ba210cbab9354b6d238/pillow-11.3.0.tar.gz"
    sha256 "3828ee7586cd0b2091b6209e5ad53e20d0649bbe87164a459d0676e035e8f523"
  end

  resource "pypdf" do
    url "https://files.pythonhosted.org/packages/28/5a/139b1a3ec3789cc77a7cb9d5d3bc9e97e742e6d03708baeb7719f8ad0827/pypdf-5.8.0.tar.gz"
    sha256 "f8332f80606913e6f0ce65488a870833c9d99ccdb988c17bb6c166f7c8e140cb"
  end

  resource "python-dotenv" do
    url "https://files.pythonhosted.org/packages/f6/b0/4bc07ccd3572a2f9df7e6782f52b0c6c90dcbb803ac4a167702d7d0dfe1e/python_dotenv-1.1.1.tar.gz"
    sha256 "a8a6399716257f45be6a007360200409fce5cda2661e3dec71d23dc15f6189ab"
  end

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/54/ed/79a089b6be93607fa5cdaedf301d7dfb23af5f25c398d5ead2525b063e17/pyyaml-6.0.2.tar.gz"
    sha256 "d584d9ec91ad65861cc08d42e834324ef890a082e591037abe114850ff7bbc3e"
  end

  resource "rich-click" do
    url "https://files.pythonhosted.org/packages/b7/a8/dcc0a8ec9e91d76ecad9413a84b6d3a3310c6111cfe012d75ed385c78d96/rich_click-1.8.9.tar.gz"
    sha256 "fd98c0ab9ddc1cf9c0b7463f68daf28b4d0033a74214ceb02f761b3ff2af3136"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/a1/53/830aa4c3066a8ab0ae9a9955976fb770fe9c6102117c8ec4ab3ea62d89e8/rich-14.0.0.tar.gz"
    sha256 "82f1bc23a6a21ebca4ae0c45af9bdbc492ed20231dcb63f297d6d1021a9d5725"
  end

  resource "scipy" do
    url "https://files.pythonhosted.org/packages/81/18/b06a83f0c5ee8cddbde5e3f3d0bb9b702abfa5136ef6d4620ff67df7eee5/scipy-1.16.0.tar.gz"
    sha256 "b5ef54021e832869c8cfb03bc3bf20366cbcd426e02a58e8a58d7584dfbb8f62"
  end

  resource "seaborn" do
    url "https://files.pythonhosted.org/packages/86/59/a451d7420a77ab0b98f7affa3a1d78a313d2f7281a57afb1a34bae8ab412/seaborn-0.13.2.tar.gz"
    sha256 "93e60a40988f4d65e9f4885df477e2fdaff6b73a9ded434c1ab356dd57eefff7"
  end

  resource "typing-extensions" do
    url "https://files.pythonhosted.org/packages/98/5a/da40306b885cc8c09109dc2e1abd358d5684b1425678151cdaed4731c822/typing_extensions-4.14.1.tar.gz"
    sha256 "38b39f4aeeab64884ce9f74c94263ef78f3c22467c8724005483154c26648d36"
  end

  def install
    virtualenv_install_with_resources
  end

  def caveats
    <<~EOS
      rxiv-maker has been installed with all Python dependencies in an isolated virtual environment.

      For full functionality, you'll need additional system dependencies:

      macOS:
        brew install --cask mactex     # Full LaTeX distribution (recommended)
        # OR
        brew install --cask basictex   # Minimal LaTeX installation

      The 'rxiv' command is now available. Quick start:
        rxiv init          # Initialize a new manuscript
        rxiv pdf           # Generate PDF
        rxiv --help        # Show help

      Documentation: https://github.com/henriqueslab/rxiv-maker#readme
    EOS
  end

  test do
    # Test that the CLI is working
    assert_match "version", shell_output("#{bin}/rxiv --version")

    # Test basic functionality
    system bin/"rxiv", "--help"

    # Test Python module import
    system libexec/"bin/python", "-c", "import rxiv_maker; print('Import successful')"
  end
end
