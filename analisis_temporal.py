#!/usr/bin/env python3
"""Atajo para el análisis temporal de fragmentación (sin PYTHONPATH)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from mercadopublico.analisis_temporal import main  # noqa: E402
if __name__ == "__main__":
    raise SystemExit(main())
