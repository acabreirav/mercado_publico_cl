"""Fase 2 — Fragmentación en el tiempo: ¿se controla, amplifica o mantiene?

Mide la fragmentación de la compra de productos idénticos (mismo ID de catálogo)
por PERIODO, para ver la evolución 2024 → hoy y estimar si la Compra Coordinada
está teniendo efecto (menos compradores separados / menos dispersión de precio).

Métricas por periodo (año-mes o año):
  - commodities: nº de productos de catálogo distintos comprados
  - fragmentados: productos comprados por >= N organismos por separado
  - ordenes: nº de órdenes de compra distintas
  - gasto: suma de precio*cantidad
  - disp_mediana: mediana de la dispersión de precio (p75/p25) entre fragmentados
    → proxy de "qué tan descoordinada" está la compra (baja = más alineada)
  - org_x_commodity: promedio de organismos distintos por producto (intensidad de
    fragmentación; sube = más gente comprando lo mismo por separado)

Uso:
    python -m mercadopublico.analisis_temporal --entrada data/interim/items_cm_ocds.csv
    python -m mercadopublico.analisis_temporal --anual        # agrupa por año
    python -m mercadopublico.analisis_temporal --top 15       # commodities más fragmentados
"""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

from .config import REPO_ROOT
from .comparador import _float, _percentil
from .comparador_identicos import _cat_id

MIN_ORG = 3


def cargar(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _periodo(r: dict[str, str], anual: bool) -> str:
    f = (r.get("fecha_creacion") or "")
    return f[:4] if anual else f[:7]


def metricas_periodo(rows: list[dict[str, str]]) -> dict:
    porprod: dict[str, dict] = defaultdict(lambda: {"orgs": set(), "ocs": set(), "precios": [], "gasto": 0.0})
    for r in rows:
        cid = _cat_id(r)
        p = _float(r.get("precio_neto_unitario", ""))
        if not cid or p is None:
            continue
        g = porprod[cid]
        g["orgs"].add(r.get("organismo_nombre", ""))
        g["ocs"].add(r.get("codigo_oc", ""))
        g["precios"].append(p)
        c = _float(r.get("cantidad", "")) or 0
        g["gasto"] += p * c

    frag = {c: g for c, g in porprod.items() if len(g["orgs"]) >= MIN_ORG}
    disps = []
    for g in frag.values():
        ps = g["precios"]
        q25 = _percentil(ps, 0.25)
        if len(ps) >= 2 and q25 > 0:
            disps.append(_percentil(ps, 0.75) / q25)
    return {
        "commodities": len(porprod),
        "fragmentados": len(frag),
        "ordenes": len({oc for g in porprod.values() for oc in g["ocs"]}),
        "gasto": sum(g["gasto"] for g in porprod.values()),
        "disp_mediana": statistics.median(disps) if disps else None,
        "org_x_commodity": (statistics.mean([len(g["orgs"]) for g in frag.values()]) if frag else None),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entrada", default="data/interim/items_cm_ocds.csv")
    ap.add_argument("--anual", action="store_true", help="Agrupar por año en vez de año-mes.")
    ap.add_argument("--top", type=int, default=12, help="Commodities más fragmentados a listar.")
    args = ap.parse_args(argv)

    entrada = REPO_ROOT / args.entrada if not Path(args.entrada).is_absolute() else Path(args.entrada)
    if not entrada.exists():
        print(f"No existe {entrada}.")
        return 1
    rows = cargar(entrada)

    # --- Tendencia por periodo ---
    porper: dict[str, list] = defaultdict(list)
    for r in rows:
        porper[_periodo(r, args.anual)].append(r)

    print(f"=== Fragmentación por {'año' if args.anual else 'mes'} (producto = ID de catálogo, >= {MIN_ORG} organismos) ===")
    print(f"{'periodo':>8} {'commodities':>11} {'fragmentad.':>11} {'ordenes':>8} {'gasto MM$':>10} {'disp.med':>9} {'org/prod':>9}")
    for per in sorted(porper):
        if not per.strip():
            continue
        m = metricas_periodo(porper[per])
        dm = f"{m['disp_mediana']:.2f}×" if m['disp_mediana'] else "—"
        ox = f"{m['org_x_commodity']:.1f}" if m['org_x_commodity'] else "—"
        print(f"{per:>8} {m['commodities']:>11} {m['fragmentados']:>11} {m['ordenes']:>8} "
              f"{m['gasto']/1e6:>10,.0f} {dm:>9} {ox:>9}")

    # --- Commodities más fragmentados (todo el periodo) ---
    porprod: dict[str, dict] = defaultdict(lambda: {"orgs": set(), "ocs": set(), "gasto": 0.0, "desc": ""})
    for r in rows:
        cid = _cat_id(r)
        p = _float(r.get("precio_neto_unitario", ""))
        if not cid or p is None:
            continue
        g = porprod[cid]
        g["orgs"].add(r.get("organismo_nombre", ""))
        g["ocs"].add(r.get("codigo_oc", ""))
        g["gasto"] += p * (_float(r.get("cantidad", "")) or 0)
        if not g["desc"]:
            g["desc"] = (r.get("especificacion_comprador") or r.get("producto") or cid)
    top = sorted(porprod.items(), key=lambda kv: len(kv[1]["orgs"]), reverse=True)[:args.top]
    print(f"\n=== Top {args.top} commodities más fragmentados (más organismos comprando por separado) ===")
    print(f"{'#org':>4} {'#OC':>5} {'gasto MM$':>10}  producto")
    import re
    for cid, g in top:
        desc = re.sub(r"\(\d{5,8}\)", "", g["desc"]).strip()[:48]
        print(f"{len(g['orgs']):>4} {len(g['ocs']):>5} {g['gasto']/1e6:>10,.0f}  {desc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
