# Telemetry System

Real-time student progress tracking for AI Pros Bootcamp notebooks.

## Overview

The telemetry system tracks student activity in Jupyter/Colab notebooks and sends events to PostHog for analytics.

## Architecture

The telemetry is split into two parts:

1. **`bootstrap.py`** - Standalone script hosted on GitHub, fetched and executed at runtime
2. **`notebook_cells.py`** - Generator that creates the fetch-and-execute cell for notebooks

This design allows updating telemetry logic without regenerating notebooks.

## Remote Bootstrap

Notebooks fetch and execute `bootstrap.py` from GitHub:

```python
import requests
exec(requests.get("https://raw.githubusercontent.com/FarisHijazi/ipynb-telemetry/refs/heads/master/src/bootstrap.py").text)
setup_telemetry("notebook_id")
```

### `setup_telemetry()` Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `notebook_id` | str | required | Unique notebook identifier |
| `host` | str | PostHog US | PostHog instance URL |
| `api_key` | str | project key | PostHog API key |
| `skip_name_prompt` | bool | False | Skip interactive name input |
| `student_name` | str | None | Pre-set name (requires skip_name_prompt) |

### Injected Globals

After `setup_telemetry()` runs, these are available globally:

- `STUDENT_NAME` - Normalized student name (e.g., "JOHN-DOE")
- `_cell(cell_id, code_preview)` - Track cell execution
- `tracked_test(name)` - Decorator for test functions
- `_telemetry_capture(event, props)` - Send custom events

## PostHog Configuration

- **Host**: `https://us.i.posthog.com`
- **API Key**: `phc_I7GaZ4p1Ox5PRM5egRrHFxz3ZCdh3zyKQ7B6jxJOWis`

## Student Name Input

Each notebook starts with a name input cell that:

1. Prompts for **first name** and **last name**
2. Validates **English characters only** (A-Z, a-z, spaces, hyphens)
3. **Normalizes to UPPERCASE**
4. Shows clear error if no name entered
5. Stores as `STUDENT_ID` in format `FIRSTNAME_LASTNAME`

```python
import re

first_name = input("Enter your FIRST NAME (English only): ").strip()
last_name = input("Enter your LAST NAME (English only): ").strip()

# Validation
pattern = r'^[A-Za-z\s\-]+$'
if not first_name or not last_name:
    raise ValueError("ERROR: Both first and last name are required!")
if not re.match(pattern, first_name) or not re.match(pattern, last_name):
    raise ValueError("ERROR: Names must contain only English letters!")

# Normalize to uppercase
STUDENT_ID = f"{first_name.upper()}_{last_name.upper()}"
print(f"Welcome, {STUDENT_ID}!")
```

## Events Tracked

### 1. Cell Execution (Every Cell)

Uses IPython hooks to capture ALL cell executions:

```python
from IPython import get_ipython

def pre_run_cell(info):
    # Capture cell code before execution
    global _current_cell_code
    _current_cell_code = info.raw_cell

def post_run_cell(result):
    # Send telemetry after execution
    send_event("cell_executed", {
        "code": _current_cell_code,
        "output": str(result.result) if result.result else "",
        "success": result.success,
        "error": str(result.error_in_exec) if result.error_in_exec else None
    })

ip = get_ipython()
ip.events.register('pre_run_cell', pre_run_cell)
ip.events.register('post_run_cell', post_run_cell)
```

### 2. Test Results

The `@tracked_test` decorator wraps exercise test functions:

```python
def tracked_test(test_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                send_event("test_passed", {"test": test_name})
                print(f"TEST PASSED: {test_name}")
                return result
            except AssertionError as e:
                send_event("test_failed", {"test": test_name, "error": str(e)})
                print(f"TEST FAILED: {test_name} - {e}")
                raise
        return wrapper
    return decorator
```

### 3. Solution Peeks

When students expand a `<details>` solution block, it's tracked via JavaScript:

```javascript
document.querySelectorAll('details').forEach(el => {
    el.addEventListener('toggle', () => {
        if (el.open) {
            // Send peek event to PostHog
        }
    });
});
```

### 4. Focus/Blur Events

Tracks when students switch away from the notebook:

```javascript
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Send blur event
    } else {
        // Send focus event
    }
});
```

### 5. Paste Detection

Detects when students paste code:

```javascript
document.addEventListener('paste', (e) => {
    // Send paste event with pasted text length
});
```

## Event Payload Structure

All events include:

```python
{
    "student_id": STUDENT_ID,      # e.g., "JOHN_DOE"
    "notebook": NOTEBOOK_NAME,      # e.g., "D1_Python_Tooling"
    "timestamp": datetime.now().isoformat(),
    "event_type": "...",           # cell_executed, test_passed, etc.
    "properties": { ... }          # Event-specific data
}
```

## Collapsible Setup Cells

Telemetry code uses `#@title` for Colab collapsibility:

```python
#@title Setup: Telemetry (Run this cell first)
# ... telemetry code ...
```

This keeps the notebook clean while ensuring tracking runs.

## Privacy Considerations

- Only tracks learning progress, not personal data beyond name
- Code and outputs are captured for educational analytics
- No keystroke logging or screen recording
- Students see their name displayed after input

## Viewing Analytics

Access PostHog dashboard to view:

- Student progress through exercises
- Common errors and failure points
- Time spent on each notebook
- Solution peek patterns
- Engagement metrics (focus/blur)
