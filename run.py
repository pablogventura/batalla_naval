#!/usr/bin/env python
"""Arranca el servidor de desarrollo de Django."""
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "batalla_naval.settings")

    from django.core.management import execute_from_command_line

    port = sys.argv[1] if len(sys.argv) > 1 else "5000"
    argv = [sys.argv[0], "runserver", port]
    execute_from_command_line(argv)
