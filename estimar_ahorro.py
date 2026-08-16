#!/usr/bin/env python3
"""Atajo para correr mercadopublico.estimar_ahorro sin configurar PYTHONPATH.

Uso:  python estimar_ahorro.py [args...]
Equivale a:  PYTHONPATH=src python -m mercadopublico.estimar_ahorro
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mercadopublico.estimar_ahorro import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
