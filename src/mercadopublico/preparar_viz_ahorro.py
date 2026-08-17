"""Prepara el dataset del visual de AHORRO POTENCIAL (productos idénticos, Convenio Marco).

Usa el comparador de idénticos (agrupa por ID de catálogo = mismo producto y
presentación) y arma un JSON con:
  - titular: gasto comparado y ahorro potencial como RANGO, bajo 3 niveles de
    control (producto / +región / +región+mes) para ser honesto.
  - top productos por ahorro, con drill-down hasta la orden de compra.

Uso:
    python -m mercadopublico.preparar_viz_ahorro --entrada data/interim/items_cm_ocds.csv
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .config import REPO_ROOT
from .comparador_identicos import cargar, construir


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entrada", default="data/interim/items_cm_ocds.csv")
    ap.add_argument("--salida", default="data/processed/viz_ahorro.json")
    ap.add_argument("--top", type=int, default=60)
    ap.add_argument("--max-items", type=int, default=40, help="Máx. filas de drill-down por producto.")
    args = ap.parse_args(argv)

    entrada = REPO_ROOT / args.entrada if not Path(args.entrada).is_absolute() else Path(args.entrada)
    if not entrada.exists():
        print(f"No existe {entrada}. Corre antes: python -m mercadopublico.parse_ocds ...")
        return 1
    rows = cargar(entrada)

    # Titular: ahorro conservador bajo niveles crecientes de control.
    niveles = []
    for etq, ctrl in [("producto", ()), ("producto+region", ("region",)), ("producto+region+mes", ("region", "mes"))]:
        ps, g, c, a = construir(rows, min_org=3, min_items=4, ratio_cap=3.0, control=ctrl)
        niveles.append({"control": etq, "grupos": len(ps), "gasto": round(g),
                        "ahorro_conservador": round(c), "ahorro_aspiracional": round(a),
                        "pct_cons": round(100 * c / g, 1) if g else 0,
                        "pct_aspi": round(100 * a / g, 1) if g else 0})

    # Productos para la lista (nivel producto), top por ahorro, con drill-down acotado.
    prods, gasto, cons, aspi = construir(rows, min_org=3, min_items=4, ratio_cap=3.0)
    prods = prods[:args.top]
    for p in prods:
        p["items"] = p["items"][:args.max_items]

    organismos = {i["organismo"] for p in prods for i in p["items"]}
    meses = sorted({(r.get("fecha_creacion") or "")[:7] for r in rows if r.get("fecha_creacion")})

    data = {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fuente": "OCDS Convenio Marco",
        "n_items_muestra": len(rows),
        "n_organismos_muestra": len({r.get("organismo_nombre", "") for r in rows}),
        "meses": [m for m in meses if m],
        "niveles": niveles,
        "productos": prods,
    }
    salida = REPO_ROOT / args.salida if not Path(args.salida).is_absolute() else Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Productos en el visual: {len(prods)} | archivo: {salida} ({salida.stat().st_size//1024} KB)")
    for nv in niveles:
        print(f"  {nv['control']:20} grupos={nv['grupos']:>4} ahorro={nv['pct_cons']}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
