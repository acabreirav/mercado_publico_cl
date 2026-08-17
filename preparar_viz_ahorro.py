#!/usr/bin/env python3
"""Atajo para preparar el dataset del visual de ahorro (sin PYTHONPATH)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from mercadopublico.preparar_viz_ahorro import main  # noqa: E402
if __name__ == "__main__":
    raise SystemExit(main())
