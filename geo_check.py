#!/usr/bin/env python3
"""Standalone script entrypoint for FastUp GAS CLI."""

import sys
from pathlib import Path

# Add package directory to path if running directly from repo
pkg_dir = Path(__file__).resolve().parent
if str(pkg_dir) not in sys.path:
    sys.path.insert(0, str(pkg_dir))

from fastup_gas.cli import main

if __name__ == "__main__":
    main()
