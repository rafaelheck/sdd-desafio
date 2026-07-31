"""Permite `python -m src --input ... --output ... [--politica ...] [--cambio ...]` (DT-003)."""

import sys

from src.cli import main

if __name__ == "__main__":
    sys.exit(main())
