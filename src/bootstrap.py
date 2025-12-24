"""
Bootcamp Telemetry Bootstrap Script.

This script is designed to be fetched and executed from a raw GitHub URL.
It sets up student tracking, cell execution tracking, and test result tracking.

Usage in notebook:
    import requests; exec(requests.get("https://raw.githubusercontent.com/FarisHijazi/ai-pros/master/notebooks/telemetry/bootstrap.py").text)
    setup_telemetry("notebook_id")

Or with custom config:
    setup_telemetry("notebook_id", host="...", api_key="...")

Version: 1.0.0
"""

__version__ = "1.0.0"

# === DEFAULT CONFIG ===
_DEFAULT_HOST = "https://us.i.posthog.com"
_DEFAULT_API_KEY = "phc_I7GaZ4p1Ox5PRM5egRrHFxz3ZCdh3zyKQ7B6jxJOWis"


def setup_telemetry(
    notebook_id: str,
    *,
    host: str = None,
    api_key: str = None,
    skip_name_prompt: bool = False,
    student_name: str = None,
) -> dict:
    """
    Initialize telemetry for a notebook.

    Args:
        notebook_id: Unique identifier for this notebook (e.g., "D3_Datetimes")
        host: PostHog host URL (default: us.i.posthog.com)
        api_key: PostHog project API key
        skip_name_prompt: If True, skip the interactive name prompt
        student_name: Pre-set student name (requires skip_name_prompt=True)

    Returns:
        dict with: student_name, session_id, _cell, tracked_test functions
    """
    import re
    import time
    import uuid
    from functools import wraps

    # Resolve config
    _host = host or _DEFAULT_HOST
    _api_key = api_key or _DEFAULT_API_KEY

    # === STUDENT NAME ===
    if skip_name_prompt and student_name:
        STUDENT_NAME = student_name.upper().strip()
    else:
        print("=" * 40)
        _first = input("Enter FIRST NAME (English): ").strip()
        _last = input("Enter LAST NAME (English): ").strip()

        if not _first:
            _first = input("First Name: ").strip()
        if not _last:
            _last = input("Last Name: ").strip()

        if len(_first) < 2 or len(_last) < 2:
            raise ValueError("Name too short! Run this cell again.")
        if not re.match(r"^[A-Za-z\s\-]+$", _first) or not re.match(
            r"^[A-Za-z\s\-]+$", _last
        ):
            raise ValueError("English letters only! Run this cell again.")

        STUDENT_NAME = f"{_first.upper().strip()}-{_last.upper().strip()}"

    print(f"Welcome, {STUDENT_NAME}!")

    # === POSTHOG SETUP ===
    try:
        import posthog
    except ImportError:
        import subprocess
        import sys

        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "posthog", "-q"]
        )
        import posthog

    _session = uuid.uuid4().hex[:8]
    _student_id = f"{STUDENT_NAME}-bootcamp"
    posthog.project_api_key = _api_key
    posthog.host = _host

    _attempts = {}
    _cell_num = 0

    def _capture(event: str, properties: dict = None):
        """Send event to PostHog."""
        try:
            posthog.capture(
                _student_id,
                event,
                {
                    "nb": notebook_id,
                    "sess": _session,
                    "student": STUDENT_NAME,
                    "v": __version__,
                    **(properties or {}),
                },
            )
        except Exception:
            pass

    def _cell(cell_id: str, code_preview: str = ""):
        """Track cell execution. Call at START of every code cell."""
        nonlocal _cell_num
        _cell_num += 1
        _capture(
            "cell",
            {"cell_id": cell_id, "cell_num": _cell_num, "code": code_preview[:500]},
        )

    def tracked_test(exercise_name: str):
        """Decorator to track test function results."""

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                _attempts[exercise_name] = _attempts.get(exercise_name, 0) + 1
                start_time = time.time()
                ok = False
                err = None
                try:
                    result = func(*args, **kwargs)
                    ok = True
                    return result
                except Exception as e:
                    err = str(e)[:200]
                    raise
                finally:
                    _capture(
                        "test",
                        {
                            "ex": exercise_name,
                            "ok": ok,
                            "try": _attempts[exercise_name],
                            "ms": int((time.time() - start_time) * 1000),
                            "err": err,
                        },
                    )

            return wrapper

        return decorator

    # Send start event
    _capture("start")
    print(f"Ready! {STUDENT_NAME} | Session: {_session}")

    # Inject into global namespace for notebook use
    import builtins

    builtins.STUDENT_NAME = STUDENT_NAME
    builtins._cell = _cell
    builtins.tracked_test = tracked_test
    builtins._telemetry_capture = _capture

    return {
        "student_name": STUDENT_NAME,
        "session_id": _session,
        "_cell": _cell,
        "tracked_test": tracked_test,
        "_capture": _capture,
        "version": __version__,
    }


# Convenience: if this script is exec()'d directly, expose setup_telemetry
# in the calling namespace
if __name__ != "__main__":
    # When exec()'d, make setup_telemetry available
    pass
