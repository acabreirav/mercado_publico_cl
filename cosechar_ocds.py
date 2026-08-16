#!/usr/bin/env python3
"""Atajo — cosecha TODOS los registros OCDS de un año/mes/tipo (API paginada).

Uso:
    python cosechar_ocds.py --tipo tratodirecto --anio 2020 --meses 01
    python cosechar_ocds.py --tipo todos --anio 2024 --meses 01,02,03
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mercadopublico.cosechar_ocds import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
