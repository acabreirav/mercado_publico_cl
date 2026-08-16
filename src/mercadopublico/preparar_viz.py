"""Fase 1 — Prepara el dataset del visual del comparador (JSON para la web).

Toma la tabla de ítems y produce un JSON compacto con los productos "creíbles"
(dispersión razonable, varios organismos, sin bandera de revisar) y, para cada
uno, el detalle de sus ítems para el DRILL-DOWN (organismo, comuna, precio, OC).

Uso:
    python -m mercadopublico.preparar_viz
    python -m mercadopublico.preparar_viz --min-org 4 --ratio-max 6 --top 40

Criterio de "creíble" (ver docs/mercado-publico-referencia.md §10 y discrepancias):
  - `codigo_producto` UNSPSC real (no 0/vacío).
  - Comprado por >= --min-org organismos distintos.
  - Dispersión robusta p75/p25 entre 1.3 y --ratio-max (evita mezclas de unidad/lote).
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import REPO_ROOT
from .comparador import _percentil, _float
from .scoring import confiabilidad, interes


def preparar(
    items_path: Path, *, min_org: int, ratio_max: float, top: int
) -> dict[str, Any]:
    with items_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    grupos: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        cod = (r.get("codigo_producto") or "").strip()
        if cod in ("", "0"):
            continue
        if _float(r.get("precio_neto_unitario", "")) is None:
            continue
        grupos[(cod, (r.get("moneda") or "").strip())].append(r)

    productos: list[dict[str, Any]] = []
    for (cod, moneda), its in grupos.items():
        precios = [p for p in (_float(r["precio_neto_unitario"]) for r in its) if p is not None]
        organismos = {r.get("organismo_nombre", "") for r in its}
        if len(organismos) < min_org or len(precios) < 2:
            continue
        p25, p50, p75 = _percentil(precios, 0.25), statistics.median(precios), _percentil(precios, 0.75)
        ratio = round(p75 / p25, 2) if p25 > 0 else None
        if ratio is None or not (1.3 <= ratio <= ratio_max):
            continue
        pmin, pmax = min(precios), max(precios)
        n_org = len(organismos)
        tier, conf = confiabilidad(n_org, len(its))
        score = interes(ratio, n_org, len(its))

        # Ítems para drill-down (ordenados por precio unitario asc).
        detalle = sorted(
            (
                {
                    "organismo": r.get("organismo_nombre", ""),
                    "comuna": r.get("comuna", ""),
                    "region": r.get("region", "").strip(),
                    "precio": _float(r["precio_neto_unitario"]),
                    "cantidad": _float(r.get("cantidad", "")) or None,
                    "fecha": (r.get("fecha_creacion") or "")[:10],
                    "tipo": r.get("tipo", ""),
                    "codigo_oc": r.get("codigo_oc", ""),
                    "proveedor": r.get("proveedor_nombre", ""),
                    "especificacion": (r.get("especificacion_comprador") or "")[:200],
                }
                for r in its
            ),
            key=lambda d: d["precio"] or 0,
        )
        productos.append(
            {
                "codigo_producto": cod,
                "producto": next((r.get("producto") for r in its if r.get("producto")), cod),
                "categoria": next((r.get("categoria") for r in its if r.get("categoria")), ""),
                "moneda": moneda,
                "n_items": len(its),
                "n_organismos": n_org,
                "precio_min": round(pmin, 2),
                "precio_p25": round(p25, 2),
                "precio_mediana": round(p50, 2),
                "precio_p75": round(p75, 2),
                "precio_max": round(pmax, 2),
                "ratio_p75_p25": ratio,
                "ratio_max_min": round(pmax / pmin, 2) if pmin > 0 else None,
                "confiabilidad": tier,
                "confiabilidad_score": conf,
                "interes": score,
                "items": detalle,
            }
        )

    # Orden por defecto: mayor INTERÉS (dispersión ponderada por amplitud/confiabilidad).
    productos.sort(key=lambda d: d["interes"], reverse=True)
    productos = productos[:top]

    return {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_items_total": len(rows),
        "criterio": {"min_org": min_org, "ratio_max": ratio_max, "top": top},
        "productos": productos,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", default="data/interim/items.csv")
    parser.add_argument("--salida", default="data/processed/viz_comparador.json")
    parser.add_argument("--min-org", type=int, default=4)
    parser.add_argument("--ratio-max", type=float, default=6.0)
    parser.add_argument("--top", type=int, default=40)
    args = parser.parse_args(argv)

    entrada = REPO_ROOT / args.entrada if not Path(args.entrada).is_absolute() else Path(args.entrada)
    if not entrada.exists():
        print(f"No existe {entrada}. Corre antes: python -m mercadopublico.parse_items")
        return 1

    data = preparar(entrada, min_org=args.min_org, ratio_max=args.ratio_max, top=args.top)
    salida = REPO_ROOT / args.salida if not Path(args.salida).is_absolute() else Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Productos en el visual: {len(data['productos'])}")
    print(f"JSON escrito en: {salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
