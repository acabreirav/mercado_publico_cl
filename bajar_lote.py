#!/usr/bin/env python3
"""Atajo Fase 1 — baja el detalle de muchas OC de un día (con pausas e idempotencia).

Uso:
    python bajar_lote.py --fecha 2024-03-04 --limit 200
    python bajar_lote.py --fecha 2024-03-04            # todo el día (respeta el tope)

Equivale a:  PYTHONPATH=src python -m mercadopublico.download_lote_detalles
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mercadopublico.download_lote_detalles import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
