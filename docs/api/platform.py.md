<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `platform.py`
Platform detection and compatibility utilities for Rxiv-Maker. 

This module provides cross-platform utilities for detecting the operating system and handling platform-specific operations like path management and command execution. 

**Global Variables**
---------------
- **platform_detector**

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L197"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_platform`

```python
get_platform() → str
```

Get the current platform name. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L202"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_python_command`

```python
get_python_command() → str
```

Get the Python command to use. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L207"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `is_windows`

```python
is_windows() → bool
```

Check if running on Windows. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L212"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `is_unix_like`

```python
is_unix_like() → bool
```

Check if running on Unix-like system. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L217"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `run_platform_command`

```python
run_platform_command(cmd: str, **kwargs) → CompletedProcess
```

Run a command with platform-appropriate settings. 


---

## <kbd>class</kbd> `PlatformDetector`
Detect and manage platform-specific operations. 

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__()
```

Initialize platform detector. 


---

#### <kbd>property</kbd> platform

Get the current platform name. 

---

#### <kbd>property</kbd> python_cmd

Get the Python command to use. 



---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L122"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `check_command_exists`

```python
check_command_exists(command: str) → bool
```

Check if a command exists on the system. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L169"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `copy_file`

```python
copy_file(src: Path, dst: Path) → bool
```

Copy a file with error handling. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L126"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_env_file_content`

```python
get_env_file_content(env_file: Path = PosixPath('.env')) → dict
```

Read environment file content if it exists. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_null_device`

```python
get_null_device() → str
```

Get the null device path for the current platform. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L77"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_path_separator`

```python
get_path_separator() → str
```

Get the path separator for the current platform. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L98"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_venv_activate_path`

```python
get_venv_activate_path() → Optional[str]
```

Get the virtual environment activation script path. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L85"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_venv_python_path`

```python
get_venv_python_path() → Optional[str]
```

Get the virtual environment Python path. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L144"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `install_uv`

```python
install_uv() → bool
```

Install uv package manager for the current platform. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L69"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `is_linux`

```python
is_linux() → bool
```

Check if running on Linux. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `is_macos`

```python
is_macos() → bool
```

Check if running on macOS. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L73"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `is_unix_like`

```python
is_unix_like() → bool
```

Check if running on Unix-like system (macOS or Linux). 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `is_windows`

```python
is_windows() → bool
```

Check if running on Windows. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L178"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `make_executable`

```python
make_executable(path: Path) → bool
```

Make a file executable (Unix-like systems only). 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `remove_directory`

```python
remove_directory(path: Path) → bool
```

Remove a directory with platform-appropriate method. 

---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/utils/platform.py#L111"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `run_command`

```python
run_command(cmd: str, shell: bool = True, **kwargs) → CompletedProcess
```

Run a command with platform-appropriate settings. 


