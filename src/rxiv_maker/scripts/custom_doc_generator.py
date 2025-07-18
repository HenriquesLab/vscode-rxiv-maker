#!/usr/bin/env python
"""Custom documentation generator.

This script generates markdown documentation for Python modules by inspecting
classes, methods, functions and their docstrings. It uses Python's introspection
capabilities to extract information and create well-formatted markdown files.
"""

import importlib.util
import inspect
import os
import sys


def generate_markdown_doc(module_name, module, output_dir):
    """Generate markdown documentation for a module.

    Args:
        module_name: The name of the module
        module: The module object to document
        output_dir: Directory where documentation files will be written
    """
    doc = f"# {module_name}\n\n"

    if module.__doc__:
        doc += f"{module.__doc__.strip()}\n\n"

    # Get all classes and functions
    members = inspect.getmembers(module)

    # Document classes
    classes = [
        member
        for member in members
        if inspect.isclass(member[1]) and member[1].__module__ == module.__name__
    ]
    if classes:
        doc += "## Classes\n\n"
        for name, cls in classes:
            doc += f"### {name}\n\n"
            if cls.__doc__:
                doc += f"{cls.__doc__.strip()}\n\n"

            # Get methods
            methods = inspect.getmembers(cls, predicate=inspect.isfunction)
            if methods:
                doc += "#### Methods\n\n"
                for method_name, method in methods:
                    if not method_name.startswith("_") or method_name == "__init__":
                        doc += f"##### `{method_name}`\n\n"
                        if method.__doc__:
                            doc += f"{method.__doc__.strip()}\n\n"

                        # Get signature
                        try:
                            signature = inspect.signature(method)
                            doc += f"```python\n{method_name}{signature}\n```\n\n"
                        except ValueError:
                            pass

    # Document functions
    functions = [
        member
        for member in members
        if inspect.isfunction(member[1]) and member[1].__module__ == module.__name__
    ]
    if functions:
        doc += "## Functions\n\n"
        for name, func in functions:
            if not name.startswith("_"):
                doc += f"### {name}\n\n"
                if func.__doc__:
                    doc += f"{func.__doc__.strip()}\n\n"

                # Get signature
                try:
                    signature = inspect.signature(func)
                    doc += f"```python\n{name}{signature}\n```\n\n"
                except ValueError:
                    pass

    # Write to file
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, f"{module_name}.md"), "w") as f:
        f.write(doc)


def process_directory(dir_path, output_dir, base_package=""):
    """Process a directory and its subdirectories for Python modules.

    Args:
        dir_path: Path to the directory containing Python modules
        output_dir: Directory where documentation files will be written
        base_package: Base package name for imports (used for recursion)
    """
    for item in os.listdir(dir_path):
        path = os.path.join(dir_path, item)

        # Skip directories that start with underscore, like __pycache__
        if os.path.isdir(path) and not item.startswith("_"):
            subpackage = f"{base_package}.{item}" if base_package else item
            process_directory(path, output_dir, subpackage)

        elif item.endswith(".py") and not item.startswith("_"):
            module_name = item[:-3]  # Remove .py extension
            full_module_name = (
                f"{base_package}.{module_name}" if base_package else module_name
            )

            try:
                # Import the module
                spec = importlib.util.spec_from_file_location(full_module_name, path)
                if spec is None:
                    print(f"Failed to load spec for {path}")
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Generate documentation
                generate_markdown_doc(module_name, module, output_dir)
                print(f"Generated documentation for {full_module_name}")
            except Exception as e:
                print(f"Failed to generate docs for {full_module_name}: {e}")


def main():
    """Main entry point for the documentation generator."""
    # Ensure we can import modules from the current directory
    sys.path.insert(0, os.path.abspath("."))

    src_dir = "src/py"
    output_dir = "docs/api"

    # Process the main directory
    process_directory(src_dir, output_dir)

    # Generate index.md
    with open(os.path.join(output_dir, "index.md"), "w") as f:
        f.write("# API Documentation\n\n")
        f.write("Welcome to the API documentation for rxiv-maker.\n\n")
        f.write("## Modules\n\n")

        # List all generated markdown files
        for item in sorted(os.listdir(output_dir)):
            if item.endswith(".md") and item != "index.md":
                module_name = item[:-3]  # Remove .md extension
                f.write(f"- [{module_name}]({item})\n")

    print(f"Documentation index created at {os.path.join(output_dir, 'index.md')}")


if __name__ == "__main__":
    main()
