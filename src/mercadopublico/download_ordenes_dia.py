"""Fase 0 — Baja UN día de órdenes de compra y guarda el JSON CRUDO para inspección.

Objetivo de esta fase: validar el *shape* del JSON que devuelve la API antes de
modelar nada. No transforma ni normaliza: solo pide, guarda crudo y resume.

Uso:
    python -m mercadopublico.download_ordenes_dia                 # ayer
    python -m mercadopublico.download_ordenes_dia --fecha 2014-02-02
    python -m mercadopublico.download_ordenes_dia --fecha 02022014
    python -m mercadopublico.download_ordenes_dia --estado todos  # día actual, por estado

Endpoint (ver docs/contexto-compras-publicas-chile.md §3.1):
    GET /servicios/v1/publico/ordenesdecompra.json?fecha=<ddmmaaaa>&ticket=<TICKET>

El ticket se lee del entorno (.env). Nunca se imprime ni se guarda en disco.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path
from typing import Any

import requests

from .config import API_BASE, RAW_DIR, get_ticket

USER_AGENT = "mercado-publico-cl-ingesta/0.0 (fase0; inspeccion de shape)"
TIMEOUT_S = 60
MAX_RETRIES = 4


def parse_fecha(value: str | None) -> str:
    """Normaliza una fecha a `ddmmaaaa` (formato que exige la API).

    Acepta `YYYY-MM-DD`, `DD-MM-YYYY` o `ddmmaaaa`. Si es None, usa AYER
    (el día actual suele venir incompleto).
    """
    if value is None:
        d = dt.date.today() - dt.timedelta(days=1)
        return d.strftime("%d%m%Y")

    v = value.strip()
    if v.isdigit() and len(v) == 8:  # ya viene como ddmmaaaa
        return v
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return dt.datetime.strptime(v, fmt).strftime("%d%m%Y")
        except ValueError:
            continue
    raise ValueError(
        f"Fecha no reconocida: {value!r}. Usa YYYY-MM-DD, DD-MM-YYYY o ddmmaaaa."
    )


def fetch_ordenes(
    ticket: str, *, fecha: str | None = None, estado: str | None = None
) -> tuple[dict[str, Any], str]:
    """Pide las órdenes de compra a la API. Devuelve (json, url_sin_ticket).

    Reintenta con backoff exponencial ante errores de red / 5xx / 429.
    """
    params: dict[str, str] = {}
    if fecha is not None:
        params["fecha"] = fecha
    if estado is not None:
        params["estado"] = estado

    url = f"{API_BASE}/ordenesdecompra.json"
    # URL para logs/metadata SIN el ticket (no filtrar la credencial).
    url_safe = url + "?" + "&".join(f"{k}={v}" for k, v in params.items())

    request_params = {**params, "ticket": ticket}
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url, params=request_params, headers=headers, timeout=TIMEOUT_S
            )
            if resp.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"HTTP {resp.status_code}", response=resp)
            resp.raise_for_status()
            return resp.json(), url_safe
        except (requests.RequestException, ValueError) as err:
            last_err = err
            if attempt == MAX_RETRIES:
                break
            wait = 2**attempt  # 2, 4, 8, 16
            print(
                f"  intento {attempt} falló ({err}); reintentando en {wait}s...",
                file=sys.stderr,
            )
            time.sleep(wait)

    raise RuntimeError(f"No se pudo obtener la data tras {MAX_RETRIES} intentos: {last_err}")


def save_raw(payload: dict[str, Any], *, fecha: str | None, estado: str | None) -> Path:
    """Guarda el JSON crudo en data/raw/ con nombre trazable y timestamp de descarga."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    key = fecha if fecha is not None else f"estado-{estado}"
    out = RAW_DIR / f"ordenesdecompra_{key}_{stamp}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def summarize(payload: dict[str, Any]) -> None:
    """Imprime un resumen del shape para inspección rápida (no transforma)."""
    print("\n=== Resumen del shape ===")
    if not isinstance(payload, dict):
        print(f"Respuesta no es un objeto JSON, es: {type(payload).__name__}")
        return

    print(f"Claves de nivel superior: {list(payload.keys())}")
    cantidad = payload.get("Cantidad")
    if cantidad is not None:
        print(f"Cantidad (según API): {cantidad}")

    listado = payload.get("Listado")
    if isinstance(listado, list):
        print(f"Listado: {len(listado)} elementos")
        if listado:
            primero = listado[0]
            if isinstance(primero, dict):
                print(f"Claves de un elemento del listado: {list(primero.keys())}")
                print("\nPrimer elemento (muestra):")
                print(json.dumps(primero, ensure_ascii=False, indent=2)[:1500])
    else:
        print("No hay 'Listado' tipo lista en la respuesta.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fecha",
        default=None,
        help="Fecha (YYYY-MM-DD, DD-MM-YYYY o ddmmaaaa). Por defecto: ayer.",
    )
    parser.add_argument(
        "--estado",
        default=None,
        help="En vez de fecha, consultar por estado del día actual (ej. 'todos').",
    )
    args = parser.parse_args(argv)

    ticket = get_ticket()

    if args.estado is not None:
        fecha = None
        estado = args.estado
        print(f"Consultando órdenes de compra por estado='{estado}' (día actual)...")
    else:
        fecha = parse_fecha(args.fecha)
        estado = None
        print(f"Consultando órdenes de compra para fecha={fecha} (ddmmaaaa)...")

    payload, url_safe = fetch_ordenes(ticket, fecha=fecha, estado=estado)
    print(f"OK. URL (sin ticket): {url_safe}")

    out = save_raw(payload, fecha=fecha, estado=estado)
    print(f"JSON crudo guardado en: {out.relative_to(RAW_DIR.parent.parent)}")

    summarize(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
