<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/validators/pdf_validator.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pdf_validator.py`
PDF post-build validator for verifying final PDF output. 

This validator extracts text from the generated PDF and verifies that: 
- Citations are properly rendered (no "?" citations) 
- Equations are properly rendered (no malformed LaTeX) 
- Figure references are properly resolved 
- Table references are properly resolved 
- Cross-references are working correctly 
- Bibliography entries are present 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/validators/pdf_validator.py#L469"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `validate_pdf`

```python
validate_pdf(
    manuscript_path: str,
    pdf_path: Optional[str] = None
) → ValidationResult
```

Convenience function to validate a PDF file. 



**Args:**
 
 - <b>`manuscript_path`</b>:  Path to manuscript directory 
 - <b>`pdf_path`</b>:  Path to PDF file (optional) 



**Returns:**
 ValidationResult with PDF validation issues 


---

## <kbd>class</kbd> `PDFValidator`
Validator for checking final PDF output quality. 

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/validators/pdf_validator.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(manuscript_path: str, pdf_path: Optional[str] = None)
```

Initialize PDF validator. 



**Args:**
 
 - <b>`manuscript_path`</b>:  Path to manuscript directory 
 - <b>`pdf_path`</b>:  Path to PDF file (if None, looks for standard output) 




---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/validators/pdf_validator.py#L403"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `validate`

```python
validate() → ValidationResult
```

Validate PDF output quality. 



**Returns:**
  ValidationResult with PDF validation issues 


