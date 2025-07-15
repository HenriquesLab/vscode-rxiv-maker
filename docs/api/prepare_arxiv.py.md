<!-- markdownlint-disable -->

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/prepare_arxiv.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `prepare_arxiv.py`
Prepare arXiv submission package from Rxiv-Maker output. 

This script creates a clean, self-contained package suitable for arXiv submission by copying and modifying the necessary files to remove dependencies on minted and other shell-escape requiring packages. 

Usage:  python prepare_arxiv.py [--output-dir DIR] 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/prepare_arxiv.py#L20"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `prepare_arxiv_package`

```python
prepare_arxiv_package(
    output_dir='./output',
    arxiv_dir=None,
    manuscript_path=None
)
```

Prepare arXiv submission package. 



**Args:**
 
 - <b>`output_dir`</b> (str):  Path to the Rxiv-Maker output directory 
 - <b>`arxiv_dir`</b> (str):  Path where arXiv submission files will be created  If None, defaults to {output_dir}/arxiv_submission 
 - <b>`manuscript_path`</b> (str):  Path to the source manuscript directory  (for context and naming) 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/prepare_arxiv.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `verify_package`

```python
verify_package(arxiv_path, manuscript_path=None)
```

Verify that the arXiv package contains all necessary files. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/prepare_arxiv.py#L272"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `test_arxiv_compilation`

```python
test_arxiv_compilation(arxiv_path)
```

Test compilation of the arXiv package to ensure it builds correctly. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/prepare_arxiv.py#L391"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_zip_package`

```python
create_zip_package(
    arxiv_path,
    zip_filename='for_arxiv.zip',
    manuscript_path=None
)
```

Create a ZIP file for arXiv submission. 


---

<a href="https://github.com/henriqueslab/rxiv-maker/blob/main/src/py/commands/prepare_arxiv.py#L416"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `main`

```python
main()
```

Main entry point for preparing arXiv submission package. 


