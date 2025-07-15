<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/figure_checksum.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `figure_checksum.py`
Figure checksum manager for efficient figure regeneration. 

This module provides checksum-based figure regeneration that only regenerates figures when source files (.mmd, .py, .R) actually change, not just when timestamps change. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/figure_checksum.py#L235"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_figure_checksum_manager`

```python
get_figure_checksum_manager(manuscript_path: str) → FigureChecksumManager
```

Get a FigureChecksumManager instance for the given manuscript. 



**Args:**
 
 - <b>`manuscript_path`</b>:  Path to the manuscript directory 



**Returns:**
 FigureChecksumManager instance 


---

## <kbd>class</kbd> `FigureChecksumManager`
Manages checksums for figure source files to enable efficient regeneration. 

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/figure_checksum.py#L21"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(manuscript_path: str, cache_dir: str = '.cache')
```

Initialize the checksum manager. 



**Args:**
 
 - <b>`manuscript_path`</b>:  Path to the manuscript directory 
 - <b>`cache_dir`</b>:  Directory for cache files (relative to project root) 




---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/figure_checksum.py#L132"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `check_figures_need_update`

```python
check_figures_need_update() → bool
```

Check if any figures need to be updated. 



**Returns:**
  True if any figure source files have changed, False otherwise 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/figure_checksum.py#L177"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `cleanup_orphaned_checksums`

```python
cleanup_orphaned_checksums() → None
```

Remove checksums for files that no longer exist. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/figure_checksum.py#L227"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `clear_cache`

```python
clear_cache() → None
```

Clear all checksums from cache. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/figure_checksum.py#L222"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `force_update_all`

```python
force_update_all() → None
```

Force update all checksums regardless of current state. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/figure_checksum.py#L201"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_cache_stats`

```python
get_cache_stats() → dict[str, any]
```

Get statistics about the checksum cache. 



**Returns:**
  Dictionary with cache statistics 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/figure_checksum.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_changed_files`

```python
get_changed_files() → list[Path]
```

Get list of figure source files that have changed. 



**Returns:**
  List of Path objects for files that have changed or are new 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/figure_checksum.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_figure_source_files`

```python
get_figure_source_files() → list[Path]
```

Get all figure source files in the FIGURES directory. 



**Returns:**
  List of Path objects for .mmd, .py, and .R files 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/figure_checksum.py#L149"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `update_checksums`

```python
update_checksums(files: Optional[list[Path]] = None) → None
```

Update checksums for specified files or all source files. 



**Args:**
 
 - <b>`files`</b>:  Optional list of specific files to update. If None, updates all source files. 


