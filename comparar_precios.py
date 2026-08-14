#!/usr/bin/env python3
"""Atajo Fase 1 — comparador de precios: mismo producto, precio por organismo.

Uso:
    python comparar_precios.py             # lee data/interim/items.csv -> ranking

Equivale a:  PYTHONPATH=src python -m mercadopublico.comparador
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mercadopublico.comparador import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
