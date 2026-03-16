#!/usr/bin/env python
"""Arranca el servidor de desarrollo de Django."""
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "batalla_naval.settings")

    from django.core.management import execute_from_command_line

    argv = [sys.argv[0], "runserver"] + sys.argv[1:]
    execute_from_command_line(argv)
