"""Permite `python -m src calcular --input ... --output ... [--politica ...] [--cambio ...]` (DT-003b).

O subcomando `calcular` e obrigatorio; delega a `cli.main` (mesma logica de
`python -m src.cli calcular ...`). A forma antiga `python -m src --input ...` (sem
o subcomando) passa a ser erro de uso do argparse (codigo 2).
"""

import sys

from src.cli import main

if __name__ == "__main__":
    sys.exit(main())
