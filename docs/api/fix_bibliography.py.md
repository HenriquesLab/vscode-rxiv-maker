<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/fix_bibliography.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `fix_bibliography.py`
Bibliography fixing tool that attempts to find and correct citation information. 

This script analyzes bibliography validation issues and attempts to automatically fix them by searching for publications using CrossRef API based on titles, authors, and other available metadata. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/fix_bibliography.py#L598"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `main`

```python
main()
```

Main entry point for the bibliography fixer. 


---

## <kbd>class</kbd> `BibliographyFixer`
Tool for automatically fixing bibliography issues. 

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/fix_bibliography.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(manuscript_path: str, backup: bool = True)
```

Initialize bibliography fixer. 



**Args:**
 
 - <b>`manuscript_path`</b>:  Path to manuscript directory 
 - <b>`backup`</b>:  Whether to create backup before modifying 




---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/fix_bibliography.py#L59"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `fix_bibliography`

```python
fix_bibliography(dry_run: bool = False) → Dict[str, Any]
```

Fix bibliography issues found by validation. 



**Args:**
 
 - <b>`dry_run`</b>:  If True, show what would be fixed without making changes 



**Returns:**
 Dictionary with fixing results and statistics 


