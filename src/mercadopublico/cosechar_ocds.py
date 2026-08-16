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


def _n_registros(data) -> int:
    """Cuenta registros en una página del ÍNDICE OCDS ({pagination, data:[...]})."""
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        return len(data["data"])
    return 0


def _total(data) -> int | None:
    if isinstance(data, dict):
        return (data.get("pagination") or {}).get("total")
    return None

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


def _codigo_de_ocid(ocid: str) -> str:
    return ocid.split("-", 2)[-1] if isinstance(ocid, str) and "-" in ocid else str(ocid)


def cosechar_indice(tipo: str, anio: int, mes: str, pausa_inicial: float) -> list[tuple[str, str]]:
    """FASE 1: pagina el índice y devuelve [(codigo, urlAward)] de todo el mes."""
    endpoint = ENDPOINTS[tipo]
    carpeta = RAW_DIR / "ocds" / tipo / f"{anio}{mes}"
    carpeta.mkdir(parents=True, exist_ok=True)
    print(f"\n== índice {tipo} {anio}-{mes} ==")

    entradas: list[tuple[str, str]] = []
    delay = pausa_inicial
    total = 0
    n429 = 0
    for k in range(MAX_PAGINAS):
        ini, fin = _rango(k)
        destino = carpeta / f"p{k:03d}_{ini}-{fin}.json"
        if destino.exists() and destino.stat().st_size > 0:
            data = json.loads(destino.read_text(encoding="utf-8"))
        else:
            url = f"{BASE}/{endpoint}/{anio}/{mes}/{ini}/{fin}"
            stats: dict[str, int] = {}
            try:
                data = fetch_url(url, stats=stats)
            except Exception as err:  # noqa: BLE001
                print(f"  error lote {k} [{ini}-{fin}]: {err}")
                break
            destino.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            if stats.get("n429"):
                n429 += stats["n429"]; delay = min(MAX_DELAY, delay * 1.6 + 0.4)
            else:
                delay = max(MIN_DELAY, delay * 0.92)
            time.sleep(delay)

        n = _n_registros(data)
        total += n
        tot = _total(data)
        for e in (data.get("data") or []):
            if e.get("urlAward"):
                entradas.append((_codigo_de_ocid(e.get("ocid", "")), e["urlAward"]))
        print(f"  lote {k} [{ini}-{fin}]: {n} (acum {total}/{tot or '?'})")
        if n < LOTE or (tot and total >= tot):
            break
    print(f"  índice {tipo} {anio}-{mes}: {len(entradas)} urlAwards (429s={n429})")
    return entradas


def bajar_detalles(tipo: str, anio: int, mes: str, entradas: list[tuple[str, str]],
                   pausa_inicial: float, limit: int | None) -> int:
    """FASE 2: baja el detalle (award) de cada urlAward. http→https, idempotente, AIMD."""
    awards_dir = RAW_DIR / "ocds" / tipo / f"{anio}{mes}" / "awards"
    awards_dir.mkdir(parents=True, exist_ok=True)
    pendientes = [(c, u) for c, u in entradas if not (awards_dir / f"{c}.json").exists()]
    print(f"  detalles: {len(entradas)} totales, {len(pendientes)} pendientes"
          + (f" (esta corrida hasta {limit})" if limit else ""))
    if limit:
        pendientes = pendientes[:limit]

    delay = pausa_inicial
    bajadas = errores = n429 = 0
    for i, (codigo, url) in enumerate(pendientes, 1):
        url = url.replace("http://", "https://", 1)  # el award solo responde por https
        stats: dict[str, int] = {}
        try:
            data = fetch_url(url, stats=stats)
            (awards_dir / f"{codigo}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            bajadas += 1
        except Exception as err:  # noqa: BLE001
            errores += 1
            print(f"    [{i}/{len(pendientes)}] error {codigo}: {err}")
        if stats.get("n429"):
            n429 += stats["n429"]; delay = min(MAX_DELAY, delay * 1.6 + 0.4)
        else:
            delay = max(MIN_DELAY, delay * 0.92)
        if i % 100 == 0 or i == len(pendientes):
            print(f"    [{i}/{len(pendientes)}] bajadas={bajadas} errores={errores} pausa≈{delay:.1f}s 429s={n429}")
        if i < len(pendientes):
            time.sleep(delay)
    print(f"  detalles {tipo} {anio}-{mes}: {bajadas} bajadas, {errores} errores → {awards_dir}")
    return bajadas


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tipo", required=True, choices=list(ENDPOINTS) + ["todos"])
    ap.add_argument("--anio", required=True, type=int)
    ap.add_argument("--meses", required=True, help="Meses de 2 dígitos, coma-separados. Ej: 01,02,03")
    ap.add_argument("--detalle", action="store_true",
                    help="Además del índice, baja el detalle (award) de cada registro.")
    ap.add_argument("--limit-detalle", type=int, default=None,
                    help="Máx. de detalles a bajar por mes esta corrida (para probar de a poco).")
    ap.add_argument("--pausa", type=float, default=0.5, help="Pausa inicial entre llamadas (s).")
    args = ap.parse_args(argv)

    tipos = list(ENDPOINTS) if args.tipo == "todos" else [args.tipo]
    meses = [m.strip().zfill(2) for m in args.meses.split(",") if m.strip()]
    inicio = dt.datetime.now()
    for tipo in tipos:
        for mes in meses:
            entradas = cosechar_indice(tipo, args.anio, mes, args.pausa)
            if args.detalle:
                bajar_detalles(tipo, args.anio, mes, entradas, args.pausa, args.limit_detalle)
    print(f"\n=== Terminado en {dt.datetime.now()-inicio} ===")
    if args.detalle:
        print("Siguiente: python -m mercadopublico.parse_ocds --entrada data/raw/ocds/<tipo>/<añomes>/awards")
    else:
        print("Índice listo. Para bajar los detalles, agrega --detalle (y opcional --limit-detalle 500).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
