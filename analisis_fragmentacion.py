#!/usr/bin/env python3
"""Atajo para correr mercadopublico.analisis_fragmentacion sin configurar PYTHONPATH.

Uso:  python analisis_fragmentacion.py [args...]
Equivale a:  PYTHONPATH=src python -m mercadopublico.analisis_fragmentacion
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mercadopublico.analisis_fragmentacion import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
