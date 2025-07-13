[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15752358.svg)](https://doi.org/10.5281/zenodo.15752358)
[![License](https://img.shields.io/github/license/henriqueslab/rxiv-maker?color=Green)](https://github.com/henriqueslab/rxiv-maker/blob/main/LICENSE)
[![Contributors](https://img.shields.io/github/contributors-anon/henriqueslab/rxiv-maker)](https://github.com/henriqueslab/rxiv-maker/graphs/contributors)
[![GitHub stars](https://img.shields.io/github/stars/henriqueslab/rxiv-maker?style=social)](https://github.com/HenriquesLab/rxiv-maker/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/henriqueslab/rxiv-maker?style=social)](https://github.com/henriqueslab/rxiv-maker/forks)

![Enhanced Markdown (rxiv-markdown)](https://img.shields.io/badge/rxiv_markdown-20+_features-blue?labelColor=white&color=gray)
![Figure Generation](https://img.shields.io/badge/figures-python_&_R_&_mermaid-blue?labelColor=white&color=gray)
![Cross References](https://img.shields.io/badge/cross_refs-automated-blue?labelColor=white&color=gray)
![Citations](https://img.shields.io/badge/citations-bibtex-blue?labelColor=white&color=gray)
![LaTeX Output](https://img.shields.io/badge/output-professional_pdf-blue?labelColor=white&color=gray)
![Docker Support](https://img.shields.io/badge/docker-containerized_builds-blue?labelColor=white&color=gray)
![GitHub Actions](https://img.shields.io/badge/deployment-cloud_&_local-blue?labelColor=white&color=gray)
![VS Code Extension](https://img.shields.io/badge/VS_Code-extension_available-blue?labelColor=white&color=gray)

# Rxiv-Maker

<img src="src/logo/logo-rxiv-maker.svg" align="right" width="200" style="margin-left: 20px;"/>

Rxiv-Maker is an automated LaTeX article generation system that transforms scientific writing from chaos to clarity. It converts Markdown manuscripts into publication-ready PDFs with reproducible figures, professional typesetting, and zero LaTeX hassle.

The platform bridges the gap between **easy writing** (Markdown) and **beautiful output** (LaTeX), featuring automated figure generation from Python/R scripts and Mermaid diagrams, seamless citation management, Docker containerization for dependency-free execution, and integration with GitHub Actions for accelerated cloud-based PDF generation.

Rxiv-Maker enhances the capabilities of traditional scientific writing by ensuring version control compatibility, facilitating reproducible science workflows, and providing professional formatting that meets publication standards.

## Key Features

- **20+ Enhanced Markdown Features** - Scientific cross-references, citations, subscript/superscript, and programmatic figure generation. A new standard for scientific Markdown writing dubbed **rxiv-markdown**.
- **Intelligent Validation System** - Pre-build validation catches errors with actionable feedback and suggestions
- **Automated Figure Generation** - Python scripts, R scripts, and Mermaid diagrams with smart caching
- **GitHub Actions Integration** - Cloud-based PDF generation with manual triggers
- **Professional LaTeX Templates** - Various citation styles and academic formatting
- **Version Control Friendly** - Git-based workflows and reproducible builds
- **Multi-Environment Support** - Local, Docker containers, Google Colab, and GitHub Actions
- **VS Code Integration** - Dedicated extension with syntax highlighting, IntelliSense, and project commands

<details>
<summary><strong>📋 Complete Rxiv-Markdown Feature List</strong></summary>

| **Markdown Element** | **LaTeX Equivalent** | **Description** |
|------------------|------------------|-------------|
| **Basic Text Formatting** | | |
| `**bold text**` | `\textbf{bold text}` | Bold formatting for emphasis |
| `*italic text*` | `\textit{italic text}` | Italic formatting for emphasis |
| `~subscript~` | `\textsubscript{subscript}` | Subscript formatting (H~2~O, CO~2~) |
| `^superscript^` | `\textsuperscript{superscript}` | Superscript formatting (E=mc^2^, x^n^) |
| **Document Structure** | | |
| `# Header 1` | `\section{Header 1}` | Top-level section heading |
| `## Header 2` | `\subsection{Header 2}` | Second-level section heading |
| `### Header 3` | `\subsubsection{Header 3}` | Third-level section heading |
| **Lists** | | |
| `- list item` | `\begin{itemize}\item...\end{itemize}` | Unordered list |
| `1. list item` | `\begin{enumerate}\item...\end{enumerate}` | Ordered list |
| **Links and URLs** | | |
| `[link text](url)` | `\href{url}{link text}` | Hyperlink with custom text |
| `https://example.com` | `\url{https://example.com}` | Bare URL |
| **Citations** | | |
| `@citation` | `\cite{citation}` | Single citation reference |
| `[@cite1;@cite2]` | `\cite{cite1,cite2}` | Multiple citation references |
| **Cross-References** | | |
| `@fig:label` | `\ref{fig:label}` | Figure cross-reference |
| `@sfig:label` | `\ref{sfig:label}` | Supplementary figure cross-reference |
| `@table:label` | `\ref{table:label}` | Table cross-reference |
| `@stable:label` | `\ref{stable:label}` | Supplementary table cross-reference |
| `@eq:label` | `\eqref{eq:label}` | Equation cross-reference |
| `@snote:label` | `\ref{snote:label}` | Supplement note cross-reference |
| **Tables and Figures** | | |
| Markdown table | `\begin{table}...\end{table}` | Table with automatic formatting |
| Image with caption | `\begin{figure}...\end{figure}` | Figure with separate caption |
| **Document Control** | | |
| `<!-- comment -->` | `% comment` | Comments (converted to LaTeX style) |
| `<newpage>` | `\newpage` | Manual page break control |
| `<clearpage>` | `\clearpage` | Page break with float clearing |
| `<float-barrier>` | `\FloatBarrier` | Prevent floats from crossing this point |

</details>

## Key Benefits of Rxiv-Maker

- **Accessibility:** Write in familiar Markdown syntax without LaTeX expertise. Interactive workflows lower barriers for researchers.
- **Reproducibility:** Automated figure generation and version control ensure consistent results across builds.
- **Flexibility:** Generate PDFs locally, in the cloud, or via GitHub Actions. No vendor lock-in.
- **Professional Output:** LaTeX-quality formatting with automated bibliography and cross-reference management.
- **Collaboration:** Git-based workflows enable team editing with automated PDF generation for reviews.
- **Extensibility:** Modular architecture supports custom templates, styles, and figure generation scripts.

## What is Rxiv-Maker?

- A comprehensive manuscript generation system combining Markdown simplicity with LaTeX professionalism.
- Fully automated figure generation from Python scripts, R scripts, and Mermaid diagrams integrated into the document build process.
- GitHub Actions workflows provide cloud-based PDF generation with dependency caching and artifact management.
- Professional templates supporting academic publishing conventions, including author affiliations, ORCID integration, and citation styles.
- Version-controlled workflow enabling collaborative writing with automated quality checks and build validation.

## Quickstart

### 🎯 **Choose Your Setup Method (Pick ONE)**

<details>
<summary><strong>🆕 New Users → Start Here (2-5 minutes)</strong></summary>

**Recommended for first-time users:**

**🌐 Google Colab** (No installation required)
- Build manuscripts in your browser [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/HenriquesLab/rxiv-maker/blob/main/notebooks/rxiv_maker_colab.ipynb)
- Perfect for: Trying Rxiv-Maker, quick experiments, collaborative editing
- [Complete Tutorial →](docs/tutorials/google_colab.md)

**🐳 Docker Engine** (Only Docker + Make required)
- No LaTeX, Python, or R installation needed
- Cross-platform consistency (Windows, macOS, Linux)
- [Setup Guide →](docs/docker-engine-mode.md)

</details>

<details>  
<summary><strong>🔧 Developers & Power Users (5-30 minutes)</strong></summary>

**For ongoing development work:**

**🏠 Local Development** (Full control)
- Complete local environment setup
- Best for: Advanced users, offline work, custom modifications
- [Platform-Specific Setup →](docs/platforms/LOCAL_DEVELOPMENT.md)

**⚡ GitHub Actions** (Automated cloud builds)
- Automatic PDF generation on every commit
- 5x faster builds with pre-compiled Docker images
- [Workflow Setup →](docs/github-actions-guide.md)

</details>

<details>
<summary><strong>📝 VS Code Users (Enhanced editing)</strong></summary>

**After choosing any setup method above:**
- Install [VS Code Extension](https://github.com/HenriquesLab/vscode-rxiv-maker) for syntax highlighting and IntelliSense
- Intelligent autocompletion for citations and cross-references
- Integrated commands for validation and PDF generation

</details>

### 🚀 First PDF in 2 Minutes

Once you've chosen your method above, generate your first PDF:

```bash
# For all local methods (add RXIV_ENGINE=DOCKER for Docker mode)
git clone https://github.com/henriqueslab/rxiv-maker.git
cd rxiv-maker
make pdf MANUSCRIPT_PATH=EXAMPLE_MANUSCRIPT

# For Google Colab: just click the badge above
# For GitHub Actions: fork repo → Actions tab → "Run workflow"
```

## Core Workflow

1. **Write** your manuscript in Markdown (`01_MAIN.md`)
2. **Configure** metadata in YAML (`00_CONFIG.yml`). Directly or using our notebook 
3. **Create** figures with Python scripts, R scripts, Mermaid diagrams or upload images
4. **Validate** your manuscript (`make validate`) to catch issues early
5. **Build** your PDF locally (`make pdf`) or via GitHub Actions
6. **Collaborate** using Git workflows with automated PDF generation

## Documentation

### Essential Guides
- **[Google Colab Tutorial](docs/tutorials/google_colab.md)** – Browser-based PDF generation (no installation required)
- **[GitHub Actions Tutorial](docs/tutorials/github_actions.md)** – Automated PDF generation and team workflows
- **[GitHub Actions Guide](docs/github-actions-guide.md)** – Complete cloud PDF generation tutorial
- **[User Guide](docs/user_guide.md)** – Comprehensive usage instructions and troubleshooting
- **[Architecture Overview](docs/architecture.md)** – System design and technical details

### Editor Integration
- **[VS Code Extension](https://github.com/HenriquesLab/vscode-rxiv-maker)** – Enhanced editing with syntax highlighting and IntelliSense

### Platform-Specific Setup
- **[Windows/macOS/Linux Setup](docs/platforms/LOCAL_DEVELOPMENT.md)** – Complete installation guides for all platforms

### Reference Documentation
- **[API Reference](docs/api/README.md)** – Python API documentation

### Quick Reference
| Task | Command | Documentation |
|------|---------|---------------|
| Generate PDF | `make pdf` | [User Guide](docs/user_guide.md) |
| Validate Manuscript | `make validate` | [Validation Guide](docs/validate_manuscript.md) |
| Fix Bibliography | `make fix-bibliography` | [User Guide](docs/user_guide.md) |
| Add Bibliography Entry | `make add-bibliography 10.1000/doi` | [User Guide](docs/user_guide.md) |
| Cloud PDF Generation | Actions → "Run workflow" | [GitHub Actions Guide](docs/github-actions-guide.md) |
| Custom Manuscript | `make pdf MANUSCRIPT_PATH=MY_PAPER` | [User Guide](docs/user_guide.md) |
| Force Figure Regeneration | `make pdf FORCE_FIGURES=true` | [User Guide](docs/user_guide.md) |

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

For troubleshooting, advanced features, and detailed guides, see the [User Guide](docs/user_guide.md).

## Contributing

We welcome contributions! Check out our [contributing guidelines](CONTRIBUTING.md) and help improve Rxiv-Maker.

```bash
# Development setup
git clone https://github.com/henriqueslab/rxiv-maker.git
pip install -e ".[dev]"
pre-commit install
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
