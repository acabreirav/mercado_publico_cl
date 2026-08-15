"""Fase 1 — Comparador de precios: mismo producto, precio distinto entre organismos.

Lee la tabla de ítems (salida de parse_items) y agrupa por `codigo_producto`
(UNSPSC). Para cada producto comprado por 2+ organismos distintos, calcula la
dispersión de precio unitario y produce un ranking de "sobreprecio potencial".

Es el MVP de la visualización #1. Cada fila del ranking es "abrible" hasta las
OC concretas (drill-down) porque conservamos la lista de códigos de OC por grupo.

Reglas y CAVEATS (ver docs/mercado-publico-referencia.md §10 y docs/discrepancias-fuentes.md):
  - Solo se comparan ítems con misma MONEDA (no mezclar CLP/USD/UTM).
  - Se EXCLUYE `codigo_producto` vacío o "0" (ítems sin código UNSPSC: no son un
    producto real, agruparlos da falsos positivos).
  - Se usa `precio_neto_unitario` (PrecioNeto ya es unitario). Se ignoran <= 0.
  - La API de OC NO llena `unidad` (viene vacía) → NO podemos normalizar unidad de
    medida. Por eso un mismo `codigo_producto` puede mezclar "unidad" vs "caja" vs
    "kg" → los ratios extremos suelen ser diferencias de envase/lote, NO sobreprecio.
    Se marca `revisar=1` cuando el ratio es implausiblemente alto.
  - La dispersión principal es ROBUSTA (p75/p25), menos sensible a un outlier que
    max/min. Ambas se reportan.

Uso:
    python -m mercadopublico.comparador
    python -m mercadopublico.comparador --tipo CM          # solo Convenio Marco (más limpio)
    python -m mercadopublico.comparador --top 30
"""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from .config import REPO_ROOT

# Umbral sobre el que un ratio max/min se considera "probable mezcla de unidad/lote".
RATIO_SOSPECHOSO = 20.0


def _leer_items(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _float(v: str) -> float | None:
    try:
        x = float(v)
        return x if x > 0 else None
    except (TypeError, ValueError):
        return None


def _percentil(datos: list[float], q: float) -> float:
    """Percentil por interpolación lineal (q en [0,1]). `datos` no vacío."""
    xs = sorted(datos)
    if len(xs) == 1:
        return xs[0]
    pos = q * (len(xs) - 1)
    lo = int(pos)
    frac = pos - lo
    if lo + 1 < len(xs):
        return xs[lo] + frac * (xs[lo + 1] - xs[lo])
    return xs[lo]


def construir_comparador(
    rows: list[dict[str, str]], tipos: set[str] | None = None
) -> list[dict[str, Any]]:
    """Agrupa por (codigo_producto, moneda) y calcula dispersión de precio."""
    grupos: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        if tipos and (r.get("tipo") or "").strip() not in tipos:
            continue
        cod = (r.get("codigo_producto") or "").strip()
        if cod in ("", "0"):  # sin código UNSPSC real → no comparar
            continue
        moneda = (r.get("moneda") or "").strip()
        if _float(r.get("precio_neto_unitario", "")) is None:
            continue
        grupos[(cod, moneda)].append(r)

    resultados: list[dict[str, Any]] = []
    for (cod, moneda), items in grupos.items():
        precios = [p for p in (_float(r["precio_neto_unitario"]) for r in items) if p is not None]
        organismos = {r.get("organismo_nombre", "") for r in items}
        if len(organismos) < 2 or len(precios) < 2:
            continue

        pmin, pmax = min(precios), max(precios)
        p25, p50, p75 = _percentil(precios, 0.25), statistics.median(precios), _percentil(precios, 0.75)
        ratio_ext = round(pmax / pmin, 2) if pmin > 0 else None
        ratio_rob = round(p75 / p25, 2) if p25 > 0 else None
        resultados.append(
            {
                "codigo_producto": cod,
                "producto": next((r.get("producto") for r in items if r.get("producto")), ""),
                "moneda": moneda,
                "n_items": len(items),
                "n_organismos": len(organismos),
                "precio_min": round(pmin, 2),
                "precio_p25": round(p25, 2),
                "precio_mediana": round(p50, 2),
                "precio_p75": round(p75, 2),
                "precio_max": round(pmax, 2),
                "ratio_p75_p25": ratio_rob,
                "ratio_max_min": ratio_ext,
                "revisar": 1 if (ratio_ext or 0) >= RATIO_SOSPECHOSO else 0,
                "codigos_oc": ";".join(sorted({r.get("codigo_oc", "") for r in items})),
            }
        )

    # Ranking por dispersión ROBUSTA (p75/p25); desempata por nº de organismos.
    resultados.sort(key=lambda d: (d["ratio_p75_p25"] or 0, d["n_organismos"]), reverse=True)
    return resultados


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", default="data/interim/items.csv")
    parser.add_argument("--salida", default="data/processed/comparador_precios.csv")
    parser.add_argument("--tipo", default=None, help="Filtrar por tipo(s) de OC, coma-separado (ej. CM,CC).")
    parser.add_argument("--top", type=int, default=20, help="Cuántas filas imprimir.")
    args = parser.parse_args(argv)

    entrada = REPO_ROOT / args.entrada if not Path(args.entrada).is_absolute() else Path(args.entrada)
    if not entrada.exists():
        print(f"No existe {entrada}. Corre antes: python -m mercadopublico.parse_items")
        return 1

    tipos = {t.strip().upper() for t in args.tipo.split(",")} if args.tipo else None
    rows = _leer_items(entrada)
    print(f"Ítems leídos: {len(rows)}" + (f" | filtro tipo={sorted(tipos)}" if tipos else ""))
    ranking = construir_comparador(rows, tipos)
    n_revisar = sum(d["revisar"] for d in ranking)
    print(
        f"Productos comparables (código UNSPSC real, 2+ organismos): {len(ranking)} "
        f"({n_revisar} marcados 'revisar' por ratio sospechoso de mezcla de unidad/lote)"
    )

    salida = REPO_ROOT / args.salida if not Path(args.salida).is_absolute() else Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "codigo_producto", "producto", "moneda", "n_items", "n_organismos",
        "precio_min", "precio_p25", "precio_mediana", "precio_p75", "precio_max",
        "ratio_p75_p25", "ratio_max_min", "revisar", "codigos_oc",
    ]
    with salida.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(ranking)
    print(f"Ranking escrito en: {salida}")

    if ranking:
        print(f"\nTop {min(args.top, len(ranking))} por dispersión robusta (p75/p25):")
        print(f"{'p75/p25':>8} {'rev':>3} {'#org':>4}  {'p25':>10} {'mediana':>10} {'p75':>10}  producto")
        for d in ranking[: args.top]:
            flag = "⚠" if d["revisar"] else " "
            print(
                f"{d['ratio_p75_p25']:>8} {flag:>3} {d['n_organismos']:>4}  "
                f"{d['precio_p25']:>10,.0f} {d['precio_mediana']:>10,.0f} {d['precio_p75']:>10,.0f}  "
                f"{(d['producto'] or d['codigo_producto'])[:50]}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
