"""Fase 0 (paso 2) — Baja el DETALLE de una orden de compra por su Codigo.

El listado "por día" solo trae Codigo/Nombre/Estado. La ficha completa —con
ítems, cantidades, precio unitario, proveedor (RUT) y organismo comprador— se
pide por `codigo`. Este script la baja CRUDA y resume su shape para inspección.

Uso:
    python -m mercadopublico.download_detalle_oc --codigo 1001546-22-AG24

Endpoint (ver docs/contexto-compras-publicas-chile.md §3.1):
    GET /servicios/v1/publico/ordenesdecompra.json?codigo=<CODIGO>&ticket=<TICKET>
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

from .api_client import fetch_json
from .config import RAW_DIR, get_ticket


def fetch_detalle(ticket: str, codigo: str) -> tuple[dict[str, Any], str]:
    """Pide la ficha de una OC por su código. Devuelve (json, url_sin_ticket)."""
    return fetch_json("ordenesdecompra.json", ticket, {"codigo": codigo})


def save_raw(payload: dict[str, Any], codigo: str) -> Path:
    """Guarda el JSON crudo del detalle en data/raw/ con nombre trazable."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    safe_codigo = codigo.replace("/", "-")
    out = RAW_DIR / f"detalle_oc_{safe_codigo}_{stamp}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def _print_keys(label: str, obj: Any) -> None:
    if isinstance(obj, dict):
        print(f"{label}: {list(obj.keys())}")
    elif isinstance(obj, list):
        print(f"{label}: lista de {len(obj)} elementos")
        if obj and isinstance(obj[0], dict):
            print(f"{label}[0] claves: {list(obj[0].keys())}")
    else:
        print(f"{label}: {type(obj).__name__}")


def summarize(payload: dict[str, Any]) -> None:
    """Recorre el shape del detalle para ubicar dónde vienen ítems/precio/proveedor."""
    print("\n=== Resumen del shape (detalle OC) ===")
    if not isinstance(payload, dict):
        print(f"Respuesta no es objeto JSON: {type(payload).__name__}")
        return

    _print_keys("Nivel superior", payload)

    listado = payload.get("Listado")
    if isinstance(listado, list) and listado and isinstance(listado[0], dict):
        oc = listado[0]
        print("\n-- Ficha de la OC (Listado[0]) --")
        _print_keys("Claves de la OC", oc)
        # Explora sub-objetos frecuentes sin asumir nombres exactos.
        for k, v in oc.items():
            if isinstance(v, (dict, list)):
                _print_keys(f"  {k}", v)

    print("\n-- JSON crudo (recorte de 3000 chars) --")
    print(json.dumps(payload, ensure_ascii=False, indent=2)[:3000])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--codigo",
        required=True,
        help="Código de la orden de compra (ej. 1001546-22-AG24).",
    )
    args = parser.parse_args(argv)

    ticket = get_ticket()
    print(f"Consultando detalle de la OC codigo={args.codigo}...")

    payload, url_safe = fetch_detalle(ticket, args.codigo)
    print(f"OK. URL (sin ticket): {url_safe}")

    out = save_raw(payload, args.codigo)
    print(f"JSON crudo guardado en: {out.relative_to(RAW_DIR.parent.parent)}")

    summarize(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
