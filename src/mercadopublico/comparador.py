"""Fase 1 — Comparador de precios: mismo producto, precio distinto entre organismos.

Lee la tabla de ítems (salida de parse_items) y agrupa por `codigo_producto`
(UNSPSC). Para cada producto comprado por 2+ organismos distintos, calcula la
dispersión de precio unitario y produce un ranking de "sobreprecio potencial".

Es el MVP de la visualización #1. Cada fila del ranking es "abrible" hasta las
OC concretas (drill-down) porque conservamos la lista de códigos de OC por grupo.

Reglas (ver docs/mercado-publico-referencia.md §10):
  - Solo se comparan ítems con misma MONEDA (no mezclar CLP/USD/UTM).
  - Se usa `precio_neto_unitario` (PrecioNeto ya es unitario).
  - Se ignoran precios <= 0 o vacíos (dudosos).
  - CAVEAT: mismo `codigo_producto` UNSPSC no garantiza misma especificación ni
    unidad de medida → esto es una SEÑAL para investigar, no una acusación.

Uso:
    python -m mercadopublico.comparador
    python -m mercadopublico.comparador --entrada data/interim/items.csv --top 30
"""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from .config import REPO_ROOT


def _leer_items(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _float(v: str) -> float | None:
    try:
        x = float(v)
        return x if x > 0 else None
    except (TypeError, ValueError):
        return None


def construir_comparador(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Agrupa por (codigo_producto, moneda) y calcula dispersión de precio."""
    grupos: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        cod = (r.get("codigo_producto") or "").strip()
        moneda = (r.get("moneda") or "").strip()
        precio = _float(r.get("precio_neto_unitario", ""))
        if not cod or precio is None:
            continue
        grupos[(cod, moneda)].append(r)

    resultados: list[dict[str, Any]] = []
    for (cod, moneda), items in grupos.items():
        precios = [_float(r["precio_neto_unitario"]) for r in items]
        precios = [p for p in precios if p is not None]
        organismos = {r.get("organismo_nombre", "") for r in items}
        if len(organismos) < 2 or len(precios) < 2:
            continue  # sin comparación entre organismos, no aporta

        pmin, pmax = min(precios), max(precios)
        ratio = round(pmax / pmin, 2) if pmin > 0 else None
        resultados.append(
            {
                "codigo_producto": cod,
                "producto": next((r.get("producto") for r in items if r.get("producto")), ""),
                "moneda": moneda,
                "n_items": len(items),
                "n_organismos": len(organismos),
                "precio_min": round(pmin, 2),
                "precio_max": round(pmax, 2),
                "precio_mediana": round(statistics.median(precios), 2),
                "ratio_max_min": ratio,
                "codigos_oc": ";".join(sorted({r.get("codigo_oc", "") for r in items})),
            }
        )

    # Ranking: primero el mayor sobreprecio potencial (ratio), luego más organismos.
    resultados.sort(key=lambda d: (d["ratio_max_min"] or 0, d["n_organismos"]), reverse=True)
    return resultados


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", default="data/interim/items.csv")
    parser.add_argument("--salida", default="data/processed/comparador_precios.csv")
    parser.add_argument("--top", type=int, default=20, help="Cuántas filas imprimir.")
    args = parser.parse_args(argv)

    entrada = REPO_ROOT / args.entrada if not Path(args.entrada).is_absolute() else Path(args.entrada)
    if not entrada.exists():
        print(f"No existe {entrada}. Corre antes: python -m mercadopublico.parse_items")
        return 1

    rows = _leer_items(entrada)
    print(f"Ítems leídos: {len(rows)}")
    ranking = construir_comparador(rows)
    print(f"Productos comparables (2+ organismos, 2+ precios): {len(ranking)}")

    salida = REPO_ROOT / args.salida if not Path(args.salida).is_absolute() else Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "codigo_producto", "producto", "moneda", "n_items", "n_organismos",
        "precio_min", "precio_max", "precio_mediana", "ratio_max_min", "codigos_oc",
    ]
    with salida.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(ranking)
    print(f"Ranking escrito en: {salida}")

    if ranking:
        print(f"\nTop {min(args.top, len(ranking))} por sobreprecio potencial (ratio max/min):")
        print(f"{'ratio':>6}  {'#org':>4}  {'min':>12}  {'max':>12}  producto")
        for d in ranking[: args.top]:
            print(
                f"{d['ratio_max_min']:>6}  {d['n_organismos']:>4}  "
                f"{d['precio_min']:>12,.0f}  {d['precio_max']:>12,.0f}  "
                f"{(d['producto'] or d['codigo_producto'])[:60]}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
