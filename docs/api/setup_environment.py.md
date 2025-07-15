<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/setup_environment.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `setup_environment.py`
Environment setup command for Rxiv-Maker. 

This script handles cross-platform environment setup including: 
- uv installation 
- Virtual environment management 
- Dependency installation 
- Environment validation 
- System dependency checking 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/setup_environment.py#L301"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `main`

```python
main()
```

Main entry point for environment setup. 


---

## <kbd>class</kbd> `EnvironmentSetup`
Handle environment setup operations. 

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/setup_environment.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    reinstall: bool = False,
    verbose: bool = False,
    check_system_deps: bool = True
)
```

Initialize environment setup. 



**Args:**
 
 - <b>`reinstall`</b>:  Whether to reinstall (remove existing .venv) 
 - <b>`verbose`</b>:  Whether to show verbose output 
 - <b>`check_system_deps`</b>:  Whether to check system dependencies 




---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/setup_environment.py#L146"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `check_system_dependencies`

```python
check_system_dependencies() → bool
```

Check system dependencies and provide guidance. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/setup_environment.py#L59"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `check_uv_installation`

```python
check_uv_installation() → bool
```

Check if uv is installed and working. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/setup_environment.py#L74"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `install_uv`

```python
install_uv() → bool
```

Install uv package manager. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/setup_environment.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `log`

```python
log(message: str, level: str = 'INFO')
```

Log a message with appropriate formatting. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/setup_environment.py#L104"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `remove_existing_venv`

```python
remove_existing_venv() → bool
```

Remove existing virtual environment. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/setup_environment.py#L252"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `run_setup`

```python
run_setup() → bool
```

Run the complete setup process. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/setup_environment.py#L209"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `show_completion_message`

```python
show_completion_message()
```

Show completion message with next steps. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/setup_environment.py#L118"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `sync_dependencies`

```python
sync_dependencies() → bool
```

Sync dependencies using uv. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/setup_environment.py#L183"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `validate_environment`

```python
validate_environment() → bool
```

Validate the environment setup. 


