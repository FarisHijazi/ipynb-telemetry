"""
ipynb-telemetry: Real-time student progress tracking for Jupyter/Colab notebooks.

Usage:
    from ipynb_telemetry import setup_telemetry
    setup_telemetry("notebook_id")
"""

from ipynb_telemetry.bootstrap import setup_telemetry

__version__ = "1.0.0"
__all__ = ["setup_telemetry", "__version__"]
