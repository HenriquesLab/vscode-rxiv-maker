<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `build_manager.py`
Build manager for Rxiv-Maker. 

This script orchestrates the complete build process including: 
- Figure generation 
- File copying 
- LaTeX compilation 
- PDF output management 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_figure_generator`

```python
get_figure_generator()
```

Get FigureGenerator class with lazy import. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L830"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `main`

```python
main()
```

Main entry point for build manager. 


---

## <kbd>class</kbd> `BuildManager`
Manage the complete build process. 

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    manuscript_path: Optional[str] = None,
    output_dir: str = 'output',
    force_figures: bool = False,
    skip_validation: bool = False,
    skip_pdf_validation: bool = False,
    verbose: bool = False
)
```

Initialize build manager. 



**Args:**
 
 - <b>`manuscript_path`</b>:  Path to manuscript directory 
 - <b>`output_dir`</b>:  Output directory for generated files 
 - <b>`force_figures`</b>:  Force regeneration of all figures 
 - <b>`skip_validation`</b>:  Skip manuscript validation 
 - <b>`skip_pdf_validation`</b>:  Skip PDF validation 
 - <b>`verbose`</b>:  Enable verbose output 




---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L160"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `check_manuscript_structure`

```python
check_manuscript_structure() → bool
```

Check if manuscript directory exists and has required structure. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L524"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `compile_pdf`

```python
compile_pdf() → bool
```

Compile LaTeX to PDF. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L443"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `copy_figures`

```python
copy_figures() → bool
```

Copy figure files to output directory. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L645"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `copy_pdf_to_manuscript`

```python
copy_pdf_to_manuscript() → bool
```

Copy generated PDF to manuscript directory with custom name. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L431"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `copy_references`

```python
copy_references() → bool
```

Copy references bibliography file to output directory. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L401"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `copy_style_files`

```python
copy_style_files() → bool
```

Copy LaTeX style files to output directory. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L257"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `generate_figures`

```python
generate_figures() → bool
```

Generate figures from source files. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L481"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `generate_tex_files`

```python
generate_tex_files() → bool
```

Generate LaTeX files from manuscript. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L90"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message: str, level: str = 'INFO')
```

Log a message with appropriate formatting. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L768"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `run_full_build`

```python
run_full_build() → bool
```

Run the complete build process. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L723"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `run_pdf_validation`

```python
run_pdf_validation() → bool
```

Run PDF validation to check final output quality. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L684"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `run_word_count_analysis`

```python
run_word_count_analysis() → bool
```

Run word count analysis on the manuscript. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L149"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `setup_output_directory`

```python
setup_output_directory() → bool
```

Create and set up the output directory. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/build_manager.py#L211"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `validate_manuscript`

```python
validate_manuscript() → bool
```

Run manuscript validation. 


