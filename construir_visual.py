#!/usr/bin/env python3
"""Construye el HTML final del comparador embebiendo el JSON de datos.

Combina la plantilla docs/visual/_plantilla.html con data/processed/viz_comparador.json
y escribe docs/visual/comparador-precios.html (autocontenido, sin dependencias).

Uso:
    python parsear_items.py            # 1) items.csv
    python -m mercadopublico.preparar_viz   # 2) viz_comparador.json  (o: py -m ...)
    python construir_visual.py         # 3) HTML final
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
TPL = ROOT / "docs" / "visual" / "_plantilla.html"
JSON = ROOT / "data" / "processed" / "viz_comparador.json"
OUT = ROOT / "docs" / "visual" / "comparador-precios.html"


def main() -> int:
    if not JSON.exists():
        print(f"Falta {JSON}. Corre antes: python -m mercadopublico.preparar_viz")
        return 1
    tpl = TPL.read_text(encoding="utf-8")
    data = JSON.read_text(encoding="utf-8").replace("</script>", "<\\/script>")
    OUT.write_text(tpl.replace("__DATA__", data), encoding="utf-8")
    print(f"HTML final escrito en: {OUT} ({OUT.stat().st_size//1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
