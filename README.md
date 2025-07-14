[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15752358.svg)](https://doi.org/10.5281/zenodo.15752358)
[![License](https://img.shields.io/github/license/henriqueslab/rxiv-maker?color=Green)](https://github.com/henriqueslab/rxiv-maker/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/henriqueslab/rxiv-maker?style=social)](https://github.com/HenriquesLab/rxiv-maker/stargazers)

# Rxiv-Maker

<img src="src/logo/logo-rxiv-maker.svg" align="right" width="200" style="margin-left: 20px;"/>

Rxiv-Maker is an automated LaTeX article generation system that transforms scientific writing from chaos to clarity. It converts Markdown manuscripts into publication-ready PDFs with reproducible figures, professional typesetting, and zero LaTeX hassle.

The platform bridges the gap between **easy writing** (Markdown) and **beautiful output** (LaTeX), featuring automated figure generation from Python/R scripts and Mermaid diagrams, seamless citation management, Docker containerization for minimal-dependency execution (only Docker and Make required), and integration with GitHub Actions for accelerated cloud-based PDF generation.

Rxiv-Maker enhances the capabilities of traditional scientific writing by ensuring version control compatibility, facilitating reproducible science workflows, and providing professional formatting that meets publication standards.

## Key Features

- **20+ Enhanced Markdown Features** - Scientific cross-references, citations, subscript/superscript (**rxiv-markdown**)
- **Automated Figure Generation** - Python/R scripts and Mermaid diagrams with smart caching
- **Intelligent Validation** - Pre-build error detection with actionable feedback
- **Professional Output** - LaTeX-quality PDFs with various citation styles
- **Multi-Environment** - Local, Docker, Google Colab, and GitHub Actions support
- **Change Tracking** - Visual diff PDFs against git tags
- **VS Code Integration** - Dedicated extension with syntax highlighting

**Key rxiv-markdown features:** Scientific cross-references (`@fig:label`, `@eq:label`), citations (`@citation`), text formatting (`~subscript~`, `^superscript^`), document control (`<newpage>`), and automated figure generation.

## Key Benefits

- **Accessibility** - Write in Markdown without LaTeX expertise
- **Reproducibility** - Automated figures and version control ensure consistent results
- **Flexibility** - Generate PDFs locally, in Docker, or via GitHub Actions
- **Professional Output** - LaTeX-quality formatting with automated bibliography management
- **Collaboration** - Git-based workflows with automated PDF generation

## System Requirements

<details>
<summary><strong>📋 Dependencies & Requirements</strong></summary>

### Core Requirements
- **Python**: 3.11+ (automatically handled in Docker/Colab modes)
- **Git**: For repository management
- **Make**: Build automation (see [platform-specific installation](docs/getting-started/installation.md))

### Python Dependencies
Automatically installed with `make setup`:
```
matplotlib>=3.7.0    # Figure generation
seaborn>=0.12.0      # Statistical plotting  
numpy>=1.24.0        # Numerical computing
pandas>=2.0.0        # Data manipulation
PyYAML>=6.0.0        # Configuration parsing
pypdf>=3.0.0         # PDF processing
crossref-commons     # Citation validation
```

### Optional Dependencies (Local Development Only Without Docker)
- **LaTeX**: For PDF generation (TeX Live, MacTeX, or MikTeX)
- **Node.js**: For Mermaid diagram generation
- **R**: For R-based figure scripts

### Platform-Specific Setup
- **Docker Mode**: Only Docker Desktop + Make required
- **Google Colab**: Zero local installation needed
- **GitHub Actions**: Zero local installation needed
- **Local Development**: Full dependency stack required

### Quick Troubleshooting
- **Permission errors**: Ensure user has write access to project directory
- **LaTeX not found**: Use Docker mode or install platform-specific LaTeX
- **Python version issues**: Use Docker mode or upgrade to Python 3.11+
- **Make command not found**: Install build tools for your platform

**📖 Full Installation Guide**: [Complete platform-specific instructions](docs/getting-started/installation.md)

</details>

## Quickstart

### Setup Options

**🌐 Google Colab** (Easiest - no installation)
- **Prerequisites**: Google account only
- **Setup Time**: 2 minutes
- [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/HenriquesLab/rxiv-maker/blob/main/notebooks/rxiv_maker_colab.ipynb)

**🐳 Docker** (Minimal dependencies)
- **Prerequisites**: [Docker Desktop](https://www.docker.com/products/docker-desktop) + Make
- **Setup Time**: 3-5 minutes
```bash
git clone https://github.com/henriqueslab/rxiv-maker.git
cd rxiv-maker
make pdf RXIV_ENGINE=DOCKER
```

**🏠 Local Development** (Full control)
- **Prerequisites**: Python 3.11+, LaTeX, Make ([platform guide](docs/getting-started/installation.md))
- **Setup Time**: 10-30 minutes
```bash
git clone https://github.com/henriqueslab/rxiv-maker.git
cd rxiv-maker
make setup && make pdf
```

**⚡ GitHub Actions** (Team collaboration)
- **Prerequisites**: GitHub account only
- **Setup Time**: 5 minutes
- **Guide**: [Automated cloud builds guide](docs/workflows/github-actions.md)

**📝 VS Code** (Enhanced editing)
- **Prerequisites**: VS Code editor
- **Extension**: [VS Code Extension](https://github.com/HenriquesLab/vscode-rxiv-maker) for syntax highlighting

## Core Workflow

1. **Write** manuscript in Markdown (`01_MAIN.md`)
2. **Configure** metadata in YAML (`00_CONFIG.yml`)
3. **Create** figures with Python/R scripts or Mermaid diagrams
4. **Validate** with `make validate`
5. **Build** PDF with `make pdf`

## Documentation

<details>
<summary><strong>📚 Complete Documentation Index</strong></summary>

### Getting Started
- **[Installation Guide](docs/getting-started/installation.md)** - Complete setup for all platforms
- **[User Guide](docs/getting-started/user_guide.md)** - Complete usage instructions

### Platform Guides  
- **[Local Development Setup](docs/platforms/LOCAL_DEVELOPMENT.md)** - Platform-specific installation
- **[Docker Engine Mode](docs/workflows/docker-engine-mode.md)** - Containerized development
- **[Google Colab Tutorial](docs/tutorials/google_colab.md)** - Browser-based PDF generation
- **[GitHub Actions Guide](docs/workflows/github-actions.md)** - Automated cloud builds

### Advanced Features
- **[Change Tracking](docs/workflows/change-tracking.md)** - Version diff PDFs
- **[Troubleshooting](docs/troubleshooting/troubleshooting-missing-figures.md)** - Common issues and fixes

### Development
- **[VS Code Extension](https://github.com/HenriquesLab/vscode-rxiv-maker)** - Enhanced editing experience
- **[API Documentation](docs/api/)** - Code reference

</details>

### Quick Commands
```bash
make pdf                              # Generate PDF
make validate                         # Validate manuscript  
make pdf MANUSCRIPT_PATH=MY_PAPER     # Custom manuscript
make pdf FORCE_FIGURES=true           # Force figure regeneration
make pdf-track-changes TAG=v1.0.0     # Track changes vs git tag
make clean                            # Clean output files
make setup                            # Install dependencies
```

### Quick Help
- **Issues?** Check [Troubleshooting Guide](docs/troubleshooting/troubleshooting-missing-figures.md)
- **Platform problems?** See [Installation Guide](docs/getting-started/installation.md) 
- **Need help?** Visit [GitHub Discussions](https://github.com/henriqueslab/rxiv-maker/discussions)

## Project Structure

```
rxiv-maker/
├── MANUSCRIPT/              # Your manuscript files
│   ├── 00_CONFIG.yml       # Metadata and configuration
│   ├── 01_MAIN.md          # Main manuscript content
│   ├── 02_SUPPLEMENTARY_INFO.md  # Optional supplementary
│   ├── 03_REFERENCES.bib   # Bibliography
│   └── FIGURES/            # Figure generation scripts
├── output/                 # Generated PDFs and artifacts
├── src/                    # Rxiv-Maker source code
└── docs/                   # Documentation
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
git clone https://github.com/henriqueslab/rxiv-maker.git
pip install -e ".[dev]" && pre-commit install
```

## How to Cite

<a href="https://zenodo.org/records/15753534"><img src="docs/screenshots/preprint.png" align="right" width="300" style="margin-left: 20px; margin-bottom: 20px;" alt="Rxiv-Maker Preprint"/></a>

If you use Rxiv-Maker in your research, please cite our work:

**BibTeX:**
```bibtex
@article{saraiva_2025_rxivmaker,
  author       = {Saraiva, Bruno M. and Jacquemet, Guillaume and Henriques, Ricardo},
  title        = {Rxiv-Maker: an automated template engine for streamlined scientific publications},
  journal      = {Zenodo},
  publisher    = {Zenodo},
  year         = 2025,
  month        = jul,
  doi          = {10.5281/zenodo.15753534},
  url          = {https://zenodo.org/records/15753534},
  eprint       = {https://zenodo.org/records/15753534/files/2025__saraiva_et_al__rxiv.pdf}
}
```

**APA Style:**
Saraiva, B. M., Jacquemet, G., & Henriques, R. (2025). Rxiv-Maker: an automated template engine for streamlined scientific publications. *Zenodo*. https://doi.org/10.5281/zenodo.15753534

## Related Projects

- **[Rxiv-Maker VS Code Extension](https://github.com/HenriquesLab/vscode-rxiv-maker)** - Enhanced editing experience with syntax highlighting, IntelliSense, and project integration

## Acknowledgments

We extend our gratitude to the scientific computing community, especially the matplotlib and seaborn communities for their plotting tools, the LaTeX Project for professional typesetting, and Mermaid for accessible diagram generation.

## License

MIT License - see [LICENSE](LICENSE) for details. Use it, modify it, share it freely.

---


**© 2025 Jacquemet and Henriques Labs | Rxiv-Maker**  
*"Because science is hard enough without fighting with LaTeX."*
