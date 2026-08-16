"""Cosechador OCDS — baja TODOS los registros de un año/mes desde la API OCDS paginada.

API OCDS de Mercado Público (1.000 registros por consulta, se itera por lotes):
  Licitación:     .../APISOCDS/OCDS/listaOCDSAgnoMes/{año}/{mes}/{ini}/{fin}
  Trato directo:  .../APISOCDS/OCDS/listaOCDSAgnoMesTratoDirecto/{año}/{mes}/{ini}/{fin}
  Convenio marco: .../APISOCDS/OCDS/listaOCDSAgnoMesConvenio/{año}/{mes}/{ini}/{fin}

Es la vía EFICIENTE (bulk): un mes son ~decenas de llamadas de 1.000, no miles.
Guarda cada página cruda en data/raw/ocds/<tipo>/<año><mes>/ y es IDEMPOTENTE
(re-correr salta páginas ya bajadas). Itera hasta que una página trae < 1.000
registros (última página). Licitaciones desde 2009; Convenio/Trato Directo desde 2019.

Uso:
    python -m mercadopublico.cosechar_ocds --tipo tratodirecto --anio 2020 --meses 01
    python -m mercadopublico.cosechar_ocds --tipo todos --anio 2024 --meses 01,02,03
    python -m mercadopublico.cosechar_ocds --tipo licitacion --anio 2024 --meses 01

Luego:  python -m mercadopublico.parse_ocds --entrada data/raw/ocds/tratodirecto/202001
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import time
from pathlib import Path

from .api_client import fetch_url
from .config import RAW_DIR
from .parse_ocds import _releases

BASE = "https://api.mercadopublico.cl/APISOCDS/OCDS"
ENDPOINTS = {
    "licitacion": "listaOCDSAgnoMes",
    "tratodirecto": "listaOCDSAgnoMesTratoDirecto",
    "convenio": "listaOCDSAgnoMesConvenio",
}
LOTE = 1000
MAX_PAGINAS = 500  # tope de seguridad (500k registros/mes)
MIN_DELAY, MAX_DELAY = 0.3, 8.0


def _rango(k: int) -> tuple[int, int]:
    """Rango [ini, fin] del lote k, siguiendo la convención: (0,1000),(1001,2000)…"""
    if k == 0:
        return 0, LOTE
    ini = k * LOTE + 1
    return ini, ini + LOTE - 1


def cosechar_mes(tipo: str, anio: int, mes: str, pausa_inicial: float) -> int:
    endpoint = ENDPOINTS[tipo]
    carpeta = RAW_DIR / "ocds" / tipo / f"{anio}{mes}"
    carpeta.mkdir(parents=True, exist_ok=True)
    print(f"\n== {tipo} {anio}-{mes} ==")

    delay = pausa_inicial
    total = 0
    n429 = 0
    for k in range(MAX_PAGINAS):
        ini, fin = _rango(k)
        destino = carpeta / f"p{k:03d}_{ini}-{fin}.json"

        if destino.exists() and destino.stat().st_size > 0:
            data = json.loads(destino.read_text(encoding="utf-8"))
            n = len(_releases(data))
            total += n
            if n < LOTE:
                print(f"  (cache) lote {k} [{ini}-{fin}]: {n} → última página")
                break
            continue

        url = f"{BASE}/{endpoint}/{anio}/{mes}/{ini}/{fin}"
        stats: dict[str, int] = {}
        try:
            data = fetch_url(url, stats=stats)
        except Exception as err:  # noqa: BLE001
            print(f"  error lote {k} [{ini}-{fin}]: {err}")
            break
        n = len(_releases(data))
        destino.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        total += n
        print(f"  lote {k} [{ini}-{fin}]: {n} registros (acum {total})")

        # ritmo adaptativo simple
        if stats.get("n429"):
            n429 += stats["n429"]; delay = min(MAX_DELAY, delay * 1.6 + 0.4)
        else:
            delay = max(MIN_DELAY, delay * 0.92)

        if n < LOTE:  # última página
            break
        time.sleep(delay)

    print(f"  Total {tipo} {anio}-{mes}: {total} registros (429s={n429}) → {carpeta}")
    return total


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tipo", required=True, choices=list(ENDPOINTS) + ["todos"])
    ap.add_argument("--anio", required=True, type=int)
    ap.add_argument("--meses", required=True, help="Meses de 2 dígitos, coma-separados. Ej: 01,02,03")
    ap.add_argument("--pausa", type=float, default=0.5, help="Pausa inicial entre lotes (s).")
    args = ap.parse_args(argv)

    tipos = list(ENDPOINTS) if args.tipo == "todos" else [args.tipo]
    meses = [m.strip().zfill(2) for m in args.meses.split(",") if m.strip()]
    inicio = dt.datetime.now()
    gran_total = 0
    for tipo in tipos:
        for mes in meses:
            gran_total += cosechar_mes(tipo, args.anio, mes, args.pausa)
    print(f"\n=== Gran total: {gran_total} registros en {dt.datetime.now()-inicio} ===")
    print("Siguiente: python -m mercadopublico.parse_ocds --entrada data/raw/ocds/<tipo>/<añomes>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
