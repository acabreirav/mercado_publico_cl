#!/usr/bin/env python3
"""Atajo Fase 1 — aplana los JSON crudos de OC a una tabla de ítems (CSV).

Uso:
    python parsear_items.py                    # lee data/raw/**/*.json -> data/interim/items.csv

Equivale a:  PYTHONPATH=src python -m mercadopublico.parse_items
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mercadopublico.parse_items import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
