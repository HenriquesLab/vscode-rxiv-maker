<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `dependency_checker.py`
System dependency checker for Rxiv-Maker. 

This module provides comprehensive checking of system dependencies required for Rxiv-Maker functionality, including LaTeX, Make, Node.js, and R. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L372"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `check_system_dependencies`

```python
check_system_dependencies(verbose: bool = False) → DependencyChecker
```

Check all system dependencies and return checker instance. 



**Args:**
 
 - <b>`verbose`</b>:  Whether to show verbose output 



**Returns:**
 DependencyChecker instance with results 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L386"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `print_dependency_report`

```python
print_dependency_report(verbose: bool = False)
```

Check and print a comprehensive dependency report. 



**Args:**
 
 - <b>`verbose`</b>:  Whether to show verbose output during checks 


---

## <kbd>class</kbd> `DependencyChecker`
Check system dependencies for Rxiv-Maker. 

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L40"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(verbose: bool = False)
```

Initialize dependency checker. 



**Args:**
 
 - <b>`verbose`</b>:  Whether to show verbose output 




---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L252"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `check_all_dependencies`

```python
check_all_dependencies() → list[DependencyInfo]
```

Check all system dependencies. 



**Returns:**
  List of dependency information 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `check_command_version`

```python
check_command_version(
    command: str,
    version_flag: str = '--version'
) → tuple[bool, Optional[str], Optional[str]]
```

Check if a command exists and get its version. 



**Args:**
 
 - <b>`command`</b>:  Command to check 
 - <b>`version_flag`</b>:  Flag to get version (default: --version) 



**Returns:**
 Tuple of (found, version, path) 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L227"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `check_git`

```python
check_git() → DependencyInfo
```

Check for Git (recommended for version control). 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L96"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `check_latex`

```python
check_latex() → DependencyInfo
```

Check for LaTeX installation. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L128"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `check_make`

```python
check_make() → DependencyInfo
```

Check for Make build tool. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L153"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `check_nodejs`

```python
check_nodejs() → DependencyInfo
```

Check for Node.js (required for Mermaid diagrams). 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L207"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `check_python`

```python
check_python() → DependencyInfo
```

Check for Python (should already be available). 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L180"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `check_r`

```python
check_r() → DependencyInfo
```

Check for R (optional, for R figure scripts). 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L275"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_missing_optional_dependencies`

```python
get_missing_optional_dependencies() → list[DependencyInfo]
```

Get list of missing optional dependencies. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L271"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_missing_required_dependencies`

```python
get_missing_required_dependencies() → list[DependencyInfo]
```

Get list of missing required dependencies. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L279"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `has_all_required_dependencies`

```python
has_all_required_dependencies() → bool
```

Check if all required dependencies are available. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message: str, level: str = 'INFO')
```

Log a message if verbose mode is enabled. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/dependency_checker.py#L283"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `print_dependency_report`

```python
print_dependency_report()
```

Print a comprehensive dependency report. 


---

## <kbd>class</kbd> `DependencyInfo`
Information about a system dependency. 





