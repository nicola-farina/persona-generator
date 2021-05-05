import os.path
from os.path import join, dirname

PROJECT_ROOT = os.path.dirname(os.path.abspath("../../../README.md"))


def get_full_path(path: str) -> str:
    return join(PROJECT_ROOT, path)