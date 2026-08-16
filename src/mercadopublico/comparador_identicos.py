"""Fase 1/2 — Comparador de PRODUCTOS IDÉNTICOS (por ID de catálogo).

A diferencia del comparador general (que agrupa por UNSPSC, demasiado grueso),
aquí agrupamos por el **ID de catálogo de Convenio Marco** que viene en la
especificación (ej. "(1573012) ARROZ TUCAPEL GRADO 1 BOLSA 1K"). Mismo ID =
producto y presentación **idénticos** → la comparación de precio es creíble y el
ahorro potencial es defendible (ver docs/metodologia-y-limites.md §3.1).

Se filtran los IDs con dispersión implausible (contratos marco heterogéneos como
combustible o alimentación, cuyo "precio" no es unitario) con un tope de ratio.

Salidas:
  - data/processed/identicos.csv  (ranking por ahorro conservador)
  - data/processed/viz_identicos.json  (para un visual curado)
  - resumen por consola con el ahorro potencial creíble

Uso:
    python -m mercadopublico.comparador_identicos
    python -m mercadopublico.comparador_identicos --ratio-cap 3 --min-org 3
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .config import REPO_ROOT
from .comparador import _float, _percentil
from .parse_items import extraer_catalogo_id


def cargar(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _cat_id(r: dict[str, str]) -> str:
    return (r.get("catalogo_id") or "").strip() or extraer_catalogo_id(r.get("especificacion_comprador"))


def construir(rows: list[dict[str, str]], *, min_org: int, min_items: int, ratio_cap: float):
    grupos: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        cid = _cat_id(r)
        if cid and _float(r.get("precio_neto_unitario", "")) is not None:
            grupos[cid].append(r)

    out = []
    tot_gasto = tot_cons = tot_aspi = 0.0
    for cid, its in grupos.items():
        precios = [p for p in (_float(r["precio_neto_unitario"]) for r in its) if p is not None]
        orgs = {r.get("organismo_nombre", "") for r in its}
        if len(orgs) < min_org or len(its) < min_items:
            continue
        pmin, pmax = min(precios), max(precios)
        if pmin <= 0 or pmax / pmin > ratio_cap:  # heterogéneo (contrato marco variable) → fuera
            continue
        med = statistics.median(precios)
        q25 = _percentil(precios, 0.25)
        # ahorro potencial: alinear lo que está sobre el benchmark, ponderado por cantidad
        gasto = cons = aspi = 0.0
        detalle = []
        for r in its:
            p = _float(r["precio_neto_unitario"]); c = _float(r.get("cantidad", "")) or 0
            gasto += p * c
            cons += max(0.0, p - med) * c
            aspi += max(0.0, p - q25) * c
            detalle.append({
                "organismo": r.get("organismo_nombre", ""), "comuna": r.get("comuna", ""),
                "region": (r.get("region") or "").strip(), "precio": p, "cantidad": c or None,
                "fecha": (r.get("fecha_creacion") or "")[:10], "codigo_oc": r.get("codigo_oc", ""),
                "proveedor": r.get("proveedor_nombre", ""),
            })
        tot_gasto += gasto; tot_cons += cons; tot_aspi += aspi
        detalle.sort(key=lambda d: d["precio"])
        out.append({
            "catalogo_id": cid,
            "descripcion": next((r.get("especificacion_comprador") for r in its if r.get("especificacion_comprador")), cid).strip()[:120],
            "n_organismos": len(orgs), "n_items": len(its),
            "precio_min": round(pmin, 2), "precio_mediana": round(med, 2), "precio_max": round(pmax, 2),
            "ratio_max_min": round(pmax / pmin, 2),
            "ahorro_conservador": round(cons), "gasto": round(gasto),
            "items": detalle,
        })
    out.sort(key=lambda d: d["ahorro_conservador"], reverse=True)
    return out, tot_gasto, tot_cons, tot_aspi


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entrada", default="data/interim/items.csv")
    ap.add_argument("--min-org", type=int, default=3)
    ap.add_argument("--min-items", type=int, default=4)
    ap.add_argument("--ratio-cap", type=float, default=3.0,
                    help="Excluye grupos con máx/mín mayor a esto (heterogéneos).")
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args(argv)

    entrada = REPO_ROOT / args.entrada if not Path(args.entrada).is_absolute() else Path(args.entrada)
    if not entrada.exists():
        print(f"No existe {entrada}. Corre antes: python -m mercadopublico.parse_items")
        return 1

    prods, gasto, cons, aspi = construir(
        cargar(entrada), min_org=args.min_org, min_items=args.min_items, ratio_cap=args.ratio_cap)

    def M(x): return f"${x/1e6:,.1f} M"
    print("=== Productos IDÉNTICOS (por ID de catálogo) — ahorro potencial creíble ===")
    print(f"Grupos idénticos comparables: {len(prods)} (>= {args.min_org} organismos, dispersión <= {args.ratio_cap}×)")
    print(f"Gasto comparado:            {M(gasto)}")
    print(f"Ahorro CONSERVADOR (→mediana): {M(cons)}  ({100*cons/gasto:.1f}% del gasto comparado)" if gasto else "")
    print(f"Ahorro ASPIRACIONAL (→p25):    {M(aspi)}  ({100*aspi/gasto:.1f}%)" if gasto else "")
    print(f"\nTop {args.top} por ahorro conservador:")
    for d in prods[:args.top]:
        print(f"  {M(d['ahorro_conservador']):>9}  {d['n_organismos']:>2}org  {d['ratio_max_min']:>4}×  "
              f"${d['precio_min']:,.0f}–${d['precio_max']:,.0f}  {d['descripcion'][:46]}")

    csv_out = REPO_ROOT / "data/processed/identicos.csv"
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    with csv_out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["catalogo_id", "descripcion", "n_organismos", "n_items", "precio_min",
                    "precio_mediana", "precio_max", "ratio_max_min", "ahorro_conservador", "gasto"])
        for d in prods:
            w.writerow([d["catalogo_id"], d["descripcion"], d["n_organismos"], d["n_items"],
                        d["precio_min"], d["precio_mediana"], d["precio_max"], d["ratio_max_min"],
                        d["ahorro_conservador"], d["gasto"]])
    json_out = REPO_ROOT / "data/processed/viz_identicos.json"
    json_out.write_text(json.dumps({
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "gasto_comparado": round(gasto), "ahorro_conservador": round(cons), "ahorro_aspiracional": round(aspi),
        "productos": prods,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nCSV: {csv_out}\nJSON: {json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
