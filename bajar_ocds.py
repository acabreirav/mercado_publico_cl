#!/usr/bin/env python3
"""Atajo — descarga un archivo masivo OCDS/CSV desde su URL.

Uso:
    python bajar_ocds.py --url "<URL del portal datos-abiertos>"

Luego:
    python -m mercadopublico.inspeccionar_ocds --archivo data/raw/ocds/<archivo>
    python -m mercadopublico.parse_ocds --entrada data/raw/ocds/<archivo_o_carpeta>
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mercadopublico.download_ocds import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
