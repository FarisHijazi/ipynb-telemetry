"""
Notebook cell generators for bootcamp telemetry.

This module provides functions that return code strings to inject into notebooks.
The actual telemetry logic lives in bootstrap.py which is fetched from GitHub.

Usage:
    from telemetry.notebook_cells import get_telemetry_setup_cell
"""

import os

# === TELEMETRY CONFIG ===
GITHUB_RAW_URL = os.getenv(
    "TELEMETRY_BOOTSTRAP_URL",
    "https://raw.githubusercontent.com/FarisHijazi/ipynb-telemetry/refs/heads/master/src/bootstrap.py",
)


def get_telemetry_setup_cell(notebook_id: str) -> str:
    """Return the student name input + telemetry setup cell code.

    This generates a cell that:
    1. Installs requests if needed
    2. Fetches bootstrap.py from GitHub
    3. Executes it to get setup_telemetry()
    4. Calls setup_telemetry() with the notebook_id
    """
    return f'''#@title Enter Your Name (REQUIRED)
# Fetch and run telemetry bootstrap from GitHub
_url = "{GITHUB_RAW_URL}"
try:
    import requests
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

_code = requests.get(_url, timeout=10).text
exec(_code)
setup_telemetry("{notebook_id}")
'''
