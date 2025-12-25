"""
Bootcamp Telemetry Bootstrap.

Sets up student tracking, cell execution tracking, and test result tracking.

Usage:
    from ipynb_telemetry import setup_telemetry
    setup_telemetry("notebook_id")
"""

import builtins
import re
import time
import uuid
from functools import wraps

import posthog

__version__ = "1.0.0"

# === DEFAULT CONFIG ===
_DEFAULT_HOST = "https://us.i.posthog.com"
_DEFAULT_API_KEY = "phc_I7GaZ4p1Ox5PRM5egRrHFxz3ZCdh3zyKQ7B6jxJOWis"


def setup_telemetry(
    notebook_id: str,
    *,
    host: str = None,
    api_key: str = None,
) -> dict:
    """
    Initialize telemetry for a notebook. Prompts for student name.

    Args:
        notebook_id: Unique identifier for this notebook (e.g., "D3_Datetimes")
        host: PostHog host URL (default: us.i.posthog.com)
        api_key: PostHog project API key

    Returns:
        dict with: student_name, session_id, _cell, tracked_test functions
    """
    # Resolve config
    _host = host or _DEFAULT_HOST
    _api_key = api_key or _DEFAULT_API_KEY

    # === STUDENT NAME (REQUIRED) ===
    print("=" * 40)
    first = input("Enter FIRST NAME (English): ").strip()
    last = input("Enter LAST NAME (English): ").strip()

    if not first or not last:
        raise ValueError("Both first and last name are REQUIRED! Run this cell again.")
    if len(first) < 2 or len(last) < 2:
        raise ValueError("Name too short! Run this cell again.")
    if not re.match(r"^[A-Za-z\s\-]+$", first) or not re.match(r"^[A-Za-z\s\-]+$", last):
        raise ValueError("English letters only! Run this cell again.")

    STUDENT_NAME = f"{first.upper()}-{last.upper()}"
    print(f"Welcome, {STUDENT_NAME}!")

    # === POSTHOG SETUP ===
    session = uuid.uuid4().hex[:8]
    posthog.project_api_key = _api_key
    posthog.host = _host

    attempts = {}
    cell_num = 0

    def _capture(event: str, properties: dict = None):
        """Send event to PostHog."""
        try:
            posthog.capture(
                STUDENT_NAME,  # Use student name as user ID
                event,
                {"nb": notebook_id, "sess": session, "v": __version__, **(properties or {})},
            )
        except Exception:
            pass

    def _cell(cell_id: str, code_preview: str = ""):
        """Track cell execution."""
        nonlocal cell_num
        cell_num += 1
        _capture("cell", {"cell_id": cell_id, "cell_num": cell_num, "code": code_preview[:500]})

    def tracked_test(exercise_name: str):
        """Decorator to track test function results."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                attempts[exercise_name] = attempts.get(exercise_name, 0) + 1
                start = time.time()
                ok, err = False, None
                try:
                    result = func(*args, **kwargs)
                    ok = True
                    return result
                except Exception as e:
                    err = str(e)[:200]
                    raise
                finally:
                    _capture("test", {
                        "ex": exercise_name,
                        "ok": ok,
                        "try": attempts[exercise_name],
                        "ms": int((time.time() - start) * 1000),
                        "err": err,
                    })
            return wrapper
        return decorator

    # Send start event
    _capture("start")
    print(f"Ready! Session: {session}")

    # Inject into global namespace
    builtins.STUDENT_NAME = STUDENT_NAME
    builtins._cell = _cell
    builtins.tracked_test = tracked_test
    builtins._telemetry_capture = _capture

    return {
        "student_name": STUDENT_NAME,
        "session_id": session,
        "_cell": _cell,
        "tracked_test": tracked_test,
        "_capture": _capture,
        "version": __version__,
    }
