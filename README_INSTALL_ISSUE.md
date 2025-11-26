# Installation Issue Fix - PyArrow Build Error

## Problem

When installing packages, you may see an error like:
```
error: subprocess-exited-with-error
× Building wheel for pyarrow (pyproject.toml) did not run successfully.
error: command 'cmake' failed: None
```

## Root Cause

This happens because:
1. **Python 3.14 is too new** - Pre-built wheels for pyarrow may not be available yet
2. **Building from source requires** CMake and Visual Studio Build Tools (C++ compiler)
3. **Client's PC doesn't have** these development tools installed

## Solutions (In Order of Recommendation)

### ✅ Solution 1: Use Python 3.11 or 3.12 (BEST OPTION)

**Why:** Python 3.11 and 3.12 have excellent pre-built wheel support for all packages.

**Steps:**
1. Download Python 3.11 or 3.12 from [python.org](https://www.python.org/downloads/)
2. During installation, **check "Add Python to PATH"**
3. Uninstall or don't use Python 3.14
4. Run the application again

**This is the easiest and most reliable solution!**

---

### Solution 2: Use the Installation Helper Script

**Steps:**
1. Double-click `install_packages.bat`
2. Follow the prompts
3. If it fails, it will give you specific instructions

---

### Solution 3: Install Visual Studio Build Tools

**Only if you must use Python 3.14:**

1. Download "Build Tools for Visual Studio" from:
   https://visualstudio.microsoft.com/downloads/
2. Run the installer
3. Select "Desktop development with C++" workload
4. Install (this is a large download, ~6GB)
5. Restart your computer
6. Run the application again

---

### Solution 4: Manual Installation via Command Prompt

1. Open Command Prompt in the project folder
2. Run these commands:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install --only-binary :all: pyarrow
python -m pip install streamlit pandas numpy prophet plotly openpyxl xlrd
```

3. If pyarrow fails, try:
```bash
python -m pip install pyarrow --no-build-isolation
```

---

## Quick Check: Which Python Version?

To check your Python version:
```bash
python --version
```

**Recommended:** Python 3.11.7 or Python 3.12.3

---

## Why This Happens

- **PyArrow** is a dependency of Prophet/pandas
- It's written in C++ and needs to be compiled
- Pre-built wheels (binary packages) avoid compilation
- Python 3.14 is too new → no wheels available → tries to build from source → needs C++ tools

---

## Still Having Issues?

1. Check Python version: `python --version`
2. Try Solution 1 (use Python 3.11/3.12) - it's the most reliable
3. See `INSTALL_FIX.txt` for more detailed troubleshooting

