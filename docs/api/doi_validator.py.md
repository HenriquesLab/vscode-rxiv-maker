<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/validators/doi_validator.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `doi_validator.py`
DOI validator for checking DOI metadata against CrossRef API. 



---

## <kbd>class</kbd> `DOIValidator`
Validator for checking DOI metadata against CrossRef API. 

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/validators/doi_validator.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    manuscript_path: str,
    enable_online_validation: bool = True,
    cache_dir: Optional[str] = None,
    force_validation: bool = False
)
```

Initialize DOI validator. 



**Args:**
 
 - <b>`manuscript_path`</b>:  Path to manuscript directory 
 - <b>`enable_online_validation`</b>:  Whether to perform online DOI validation 
 - <b>`cache_dir`</b>:  Custom cache directory (default: .cache) 
 - <b>`force_validation`</b>:  Force validation even if checksum unchanged 




---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/validators/doi_validator.py#L77"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `validate`

```python
validate() → ValidationResult
```

Validate DOI entries in bibliography using checksum-based caching. 



**Returns:**
  ValidationResult with DOI validation issues 


