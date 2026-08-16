#!/usr/bin/env python3
"""Atajo para correr mercadopublico.parse_ocds sin configurar PYTHONPATH.

Uso:  python parse_ocds.py [args...]
Equivale a:  PYTHONPATH=src python -m mercadopublico.parse_ocds
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mercadopublico.parse_ocds import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
