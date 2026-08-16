#!/usr/bin/env python3
"""Atajo para correr mercadopublico.preparar_viz sin configurar PYTHONPATH.

Uso:  python preparar_viz.py [args...]
Equivale a:  PYTHONPATH=src python -m mercadopublico.preparar_viz
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mercadopublico.preparar_viz import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
