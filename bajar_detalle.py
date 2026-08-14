#!/usr/bin/env python3
"""Atajo para bajar el DETALLE de una orden de compra sin configurar PYTHONPATH.

Uso:
    python bajar_detalle.py --codigo 1001546-22-AG24

Equivale a:  PYTHONPATH=src python -m mercadopublico.download_detalle_oc
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mercadopublico.download_detalle_oc import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
