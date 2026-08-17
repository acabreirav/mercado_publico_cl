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
V = ROOT / "docs" / "visual"
DP = ROOT / "data" / "processed"

# (plantilla, datos, salida) de cada visual autocontenido.
VISUALES = [
    (V / "_plantilla.html", DP / "viz_comparador.json", V / "comparador-precios.html"),
    (V / "_plantilla_ahorro.html", DP / "viz_ahorro.json", V / "ahorro-potencial.html"),
]


def build(tpl: Path, json_: Path, out: Path) -> bool:
    if not tpl.exists() or not json_.exists():
        print(f"  (salto {out.name}: falta {'plantilla' if not tpl.exists() else json_.name})")
        return False
    data = json_.read_text(encoding="utf-8").replace("</script>", "<\\/script>")
    out.write_text(tpl.read_text(encoding="utf-8").replace("__DATA__", data), encoding="utf-8")
    print(f"HTML escrito: {out.name} ({out.stat().st_size//1024} KB)")
    return True


def main() -> int:
    hechos = sum(build(*v) for v in VISUALES)
    return 0 if hechos else 1


if __name__ == "__main__":
    raise SystemExit(main())
