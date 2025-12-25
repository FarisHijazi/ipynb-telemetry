"""
Notebook cell generators for bootcamp telemetry.

This module provides functions that return code strings to inject into notebooks.
The telemetry package is installed via pip and imported directly.

Usage:
    from ipynb_telemetry.notebook_cells import get_telemetry_setup_cell
"""

import os

# === PACKAGE CONFIG ===
PACKAGE_NAME = os.getenv("TELEMETRY_PACKAGE_NAME", "ipynb-telemetry")
PACKAGE_SPEC = os.getenv(
    "TELEMETRY_PACKAGE_SPEC",
    "git+https://github.com/FarisHijazi/ipynb-telemetry.git",
)


def get_telemetry_setup_cell(notebook_id: str) -> str:
    """Return the student name input + telemetry setup cell code.

    This generates a cell that:
    1. Installs ipynb-telemetry package via pip (if not already installed)
    2. Imports setup_telemetry from the package
    3. Calls setup_telemetry() with the notebook_id
    """
    return f'''#@title Enter Your Name (REQUIRED)
# Install telemetry package if needed
try:
    from ipynb_telemetry.bootstrap import setup_telemetry
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "{PACKAGE_SPEC}", "-q"])
    from ipynb_telemetry.bootstrap import setup_telemetry

setup_telemetry("{notebook_id}")
'''
