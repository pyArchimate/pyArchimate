"""File readers for pyArchimate.

Provides readers for importing ArchiMate models from various file formats
including .archimate (Archi XML), ArisAML (ARIS), and other formats.
"""
# ruff: noqa: N999  # legacy module name preserved for API compatibility
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
