#!/usr/bin/env python
import os
import sys

import structlog
import builtins
from dotenv import load_dotenv

# Determine the paths to the .env file
# print(os.path.dirname())
print(os.path.dirname(os.path.dirname(__file__)))
print(__file__)
dot_env_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
print(dot_env_path)
load_dotenv(dot_env_path)


# current_directory = os.getcwd()
# print("Current Directory (os):", current_directory)
# dot_env_path = os.path.join(current_directory, 'config', '.env')
# load_dotenv(dot_env_path)


builtins.logger = structlog.get_logger(__name__)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
