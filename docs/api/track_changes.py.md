<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `track_changes.py`
Track changes functionality for Rxiv-Maker. 

This module provides change tracking capabilities by comparing the current manuscript against a specified git tag using latexdiff. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `extract_yaml_metadata_local`

```python
extract_yaml_metadata_local(yaml_file_path: str) → dict
```

Extract YAML metadata from a config file. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_custom_pdf_filename_local`

```python
get_custom_pdf_filename_local(yaml_metadata: dict) → str
```

Generate custom PDF filename from metadata. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L585"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `main`

```python
main()
```

Main entry point for track changes. 


---

## <kbd>class</kbd> `TrackChangesManager`
Manage change tracking between current manuscript and a git tag. 

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L74"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    manuscript_path: str,
    output_dir: str = 'output',
    git_tag: str = '',
    verbose: bool = False
)
```

Initialize track changes manager. 



**Args:**
 
 - <b>`manuscript_path`</b>:  Path to manuscript directory 
 - <b>`output_dir`</b>:  Output directory for generated files 
 - <b>`git_tag`</b>:  Git tag to compare against 
 - <b>`verbose`</b>:  Enable verbose output 




---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L282"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `compile_diff_pdf`

```python
compile_diff_pdf(diff_tex: Path) → bool
```

Compile the difference LaTeX file to PDF. 



**Args:**
 
 - <b>`diff_tex`</b>:  Path to difference LaTeX file 



**Returns:**
 True if compilation successful, False otherwise 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L517"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `copy_compilation_files`

```python
copy_compilation_files()
```

Copy necessary files for LaTeX compilation. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L556"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `copy_pdf_to_manuscript`

```python
copy_pdf_to_manuscript(pdf_file: Path) → bool
```

Copy the generated change tracking PDF to the manuscript directory. 



**Args:**
 
 - <b>`pdf_file`</b>:  Path to the generated PDF file 



**Returns:**
 True if copy successful, False otherwise 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L132"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `extract_files_from_tag`

```python
extract_files_from_tag(temp_dir: Path) → bool
```

Extract manuscript files from the specified git tag. 



**Args:**
 
 - <b>`temp_dir`</b>:  Temporary directory to extract files to 



**Returns:**
 True if extraction successful, False otherwise 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L451"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `generate_change_tracked_pdf`

```python
generate_change_tracked_pdf() → bool
```

Generate a PDF with changes tracked against the specified git tag. 



**Returns:**
  True if successful, False otherwise 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L425"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `generate_custom_filename`

```python
generate_custom_filename() → str
```

Generate custom filename using the same convention as regular PDF generation. 



**Returns:**
 
 - <b>`Custom filename with format`</b>:  year__first_author_et_al__changes_vs_TAG.pdf 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L182"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `generate_latex_files`

```python
generate_latex_files(manuscript_dir: Path, output_subdir: str) → bool
```

Generate LaTeX files from a manuscript directory. 



**Args:**
 
 - <b>`manuscript_dir`</b>:  Directory containing manuscript files 
 - <b>`output_subdir`</b>:  Subdirectory name in output directory 



**Returns:**
 True if generation successful, False otherwise 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message: str, force: bool = False)
```

Log a message if verbose mode is enabled. 



**Args:**
 
 - <b>`message`</b>:  Message to log 
 - <b>`force`</b>:  Force logging even if not in verbose mode 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L228"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `run_latexdiff`

```python
run_latexdiff(old_tex: Path, new_tex: Path, diff_tex: Path) → bool
```

Run latexdiff to generate difference file. 



**Args:**
 
 - <b>`old_tex`</b>:  Path to old LaTeX file 
 - <b>`new_tex`</b>:  Path to new LaTeX file 
 - <b>`diff_tex`</b>:  Path to output difference file 



**Returns:**
 True if latexdiff successful, False otherwise 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/track_changes.py#L115"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `validate_git_tag`

```python
validate_git_tag() → bool
```

Validate that the specified git tag exists. 



**Returns:**
  True if tag exists, False otherwise 


