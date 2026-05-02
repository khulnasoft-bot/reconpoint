#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reconPoint.settings")

    # Remote debug setup for Web GUI (manage.py runserver only)
    # Note: For daphne (ASGI), debugger is initialized in asgi.py
    try:
        from reconPoint.settings import UI_REMOTE_DEBUG
    except ImportError:
        ui_remote_debug = False
    else:
        ui_remote_debug = UI_REMOTE_DEBUG

    if ui_remote_debug and len(sys.argv) > 1 and sys.argv[1] == "runserver":
        try:
            from debugger_setup import setup_debugger

            setup_debugger()
        except ImportError:
            pass

    # List of commands that should not display the reconpoint artwork
    skip_art_commands = ["test", "dumpdata", "entrypoint_setup", "run_scheduled_scans", "generate_secator_api_key"]

    if all(cmd not in sys.argv for cmd in skip_art_commands):
        # show reconpoint artwork
        try:
            art_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "art", "reconPoint.txt")
            if os.path.exists(art_path):
                with open(art_path, "r", encoding="utf-8") as f:
                    print(f.read())
        except Exception:
            pass

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
