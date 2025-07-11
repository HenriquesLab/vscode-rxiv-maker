<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/add_bibliography.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `add_bibliography.py`
Add bibliography entries from DOI to the bibliography file. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/add_bibliography.py#L518"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `main`

```python
main()
```

Main entry point for add-bibliography command. 


---

## <kbd>class</kbd> `BibliographyAdder`
Add bibliography entries from DOI to bibliography file. 

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/add_bibliography.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(manuscript_path: str)
```

Initialize bibliography adder. 



**Args:**
 
 - <b>`manuscript_path`</b>:  Path to manuscript directory 




---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/add_bibliography.py#L41"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `add_entries`

```python
add_entries(dois: List[str], overwrite: bool = False) → bool
```

Add bibliography entries for the given DOIs. 



**Args:**
 
 - <b>`dois`</b>:  List of DOI strings to add 
 - <b>`overwrite`</b>:  Whether to overwrite existing entries 



**Returns:**
 True if all entries were added successfully, False otherwise 


