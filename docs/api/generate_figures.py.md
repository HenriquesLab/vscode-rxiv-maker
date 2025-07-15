<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/generate_figures.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `generate_figures.py`
Figure Generation Script for Rxiv-Maker. 

This script automatically processes figure files in the FIGURES directory and generates publication-ready output files. It supports: 
- .mmd files: Mermaid diagrams (generates SVG/PNG/PDF) 
- .py files: Python scripts for matplotlib/seaborn figures 
- .R files: R scripts (executes script and captures output figures) 

Usage:  python generate_figures.py [--output-dir OUTPUT_DIR] [--format FORMAT] 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/generate_figures.py#L351"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `main`

```python
main()
```

Main function with command-line interface. 


---

## <kbd>class</kbd> `FigureGenerator`
Main class for generating figures from various source formats. 

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/generate_figures.py#L29"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    figures_dir='FIGURES',
    output_dir='FIGURES',
    output_format='png',
    r_only=False
)
```

Initialize the figure generator. 



**Args:**
 
 - <b>`figures_dir`</b>:  Directory containing source figure files 
 - <b>`output_dir`</b>:  Directory for generated output files 
 - <b>`output_format`</b>:  Default output format for figures 
 - <b>`r_only`</b>:  Only process R files if True 




---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/generate_figures.py#L60"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `generate_all_figures`

```python
generate_all_figures()
```

Generate all figures found in the figures directory. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/generate_figures.py#L111"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `generate_mermaid_figure`

```python
generate_mermaid_figure(mmd_file)
```

Generate figure from Mermaid diagram file. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/generate_figures.py#L172"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `generate_python_figure`

```python
generate_python_figure(py_file)
```

Generate figure from Python script. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/generate_figures.py#L235"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `generate_r_figure`

```python
generate_r_figure(r_file)
```

Generate figure from R script. 


