#!/usr/bin/env python3
"""Atajo para correr la ingesta de Fase 0 sin configurar PYTHONPATH.

Uso:
    python bajar_ordenes.py                    # baja las órdenes de compra de AYER
    python bajar_ordenes.py --fecha 2024-03-04 # una fecha específica
    python bajar_ordenes.py --estado todos     # por estado, día actual

Equivale a:  PYTHONPATH=src python -m mercadopublico.download_ordenes_dia
"""

import sys
from pathlib import Path

# Agrega src/ al path para poder importar el paquete sin instalar nada.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mercadopublico.download_ordenes_dia import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
