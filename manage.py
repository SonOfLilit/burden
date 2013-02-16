#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    BASE = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.join(BASE, "local_apps"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projects.burden.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
