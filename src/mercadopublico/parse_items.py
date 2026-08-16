"""Fase 1 — Parser: JSON crudo de detalle de OC → tabla plana de ítems (CSV).

Lee los detalles crudos de órdenes de compra (los que traen `Items`) y los
aplana a una fila por ítem/línea, con las columnas necesarias para el comparador
de precios: producto (UNSPSC), organismo, comuna, proveedor y precio unitario.

Solo procesa registros que tengan ítems (los listados "por día" livianos, que
solo traen Codigo/Nombre/Estado, se ignoran).

Uso:
    python -m mercadopublico.parse_items                      # lee data/raw/**/*.json
    python -m mercadopublico.parse_items --entrada data/raw/detalles
    python -m mercadopublico.parse_items --salida data/interim/items.csv

Nota sobre precios (ver docs/discrepancias-fuentes.md D6/D7):
    `PrecioNeto` YA es el precio unitario. El total de línea se DERIVA como
    PrecioNeto * Cantidad; el campo `Total` del ítem puede venir en 0.0 (sucio),
    por eso se guarda aparte como `total_item_reportado` sin usarlo para calcular.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any, Iterator

from .config import REPO_ROOT

# ID de catálogo (Convenio Marco) que suele venir entre paréntesis en la
# especificación, p.ej. "(1573012) ARROZ TUCAPEL...". Mismo ID = producto y
# presentación idénticos → clave de normalización confiable (ver §5 del maestro).
_RX_CATALOGO = re.compile(r"\((\d{5,8})\)")


def extraer_catalogo_id(especificacion: str | None) -> str:
    m = _RX_CATALOGO.search(especificacion or "")
    return m.group(1) if m else ""

# Orden de columnas de salida (una fila por ítem).
COLUMNS = [
    "codigo_oc",
    "nombre_oc",
    "fecha_creacion",
    "tipo",
    "codigo_licitacion",
    "estado",
    "organismo_codigo",
    "organismo_nombre",
    "organismo_rut",
    "comuna",
    "region",
    "proveedor_codigo",
    "proveedor_nombre",
    "proveedor_rut",
    "proveedor_comuna",
    "proveedor_region",
    "item_correlativo",
    "codigo_categoria",
    "categoria",
    "codigo_producto",
    "catalogo_id",
    "producto",
    "especificacion_comprador",
    "cantidad",
    "unidad",
    "moneda",
    "precio_neto_unitario",
    "total_linea_derivado",
    "total_item_reportado",
]


def _num(value: Any) -> float | None:
    """Convierte a float de forma tolerante; None si no se puede."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def iter_items_from_oc(oc: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Aplana una OC (dict) en filas de ítem. Sin ítems → no rinde filas."""
    items = (oc.get("Items") or {}).get("Listado") or []
    if not items:
        return

    comprador = oc.get("Comprador") or {}
    proveedor = oc.get("Proveedor") or {}

    base = {
        "codigo_oc": oc.get("Codigo", ""),
        "nombre_oc": oc.get("Nombre", ""),
        "fecha_creacion": (oc.get("Fechas") or {}).get("FechaCreacion", ""),
        "tipo": oc.get("Tipo", ""),
        "codigo_licitacion": oc.get("CodigoLicitacion", ""),
        "estado": oc.get("Estado", ""),
        "organismo_codigo": comprador.get("CodigoOrganismo", ""),
        "organismo_nombre": comprador.get("NombreOrganismo", ""),
        "organismo_rut": comprador.get("RutUnidad", ""),
        "comuna": comprador.get("ComunaUnidad", ""),
        "region": comprador.get("RegionUnidad", ""),
        "proveedor_codigo": proveedor.get("Codigo", ""),
        "proveedor_nombre": proveedor.get("Nombre", ""),
        "proveedor_rut": proveedor.get("RutSucursal", ""),
        "proveedor_comuna": proveedor.get("Comuna", ""),
        "proveedor_region": proveedor.get("Region", ""),
    }

    for it in items:
        cantidad = _num(it.get("Cantidad"))
        precio = _num(it.get("PrecioNeto"))
        total_derivado = (
            round(precio * cantidad, 4)
            if precio is not None and cantidad is not None
            else None
        )
        row = dict(base)
        row.update(
            {
                "item_correlativo": it.get("Correlativo", ""),
                "codigo_categoria": it.get("CodigoCategoria", ""),
                "categoria": it.get("Categoria", ""),
                "codigo_producto": it.get("CodigoProducto", ""),
                "catalogo_id": extraer_catalogo_id(it.get("EspecificacionComprador")),
                "producto": it.get("Producto", ""),
                "especificacion_comprador": it.get("EspecificacionComprador", ""),
                "cantidad": cantidad if cantidad is not None else "",
                "unidad": it.get("Unidad") or "",
                "moneda": it.get("Moneda", ""),
                "precio_neto_unitario": precio if precio is not None else "",
                "total_linea_derivado": total_derivado if total_derivado is not None else "",
                "total_item_reportado": _num(it.get("Total")) or 0.0,
            }
        )
        yield row


def iter_items_from_payload(payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Recorre el `Listado` de un payload (detalle o día) y rinde filas de ítem."""
    if not isinstance(payload, dict):
        return
    for oc in payload.get("Listado") or []:
        if isinstance(oc, dict):
            yield from iter_items_from_oc(oc)


def parse_files(paths: list[Path]) -> list[dict[str, Any]]:
    """Aplana todos los JSON dados a una lista de filas de ítem."""
    rows: list[dict[str, Any]] = []
    for p in paths:
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as err:
            print(f"  aviso: no se pudo leer {p.name}: {err}")
            continue
        rows.extend(iter_items_from_payload(payload))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--entrada",
        default="data/raw",
        help="Archivo o directorio con JSON crudos (default: data/raw, recursivo).",
    )
    parser.add_argument(
        "--salida",
        default="data/interim/items.csv",
        help="CSV de salida (default: data/interim/items.csv).",
    )
    args = parser.parse_args(argv)

    entrada = (REPO_ROOT / args.entrada) if not Path(args.entrada).is_absolute() else Path(args.entrada)
    if entrada.is_dir():
        paths = sorted(entrada.rglob("*.json"))
    elif entrada.is_file():
        paths = [entrada]
    else:
        print(f"No existe la entrada: {entrada}")
        return 1

    print(f"Leyendo {len(paths)} archivo(s) desde {entrada}...")
    rows = parse_files(paths)
    print(f"Ítems extraídos: {len(rows)}")

    salida = (REPO_ROOT / args.salida) if not Path(args.salida).is_absolute() else Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV escrito en: {salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
