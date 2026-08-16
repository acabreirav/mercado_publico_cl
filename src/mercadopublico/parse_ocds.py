"""Parser OCDS (estándar 1.1) → tabla de ítems (mismo esquema que parse_items).

Convierte archivos OCDS (release/record packages) al mismo CSV de ítems que usa el
resto del pipeline, para que comparador/estimador funcionen igual con data masiva.

Ventaja clave: el estándar OCDS trae `item.unit` (unidad de medida) y `item.quantity`
→ puede resolver el problema base que la API de OC no informaba (D11). Se confirma al
correrlo sobre un archivo real (por eso primero se inspecciona el shape).

Es best-effort según el estándar; si ChileCompra usa extensiones o nombres distintos,
ajustar los mapeos tras inspeccionar (`inspeccionar_ocds.py`).

Uso:
    python -m mercadopublico.parse_ocds --entrada data/raw/ocds/<archivo_o_carpeta>
    python -m mercadopublico.parse_ocds --entrada <...> --salida data/interim/items_ocds.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Iterator

from .config import REPO_ROOT
from .parse_items import COLUMNS, extraer_catalogo_id


def _num(v: Any) -> Any:
    try:
        return float(v)
    except (TypeError, ValueError):
        return ""


def _releases(data: Any) -> list[dict]:
    """Extrae la lista de releases de un package OCDS (release o record)."""
    if isinstance(data, dict):
        if isinstance(data.get("releases"), list):
            return data["releases"]
        if isinstance(data.get("records"), list):
            out = []
            for rec in data["records"]:
                comp = rec.get("compiledRelease")
                if comp:
                    out.append(comp)
                elif isinstance(rec.get("releases"), list) and rec["releases"]:
                    out.append(rec["releases"][-1])
            return out
    if isinstance(data, list):  # a veces viene como lista de releases
        return data
    return []


def _party_index(release: dict) -> dict[str, dict]:
    return {p.get("id"): p for p in (release.get("parties") or []) if isinstance(p, dict)}


def _region_de(party: dict | None) -> str:
    if not party:
        return ""
    addr = party.get("address") or {}
    return addr.get("region") or addr.get("countrySubdivision") or ""


def iter_items(release: dict) -> Iterator[dict[str, Any]]:
    parties = _party_index(release)
    buyer = release.get("buyer") or {}
    buyer_party = parties.get(buyer.get("id")) or {}
    tender = release.get("tender") or {}

    base = {c: "" for c in COLUMNS}
    ocid = release.get("ocid") or release.get("id") or ""
    base.update({
        "codigo_oc": ocid.replace("ocds-", "") if isinstance(ocid, str) else ocid,
        "nombre_oc": tender.get("title", ""),
        "fecha_creacion": release.get("date", ""),
        "tipo": tender.get("procurementMethodDetails") or tender.get("procurementMethod", ""),
        "estado": tender.get("status", ""),
        "organismo_nombre": buyer.get("name") or buyer_party.get("name", ""),
        "organismo_rut": (buyer_party.get("identifier") or {}).get("id", ""),
        "comuna": ((buyer_party.get("address") or {}).get("locality", "")),
        "region": _region_de(buyer_party),
    })

    # Los ítems (y su adjudicación) viven en awards y/o contracts.
    for cont in ("awards", "contracts"):
        for a in (release.get(cont) or []):
            if not isinstance(a, dict):
                continue
            suppliers = a.get("suppliers") or []
            sup = suppliers[0] if suppliers else {}
            sup_party = parties.get(sup.get("id")) or {}
            moneda_a = ((a.get("value") or {}).get("currency", ""))
            for it in (a.get("items") or []):
                if not isinstance(it, dict):
                    continue
                clf = it.get("classification") or {}
                unit = it.get("unit") or {}
                unit_val = unit.get("value") or {}
                desc = it.get("description", "")
                row = dict(base)
                row.update({
                    "proveedor_nombre": sup.get("name") or sup_party.get("name", ""),
                    "proveedor_rut": (sup_party.get("identifier") or {}).get("id", ""),
                    "proveedor_comuna": (sup_party.get("address") or {}).get("locality", ""),
                    "proveedor_region": _region_de(sup_party),
                    "codigo_categoria": clf.get("id", "") if clf.get("scheme", "").upper().startswith("UNSPSC") else "",
                    "categoria": clf.get("description", ""),
                    "codigo_producto": clf.get("id", ""),
                    "catalogo_id": extraer_catalogo_id(desc),
                    "producto": clf.get("description") or desc,
                    "especificacion_comprador": desc,
                    "cantidad": _num(it.get("quantity")),
                    "unidad": unit.get("name", ""),  # <-- unidad de medida (clave)
                    "moneda": unit_val.get("currency") or moneda_a,
                    "precio_neto_unitario": _num(unit_val.get("amount")),
                })
                yield row


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entrada", required=True, help="Archivo .json o carpeta con .json OCDS.")
    ap.add_argument("--salida", default="data/interim/items_ocds.csv")
    args = ap.parse_args(argv)

    entrada = Path(args.entrada)
    if not entrada.is_absolute():
        entrada = REPO_ROOT / entrada
    if entrada.is_dir():
        paths = sorted(entrada.rglob("*.json"))
    elif entrada.exists():
        paths = [entrada]
    else:
        print(f"No existe: {entrada}")
        return 1

    rows: list[dict] = []
    con_unidad = 0
    for p in paths:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as err:
            print(f"  aviso: {p.name}: {err}")
            continue
        for rel in _releases(data):
            for row in iter_items(rel):
                rows.append(row)
                if (row.get("unidad") or "").strip():
                    con_unidad += 1

    print(f"Archivos: {len(paths)} | ítems extraídos: {len(rows)}")
    if rows:
        print(f"Ítems con unidad de medida: {con_unidad} ({100*con_unidad/len(rows):.0f}%) "
              f"{'← ¡OCDS sí trae unidad!' if con_unidad else '← no vino unidad; revisar mapeo'}")

    salida = REPO_ROOT / args.salida if not Path(args.salida).is_absolute() else Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"CSV escrito en: {salida}")
    print("Siguiente: python -m mercadopublico.comparador_identicos --entrada " + str(salida))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
