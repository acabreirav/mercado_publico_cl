"""Fase 2 (H1) — Fragmentación: ¿cuántos organismos compran lo mismo por separado?

Mide, para cada producto (UNSPSC real), cuántos organismos distintos lo compran y
en cuántas órdenes separadas. La tesis H1 dice que la demanda de commodities está
atomizada en cientos de compras chicas que podrían consolidarse. Aquí la cuantificamos
con la muestra disponible (no es el universo completo — ver caveats §11 del maestro).

Salida: data/processed/fragmentacion.csv + un resumen por consola. También cruza
tipo de proceso (AG/SE/CM/CC) contra monto de línea (aproximación parcial a H3).

Uso:
    python -m mercadopublico.analisis_fragmentacion
"""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

from .config import REPO_ROOT
from .comparador import _float


def cargar(items_path: Path) -> list[dict[str, str]]:
    with items_path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def linea_total(r: dict[str, str]) -> float | None:
    p = _float(r.get("precio_neto_unitario", ""))
    c = _float(r.get("cantidad", ""))
    return p * c if (p is not None and c is not None) else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", default="data/interim/items.csv")
    parser.add_argument("--salida", default="data/processed/fragmentacion.csv")
    parser.add_argument("--top", type=int, default=15)
    args = parser.parse_args(argv)

    entrada = REPO_ROOT / args.entrada if not Path(args.entrada).is_absolute() else Path(args.entrada)
    if not entrada.exists():
        print(f"No existe {entrada}. Corre antes: python -m mercadopublico.parse_items")
        return 1
    rows = cargar(entrada)

    # --- H1: fragmentación por producto ---
    porprod: dict[str, dict] = defaultdict(lambda: {"orgs": set(), "ocs": set(), "n": 0, "gasto": 0.0, "nombre": ""})
    for r in rows:
        cod = (r.get("codigo_producto") or "").strip()
        if cod in ("", "0"):
            continue
        g = porprod[cod]
        g["orgs"].add(r.get("organismo_nombre", ""))
        g["ocs"].add(r.get("codigo_oc", ""))
        g["n"] += 1
        lt = linea_total(r)
        if lt:
            g["gasto"] += lt
        if not g["nombre"] and r.get("producto"):
            g["nombre"] = r["producto"]

    filas = []
    for cod, g in porprod.items():
        filas.append({
            "codigo_producto": cod, "producto": g["nombre"],
            "n_organismos": len(g["orgs"]), "n_ordenes": len(g["ocs"]),
            "n_lineas": g["n"], "gasto_total": round(g["gasto"]),
        })
    # Fragmentación = muchos organismos comprando el mismo rubro por separado.
    filas.sort(key=lambda d: (d["n_organismos"], d["n_ordenes"]), reverse=True)

    salida = REPO_ROOT / args.salida if not Path(args.salida).is_absolute() else Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["codigo_producto", "producto", "n_organismos", "n_ordenes", "n_lineas", "gasto_total"])
        w.writeheader(); w.writerows(filas)

    total_prod = len(filas)
    multi = [d for d in filas if d["n_organismos"] >= 5]
    print(f"=== H1 Fragmentación (muestra) ===")
    print(f"Productos UNSPSC distintos: {total_prod}")
    print(f"Comprados por 5+ organismos por separado: {len(multi)}")
    print(f"\nTop {args.top} rubros más fragmentados (más organismos comprando por separado):")
    print(f"{'#org':>4} {'#OC':>5} {'#lin':>5} {'gasto muestra':>15}  producto")
    for d in filas[:args.top]:
        print(f"{d['n_organismos']:>4} {d['n_ordenes']:>5} {d['n_lineas']:>5} {d['gasto_total']:>15,}  {d['producto'][:44]}")

    # --- H3 parcial: tipo de proceso vs monto de línea ---
    portipo: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        lt = linea_total(r)
        if lt:
            portipo[(r.get("tipo") or "?").strip()].append(lt)
    print(f"\n=== Tipo de proceso vs monto de línea (aprox. H3) ===")
    print(f"{'tipo':>5} {'#lineas':>8} {'mediana':>14} {'p90':>14}")
    for t, xs in sorted(portipo.items(), key=lambda kv: -len(kv[1])):
        xs.sort()
        med = statistics.median(xs)
        p90 = xs[min(len(xs)-1, int(0.9*len(xs)))]
        print(f"{t:>5} {len(xs):>8} {med:>14,.0f} {p90:>14,.0f}")
    print(f"\nCSV escrito en: {salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
