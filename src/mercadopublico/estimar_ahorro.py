"""Fase 2 — Estimador de ahorro potencial (con control por volumen).

Idea: ¿cuánto podría ahorrar el Estado si las compras de un mismo producto se
alinearan a un precio de referencia razonable, comparando SOLO compras de
cantidades parecidas (para no confundir descuento por volumen con sobreprecio)?

Método (ver docs/metodologia-y-limites.md §3):
  1. Agrupar por (CodigoProducto UNSPSC, banda de cantidad por orden de magnitud).
  2. En cada grupo con >=3 compras y >=2 organismos, fijar referencia:
       - conservadora = mediana de la banda (piso creíble)
       - aspiracional = percentil 25 de la banda
  3. Ahorro de una compra = max(0, precio - referencia) * cantidad.
  4. Reportar como RANGO [conservador, aspiracional], solo productos de
     confiabilidad alta/media. Es ahorro POTENCIAL ESTIMADO, no garantizado.

Uso:
    python -m mercadopublico.estimar_ahorro
    python -m mercadopublico.estimar_ahorro --por-region
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

from .config import REPO_ROOT
from .comparador import _float, _percentil
from .scoring import confiabilidad

MIN_ITEMS_BANDA = 3
MIN_ORG_BANDA = 2


def banda_cantidad(qty: float) -> int:
    """Orden de magnitud de la cantidad: 0 (1-9), 1 (10-99), 2 (100-999), ..."""
    return int(math.floor(math.log10(qty))) if qty >= 1 else 0


def banda_label(b: int) -> str:
    lo = 10**b
    return f"{lo:,}-{10*lo-1:,}"


def cargar(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def es_bien(codigo_producto: str) -> bool:
    """True si el UNSPSC es un BIEN (segmento < 70). Los servicios (70-94) no
    tienen 'unidad' ni 'cantidad' comparables → se excluyen del estimador de ahorro."""
    try:
        return int(codigo_producto) < 70_000_000
    except (TypeError, ValueError):
        return False


def estimar(rows: list[dict[str, str]], solo_bienes: bool = False):
    # 1) confiabilidad por producto (nº organismos y compras en todo el producto)
    prod_org: dict[str, set] = defaultdict(set)
    prod_n: dict[str, int] = defaultdict(int)
    prod_nombre: dict[str, str] = {}
    for r in rows:
        cod = (r.get("codigo_producto") or "").strip()
        if cod in ("", "0"):
            continue
        if solo_bienes and not es_bien(cod):
            continue
        prod_org[cod].add(r.get("organismo_nombre", ""))
        prod_n[cod] += 1
        if cod not in prod_nombre and r.get("producto"):
            prod_nombre[cod] = r["producto"]
    confiables = {c for c in prod_org
                  if confiabilidad(len(prod_org[c]), prod_n[c])[0] != "baja"}

    # 2) agrupar por (producto, banda) y calcular referencias
    grupos: dict[tuple[str, int], list[tuple[float, float, dict]]] = defaultdict(list)
    for r in rows:
        cod = (r.get("codigo_producto") or "").strip()
        if cod not in confiables:
            continue
        precio = _float(r.get("precio_neto_unitario", ""))
        cant = _float(r.get("cantidad", ""))
        if precio is None or cant is None or cant <= 0:
            continue
        grupos[(cod, banda_cantidad(cant))].append((precio, cant, r))

    ahorro_cons = 0.0
    ahorro_aspi = 0.0
    gasto_base = 0.0
    por_prod: dict[str, float] = defaultdict(float)
    por_region: dict[str, float] = defaultdict(float)

    for (cod, b), items in grupos.items():
        orgs = {r.get("organismo_nombre", "") for _, _, r in items}
        if len(items) < MIN_ITEMS_BANDA or len(orgs) < MIN_ORG_BANDA:
            continue
        precios = [p for p, _, _ in items]
        ref_med = statistics.median(precios)
        ref_p25 = _percentil(precios, 0.25)
        for precio, cant, r in items:
            gasto_base += precio * cant
            sc = max(0.0, precio - ref_med) * cant
            sa = max(0.0, precio - ref_p25) * cant
            ahorro_cons += sc
            ahorro_aspi += sa
            por_prod[cod] += sc
            por_region[(r.get("region") or "—").strip() or "—"] += sc

    return {
        "gasto_base": gasto_base,
        "ahorro_cons": ahorro_cons,
        "ahorro_aspi": ahorro_aspi,
        "por_prod": por_prod,
        "por_region": por_region,
        "prod_nombre": prod_nombre,
        "n_confiables": len(confiables),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", default="data/interim/items.csv")
    parser.add_argument("--por-region", action="store_true")
    parser.add_argument("--solo-bienes", action="store_true",
                        help="Excluir servicios (UNSPSC>=70): recomendado, son incomparables por unidad.")
    parser.add_argument("--top", type=int, default=12)
    args = parser.parse_args(argv)

    entrada = REPO_ROOT / args.entrada if not Path(args.entrada).is_absolute() else Path(args.entrada)
    if not entrada.exists():
        print(f"No existe {entrada}. Corre antes: python -m mercadopublico.parse_items")
        return 1
    res = estimar(cargar(entrada), solo_bienes=args.solo_bienes)
    if args.solo_bienes:
        print("(Filtro: solo BIENES, servicios excluidos)\n")

    def M(x): return f"${x/1e6:,.1f} M"
    pct_c = 100 * res["ahorro_cons"] / res["gasto_base"] if res["gasto_base"] else 0
    pct_a = 100 * res["ahorro_aspi"] / res["gasto_base"] if res["gasto_base"] else 0
    print("=== Ahorro potencial estimado (control por volumen) ===")
    print("⚠️  Potencial y estimado, NO garantizado. Solo compras de cantidades comparables,")
    print("    productos de confiabilidad alta/media. Ver docs/metodologia-y-limites.md.\n")
    print(f"Gasto comparado (base):     {M(res['gasto_base'])}")
    print(f"Ahorro CONSERVADOR (→ mediana de banda): {M(res['ahorro_cons'])}  ({pct_c:.1f}% del gasto comparado)")
    print(f"Ahorro ASPIRACIONAL (→ p25 de banda):    {M(res['ahorro_aspi'])}  ({pct_a:.1f}% del gasto comparado)")

    print(f"\nTop {args.top} productos por ahorro conservador:")
    top = sorted(res["por_prod"].items(), key=lambda kv: kv[1], reverse=True)[:args.top]
    for cod, s in top:
        print(f"  {M(s):>12}  {res['prod_nombre'].get(cod, cod)[:48]}")

    if args.por_region:
        print("\nAhorro conservador por región:")
        for reg, s in sorted(res["por_region"].items(), key=lambda kv: kv[1], reverse=True)[:16]:
            print(f"  {M(s):>12}  {reg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
