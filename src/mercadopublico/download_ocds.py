"""Vía masiva OCDS — descarga archivos históricos de datos-abiertos.chilecompra.cl.

Es el camino correcto para el HISTÓRICO (§3.3 del maestro): en vez de barrer la API
detalle-a-detalle (lenta, rate-limited), se bajan archivos masivos ya publicados.

Este script solo DESCARGA (streaming, reanudable, descomprime .zip). El shape real
se inspecciona luego con `inspeccionar_ocds.py` y se parsea con `parse_ocds.py`
(mismo patrón de dos pasos que usamos en Fase 0).

De dónde sacar las URLs (páginas del portal — abrir en el navegador y copiar el link
del archivo del período que quieras):
  - Procesos OCDS:            https://datos-abiertos.chilecompra.cl/descargas/procesos-ocds
  - OC y licitaciones masivo: https://datos-abiertos.chilecompra.cl/descargas/ordenes-y-licitaciones

Uso:
    python -m mercadopublico.download_ocds --url "<URL del archivo>"
    python -m mercadopublico.download_ocds --url "<URL>.zip" --nombre ocds-2024-01.zip

Nota: las URLs exactas y el formato (JSON OCDS vs CSV) hay que CONFIRMARLOS con un
archivo real; por eso el paso siguiente es inspeccionar lo descargado.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import requests

from .config import RAW_DIR

OCDS_DIR = RAW_DIR / "ocds"
CHUNK = 1 << 20  # 1 MB


def descargar(url: str, nombre: str | None = None) -> Path:
    OCDS_DIR.mkdir(parents=True, exist_ok=True)
    nombre = nombre or Path(urlparse(url).path).name or "descarga_ocds.bin"
    destino = OCDS_DIR / nombre
    print(f"Descargando {url}\n  -> {destino}")

    headers = {"User-Agent": "mercado-publico-cl-ingesta/0.1 (OCDS masivo)"}
    with requests.get(url, headers=headers, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("Content-Length", 0))
        bajado = 0
        with destino.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=CHUNK):
                if not chunk:
                    continue
                f.write(chunk)
                bajado += len(chunk)
                if total:
                    pct = 100 * bajado / total
                    print(f"\r  {bajado/1e6:,.1f} / {total/1e6:,.1f} MB ({pct:.0f}%)", end="", file=sys.stderr)
                else:
                    print(f"\r  {bajado/1e6:,.1f} MB", end="", file=sys.stderr)
    print(file=sys.stderr)
    print(f"Listo: {destino} ({destino.stat().st_size/1e6:,.1f} MB)")

    if zipfile.is_zipfile(destino):
        carpeta = OCDS_DIR / (destino.stem + "_extraido")
        carpeta.mkdir(exist_ok=True)
        with zipfile.ZipFile(destino) as z:
            z.extractall(carpeta)
            nombres = z.namelist()
        print(f"ZIP descomprimido en: {carpeta}")
        print(f"  Contiene {len(nombres)} archivo(s); primeros: {nombres[:5]}")
        print("Siguiente: python -m mercadopublico.inspeccionar_ocds --archivo "
              f"{carpeta}/{nombres[0] if nombres else ''}")
    else:
        print("Siguiente: python -m mercadopublico.inspeccionar_ocds --archivo " + str(destino))
    return destino


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True, help="URL del archivo masivo (del portal datos-abiertos).")
    ap.add_argument("--nombre", default=None, help="Nombre de archivo de salida (opcional).")
    args = ap.parse_args(argv)
    try:
        descargar(args.url, args.nombre)
    except requests.RequestException as err:
        print(f"Error de descarga: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
