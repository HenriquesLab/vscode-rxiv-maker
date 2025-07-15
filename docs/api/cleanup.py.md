<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/cleanup.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `cleanup.py`
Cleanup command for Rxiv-Maker. 

This script handles cross-platform cleanup operations including: 
- Output directory cleanup 
- Generated figure cleanup 
- ArXiv file cleanup 
- Temporary file cleanup 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/cleanup.py#L340"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `main`

```python
main()
```

Main entry point for cleanup manager. 


---

## <kbd>class</kbd> `CleanupManager`
Handle cleanup operations. 

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/cleanup.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    manuscript_path: str = None,
    output_dir: str = 'output',
    verbose: bool = False
)
```

Initialize cleanup manager. 



**Args:**
 
 - <b>`manuscript_path`</b>:  Path to manuscript directory 
 - <b>`output_dir`</b>:  Output directory to clean 
 - <b>`verbose`</b>:  Enable verbose output 




---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/cleanup.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `clean_arxiv_files`

```python
clean_arxiv_files() → bool
```

Clean ArXiv-related files. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/cleanup.py#L269"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `clean_cache_files`

```python
clean_cache_files() → bool
```

Clean cache files. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/cleanup.py#L94"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `clean_generated_figures`

```python
clean_generated_figures() → bool
```

Clean generated figures from the FIGURES directory. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/cleanup.py#L74"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `clean_output_directory`

```python
clean_output_directory() → bool
```

Clean the output directory. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/cleanup.py#L202"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `clean_temporary_files`

```python
clean_temporary_files() → bool
```

Clean temporary LaTeX and other temporary files. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/cleanup.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message: str, level: str = 'INFO')
```

Log a message with appropriate formatting. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/cleanup.py#L304"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `run_full_cleanup`

```python
run_full_cleanup() → bool
```

Run the complete cleanup process. 


