"""Inspecciona un archivo OCDS/CSV descargado para descubrir su shape REAL.

Igual que el inspector de Fase 0, pero para los archivos masivos. No transforma:
solo reporta la estructura para que ajustemos `parse_ocds.py` a lo que de verdad
publica ChileCompra (el estándar OCDS admite extensiones, así que hay que mirar).

Uso:
    python -m mercadopublico.inspeccionar_ocds --archivo data/raw/ocds/<archivo>.json
    python -m mercadopublico.inspeccionar_ocds --archivo <archivo>.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def _keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return list(obj.keys())
    if isinstance(obj, list):
        return f"[lista de {len(obj)}]"
    return type(obj).__name__


def inspeccionar_json(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    print(f"Tipo de nivel superior: {_keys(data)}")

    releases = None
    if isinstance(data, dict):
        if "releases" in data:
            releases = data["releases"]; print(f"Es un RELEASE package. releases: {len(releases)}")
        elif "records" in data:
            recs = data["records"]; print(f"Es un RECORD package. records: {len(recs)}")
            if recs and isinstance(recs[0], dict):
                comp = recs[0].get("compiledRelease") or (recs[0].get("releases") or [{}])[0]
                releases = [comp] if comp else None

    if not releases:
        print("No encontré 'releases'/'records'. Muestra cruda (2000 chars):")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
        return

    r = releases[0]
    print(f"\n-- Claves de un release --\n{_keys(r)}")
    for k in ("buyer", "parties", "tender", "awards", "contracts"):
        if k in r:
            print(f"  {k}: {_keys(r[k])}")
    # ítems: dónde vienen y si traen unidad de medida (clave para D11)
    for cont in ("awards", "contracts"):
        arr = r.get(cont) or []
        if arr and isinstance(arr[0], dict) and arr[0].get("items"):
            it = arr[0]["items"][0]
            print(f"\n-- Primer ítem dentro de {cont}[0].items --")
            print(f"  claves: {_keys(it)}")
            print(f"  classification: {it.get('classification')}")
            print(f"  quantity: {it.get('quantity')}  unit: {it.get('unit')}  <-- ¿trae unidad de medida?")
            break
    print("\n-- Release completo (recorte 2500 chars) --")
    print(json.dumps(r, ensure_ascii=False, indent=2)[:2500])


def inspeccionar_csv(path: Path) -> None:
    with path.open(encoding="utf-8", errors="replace", newline="") as f:
        rd = csv.reader(f)
        header = next(rd, [])
        print(f"CSV con {len(header)} columnas:\n{header}")
        for i, row in enumerate(rd):
            print(f"\nFila {i+1}: {dict(zip(header, row))}")
            if i >= 1:
                break


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archivo", required=True)
    args = ap.parse_args(argv)
    path = Path(args.archivo)
    if not path.exists():
        print(f"No existe: {path}")
        return 1
    if path.suffix.lower() in (".json", ".jsonl"):
        inspeccionar_json(path)
    elif path.suffix.lower() in (".csv", ".txt"):
        inspeccionar_csv(path)
    else:
        print(f"Extensión no reconocida ({path.suffix}). Ábrela y dime si es JSON o CSV.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
