# Telemetry System

Real-time student progress tracking for AI Pros Bootcamp notebooks.

## Overview

The telemetry system tracks student activity in Jupyter/Colab notebooks and sends events to PostHog for analytics.

## Installation

```bash
# Install from GitHub
pip install git+https://github.com/FarisHijazi/ipynb-telemetry.git

# Or with uv
uv pip install git+https://github.com/FarisHijazi/ipynb-telemetry.git

# For development
cd notebooks/telemetry
uv pip install -e .
```

## Usage

### In Notebooks

```python
from ipynb_telemetry.bootstrap import setup_telemetry
setup_telemetry("notebook_id")
```

Or with custom config:

```python
setup_telemetry("notebook_id", host="...", api_key="...")
```

### For Notebook Generation

```python
from ipynb_telemetry.notebook_cells import get_telemetry_setup_cell

# Generate cell code for a notebook
cell_code = get_telemetry_setup_cell("D3_Datetimes")
```

## Package Structure

```
ipynb_telemetry/
├── __init__.py          # Empty (per project convention)
├── bootstrap.py         # Core telemetry logic
└── notebook_cells.py    # Cell code generators
```

## `setup_telemetry()` Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `notebook_id` | str | required | Unique notebook identifier |
| `host` | str | PostHog US | PostHog instance URL |
| `api_key` | str | project key | PostHog API key |

## Injected Globals

After `setup_telemetry()` runs, these are available globally:

- `STUDENT_NAME` - Normalized student name (e.g., "JOHN-DOE")
- `_cell(cell_id, code_preview)` - Track cell execution
- `tracked_test(name)` - Decorator for test functions
- `_telemetry_capture(event, props)` - Send custom events

## PostHog Configuration

- **Host**: `https://us.i.posthog.com`
- **API Key**: `phc_I7GaZ4p1Ox5PRM5egRrHFxz3ZCdh3zyKQ7B6jxJOWis`

## Events Tracked

### 1. Session Start

Sent when `setup_telemetry()` is called.

### 2. Cell Execution

Uses the `_cell()` function to track code cell runs:

```python
_cell("exercise_1", "# code preview...")
```

### 3. Test Results

The `@tracked_test` decorator wraps exercise test functions:

```python
@tracked_test("exercise_name")
def test_exercise():
    assert result == expected
    print("Passed!")
```

## Event Payload Structure

All events include:

```python
{
    "nb": "notebook_id",
    "sess": "abc12345",
    "student": "JOHN-DOE",
    "v": "1.0.0",
    # ... event-specific properties
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEMETRY_PACKAGE_NAME` | `ipynb-telemetry` | Package name |
| `TELEMETRY_PACKAGE_SPEC` | GitHub URL | pip install spec |

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .
```
