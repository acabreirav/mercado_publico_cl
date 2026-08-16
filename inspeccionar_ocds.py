#!/usr/bin/env python3
"""Atajo para correr mercadopublico.inspeccionar_ocds sin configurar PYTHONPATH.

Uso:  python inspeccionar_ocds.py [args...]
Equivale a:  PYTHONPATH=src python -m mercadopublico.inspeccionar_ocds
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mercadopublico.inspeccionar_ocds import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
