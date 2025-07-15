<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/bibliography_checksum.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `bibliography_checksum.py`
Bibliography checksum manager for efficient DOI validation. 

This module provides checksum-based DOI validation that only re-validates bibliography files when they actually change, not just when timestamps change. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/bibliography_checksum.py#L272"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_bibliography_checksum_manager`

```python
get_bibliography_checksum_manager(
    manuscript_path: str
) → BibliographyChecksumManager
```

Get a BibliographyChecksumManager instance for the given manuscript. 



**Args:**
 
 - <b>`manuscript_path`</b>:  Path to the manuscript directory 



**Returns:**
 BibliographyChecksumManager instance 


---

## <kbd>class</kbd> `BibliographyChecksumManager`
Manages checksums for bibliography files to enable efficient DOI validation. 

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/bibliography_checksum.py#L21"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(manuscript_path: str, cache_dir: str = '.cache')
```

Initialize the bibliography checksum manager. 



**Args:**
 
 - <b>`manuscript_path`</b>:  Path to the manuscript directory 
 - <b>`cache_dir`</b>:  Directory for cache files (relative to project root) 




---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/bibliography_checksum.py#L117"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `bibliography_has_changed`

```python
bibliography_has_changed() → tuple[bool, Optional[str]]
```

Check if bibliography file has changed since last validation. 



**Returns:**
  Tuple of (has_changed, current_checksum) 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/bibliography_checksum.py#L264"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `clear_cache`

```python
clear_cache() → None
```

Clear all cached checksum data. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/bibliography_checksum.py#L146"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `doi_entries_have_changed`

```python
doi_entries_have_changed() → tuple[bool, Optional[dict[str, str]]]
```

Check if DOI entries in bibliography have changed. 



**Returns:**
  Tuple of (have_changed, current_doi_entries) 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/bibliography_checksum.py#L235"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `force_validation`

```python
force_validation() → None
```

Force validation by clearing cached checksum. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/bibliography_checksum.py#L241"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_cache_stats`

```python
get_cache_stats() → dict[str, any]
```

Get statistics about the bibliography checksum cache. 



**Returns:**
  Dictionary with cache statistics 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/bibliography_checksum.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `needs_validation`

```python
needs_validation() → bool
```

Check if bibliography needs DOI validation. 



**Returns:**
  True if validation is needed, False otherwise 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/bibliography_checksum.py#L195"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `update_checksum`

```python
update_checksum(validation_completed: bool = True) → None
```

Update checksum after validation is completed. 



**Args:**
 
 - <b>`validation_completed`</b>:  Whether validation was successfully completed 


