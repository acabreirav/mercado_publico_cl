"""Fase 1 — Descargador por lotes: baja el DETALLE de muchas OC de un día.

Flujo de dos pasos (ver docs/mercado-publico-referencia.md §3.1):
  1. Lista las OC del día (Codigo/Nombre/Estado).
  2. Por cada Codigo, baja el detalle completo (ítems, precio, proveedor) y lo
     guarda crudo en data/raw/detalles/<codigo>.json.

Pensado para respetar el rate limit (10.000 req/día por ticket, ver §4.3):
  - Es IDEMPOTENTE: si el detalle ya existe en disco, lo salta (re-correr no
    re-descarga ni gasta cuota).
  - Pausa configurable entre llamadas (--pausa).
  - Tope de descargas por corrida (--limit) y de requests totales (--max-requests).

Uso:
    python -m mercadopublico.download_lote_detalles --fecha 2024-03-04 --limit 200
    python -m mercadopublico.download_lote_detalles --fecha 2024-03-04 --pausa 0.3
    # reanudar: volver a correr el mismo comando; salta lo ya bajado.

NOTA: el listado del día se cachea en data/raw/ (lo reusa si ya está y no se pasa
--refrescar-listado), para no gastar una llamada extra al reanudar.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import time
from pathlib import Path
from typing import Any

from .api_client import fetch_json
from .config import RAW_DIR, get_ticket
from .download_detalle_oc import fetch_detalle
from .download_ordenes_dia import parse_fecha

DETALLES_DIR = RAW_DIR / "detalles"


def _codigo_a_archivo(codigo: str) -> Path:
    """Ruta estable (idempotente) del detalle de una OC en disco."""
    safe = codigo.replace("/", "-")
    return DETALLES_DIR / f"{safe}.json"


def obtener_listado_dia(ticket: str, fecha: str, refrescar: bool) -> dict[str, Any]:
    """Devuelve el listado del día. Reusa el cache en data/raw/ si existe."""
    cache = RAW_DIR / f"listado_dia_{fecha}.json"
    if cache.exists() and not refrescar:
        print(f"Usando listado cacheado: {cache.name}")
        return json.loads(cache.read_text(encoding="utf-8"))

    print(f"Descargando listado del día fecha={fecha}...")
    payload, _ = fetch_json("ordenesdecompra.json", ticket, {"fecha": fecha})
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def descargar_lote(
    ticket: str,
    fecha: str,
    *,
    limit: int | None,
    pausa: float,
    max_requests: int,
    refrescar_listado: bool,
) -> None:
    DETALLES_DIR.mkdir(parents=True, exist_ok=True)

    payload = obtener_listado_dia(ticket, fecha, refrescar_listado)
    listado = payload.get("Listado") or []
    codigos = [oc.get("Codigo") for oc in listado if isinstance(oc, dict) and oc.get("Codigo")]
    print(f"OC en el día: {len(codigos)}")

    pendientes = [c for c in codigos if not _codigo_a_archivo(c).exists()]
    ya_bajadas = len(codigos) - len(pendientes)
    print(f"Ya en disco: {ya_bajadas} | Pendientes: {len(pendientes)}")

    if limit is not None:
        pendientes = pendientes[:limit]
        print(f"Esta corrida bajará hasta {len(pendientes)} (por --limit).")

    requests_hechos = 0
    bajadas = 0
    errores = 0
    for i, codigo in enumerate(pendientes, start=1):
        if requests_hechos >= max_requests:
            print(f"Tope de requests alcanzado (--max-requests={max_requests}). Corta.")
            break
        try:
            detalle, _ = fetch_detalle(ticket, codigo)
            requests_hechos += 1
            _codigo_a_archivo(codigo).write_text(
                json.dumps(detalle, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            bajadas += 1
        except Exception as err:  # noqa: BLE001 - registrar y seguir con el lote
            errores += 1
            print(f"  [{i}/{len(pendientes)}] error en {codigo}: {err}")
            continue

        if i % 25 == 0 or i == len(pendientes):
            print(f"  [{i}/{len(pendientes)}] {codigo} OK (bajadas={bajadas}, errores={errores})")
        if pausa > 0 and i < len(pendientes):
            time.sleep(pausa)

    print(
        f"\nListo. Bajadas esta corrida: {bajadas} | errores: {errores} | "
        f"requests usados: {requests_hechos}"
    )
    print(f"Detalles crudos en: {DETALLES_DIR}")
    print("Siguiente paso: python -m mercadopublico.parse_items")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fecha", required=True, help="YYYY-MM-DD, DD-MM-YYYY o ddmmaaaa.")
    parser.add_argument(
        "--limit", type=int, default=None, help="Máx. de detalles a bajar esta corrida."
    )
    parser.add_argument(
        "--pausa", type=float, default=0.2, help="Segundos entre llamadas (default 0.2)."
    )
    parser.add_argument(
        "--max-requests",
        type=int,
        default=9000,
        help="Tope de requests por corrida, margen bajo el límite diario de 10.000.",
    )
    parser.add_argument(
        "--refrescar-listado",
        action="store_true",
        help="Vuelve a pedir el listado del día en vez de usar el cache.",
    )
    args = parser.parse_args(argv)

    ticket = get_ticket()
    fecha = parse_fecha(args.fecha)
    inicio = dt.datetime.now()
    descargar_lote(
        ticket,
        fecha,
        limit=args.limit,
        pausa=args.pausa,
        max_requests=args.max_requests,
        refrescar_listado=args.refrescar_listado,
    )
    print(f"Duración: {dt.datetime.now() - inicio}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
