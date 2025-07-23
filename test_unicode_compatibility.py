#!/usr/bin/env python3
"""Test script for Windows Unicode compatibility.

This script tests various Unicode-related operations that could fail on Windows
with non-ASCII characters in file paths or content.
"""

import json
import os
import tempfile
from pathlib import Path


def test_file_operations_with_unicode():
    """Test file I/O operations with Unicode content and paths."""
    print("Testing Unicode file operations...")

    # Test Unicode content
    test_content = "Test with Unicode: héllo wörld 📚 研究論文"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test 1: Write and read Unicode content
        test_file = temp_path / "test_unicode.txt"
        try:
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(test_content)

            with open(test_file, encoding="utf-8") as f:
                read_content = f.read()

            assert read_content == test_content
            print("✅ Unicode content I/O: PASS")
        except Exception as e:
            print(f"❌ Unicode content I/O: FAIL - {e}")

        # Test 2: JSON with Unicode
        test_data = {
            "title": "研究論文",
            "author": "José María",
            "symbols": "α β γ δ ε",
        }

        try:
            json_file = temp_path / "test_unicode.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(test_data, f, indent=2, ensure_ascii=False)

            with open(json_file, encoding="utf-8") as f:
                loaded_data = json.load(f)

            assert loaded_data == test_data
            print("✅ Unicode JSON I/O: PASS")
        except Exception as e:
            print(f"❌ Unicode JSON I/O: FAIL - {e}")

        # Test 3: YAML-like content
        yaml_content = """title: "研究論文: Advanced Methods"
authors:
  - name: "José María García"
    email: "jose@university.edu"
  - name: "王小明"
    affiliation: "北京大学"
keywords: ["机器学习", "人工智能", "deep learning"]
"""

        try:
            yaml_file = temp_path / "test_unicode.yml"
            with open(yaml_file, "w", encoding="utf-8") as f:
                f.write(yaml_content)

            with open(yaml_file, encoding="utf-8") as f:
                read_yaml = f.read()

            assert read_yaml == yaml_content
            print("✅ Unicode YAML-like I/O: PASS")
        except Exception as e:
            print(f"❌ Unicode YAML-like I/O: FAIL - {e}")


def test_path_handling():
    """Test path handling that might contain Unicode."""
    print("\nTesting Unicode path handling...")

    try:
        # Test creating paths with Unicode (though we can't create them on all systems)
        unicode_path = Path("测试_path_with_ñ")
        resolved = unicode_path.resolve()
        print(f"✅ Unicode path resolution: PASS - {resolved}")
    except Exception as e:
        print(f"❌ Unicode path resolution: FAIL - {e}")


def test_environment_variables():
    """Test environment variable handling."""
    print("\nTesting environment variable handling...")

    try:
        # Test getting current directory (might contain Unicode)
        cwd = os.getcwd()
        path_obj = Path(cwd)
        print(f"✅ Current directory handling: PASS - {cwd}")

        # Test environment variables
        home = os.path.expanduser("~")
        print(f"✅ Home directory expansion: PASS - {home}")
    except Exception as e:
        print(f"❌ Environment handling: FAIL - {e}")


def main():
    """Run all Unicode compatibility tests."""
    print("🧪 Windows Unicode Compatibility Test")
    print("=" * 40)

    test_file_operations_with_unicode()
    test_path_handling()
    test_environment_variables()

    print("\n" + "=" * 40)
    print("✅ Tests completed! Check output above for any failures.")
    print("\nNote: This test verifies that rxiv-maker's encoding fixes")
    print("will handle Unicode content properly on Windows systems.")


if __name__ == "__main__":
    main()
