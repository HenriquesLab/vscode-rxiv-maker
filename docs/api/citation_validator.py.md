<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/validators/citation_validator.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `citation_validator.py`
Citation validator for checking citation syntax and bibliography references. 



---

## <kbd>class</kbd> `CitationValidator`
Validates citation syntax and checks against bibliography. 

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/validators/citation_validator.py#L41"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(manuscript_path: str, enable_doi_validation: bool = True)
```

Initialize citation validator. 



**Args:**
 
 - <b>`manuscript_path`</b>:  Path to the manuscript directory 
 - <b>`enable_doi_validation`</b>:  Whether to enable DOI validation 




---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/validators/citation_validator.py#L363"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_citation_statistics`

```python
get_citation_statistics() → dict[str, Any]
```

Get statistics about citations found. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/validators/citation_validator.py#L54"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `validate`

```python
validate() → ValidationResult
```

Validate citations in manuscript files. 


