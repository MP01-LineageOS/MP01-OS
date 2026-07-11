#!/usr/bin/env -S /usr/bin/python3.14 -I -S
"""Minimal isolated launcher; the .sh name is retained for operator continuity."""

from pathlib import Path
import runpy


runpy.run_path(str(Path(__file__).resolve().with_name("audit.py")), run_name="__main__")
