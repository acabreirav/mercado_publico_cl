# Compras públicas de Chile — Mercado Público / ChileCompra

Pipeline de ingesta + informe/web interactiva sobre las compras del Estado chileno,
con foco en **evidencia navegable con drill-down** (comparador de precios,
concentración de proveedores, fragmentación / tipo de proceso).

> **Referencia única del proyecto** (objetivo, fuentes, ambas APIs, diccionarios de datos
> completos, tablas de códigos validadas, trampas conocidas y plan por fases):
> **[`docs/mercado-publico-referencia.md`](docs/mercado-publico-referencia.md)** — léelo primero.
> Las fuentes originales (PDFs oficiales) se conservan en [`docs/fuentes/`](docs/fuentes/) para auditoría.

## Estado actual: Fase 0 (setup)

- Estructura de repo, `.env` / `.env.example` / `.gitignore`.
- Script que baja **un día de órdenes de compra** desde la API y lo guarda **crudo**
  en `data/raw/` para inspeccionar el *shape* del JSON antes de modelar.

## Setup

```bash
# 1) dependencias
pip install -r requirements.txt

# 2) credenciales: copia el ejemplo y completa el ticket
cp .env.example .env
# edita .env y pon MERCADO_PUBLICO_TICKET=<tu-ticket>
```

El ticket se solicita en <https://www.chilecompra.cl/api/>. Nunca se commitea:
`.env` está en `.gitignore` y el código lo lee del entorno.

## Uso (Fase 0)

```bash
# baja las órdenes de compra de AYER y las guarda crudas
PYTHONPATH=src python -m mercadopublico.download_ordenes_dia

# una fecha específica (acepta YYYY-MM-DD, DD-MM-YYYY o ddmmaaaa)
PYTHONPATH=src python -m mercadopublico.download_ordenes_dia --fecha 2024-03-04

# por estado del día actual
PYTHONPATH=src python -m mercadopublico.download_ordenes_dia --estado todos
```

Salida: un JSON crudo en `data/raw/ordenesdecompra_<fecha>_<timestamp>.json` y un
resumen del shape (claves de nivel superior, tamaño del `Listado`, claves de un
elemento y una muestra).

## Uso (Fase 1 — comparador de precios)

Flujo de tres pasos. En Windows usa `py` en vez de `python`.

```bash
# 1) Baja el detalle de muchas OC de un día (dos pasos: listado -> detalle por código).
#    Es idempotente (re-correr salta lo ya bajado) y pausa entre llamadas.
python bajar_lote.py --fecha 2024-03-04 --limit 300

# 2) Aplana los JSON crudos a una tabla de ítems (una fila por línea de compra).
python parsear_items.py

# 3) Comparador: agrupa por producto (UNSPSC) y rankea "mismo producto, precio
#    distinto entre organismos".
python comparar_precios.py
```

Salidas:
- `data/raw/detalles/<codigo>.json` — detalle crudo de cada OC.
- `data/interim/items.csv` — tabla de ítems.
- `data/processed/comparador_precios.csv` — ranking de sobreprecio potencial, con
  `codigos_oc` por fila para el drill-down.

> **Rate limit:** el ticket permite 10.000 requests/día. Un día completo son ~8.500
> OC → cabe, pero conviene bajarlo por lotes (`--limit`) y en horario nocturno para
> descargas grandes. El descargador respeta un tope (`--max-requests`, default 9000).

## Estructura

```
docs/
  mercado-publico-referencia.md        referencia única del proyecto (leer primero)
  discrepancias-fuentes.md             contradicciones entre fuentes, para revisar
  fuentes/                             PDFs oficiales y originales (auditoría)
src/mercadopublico/
  config.py                            carga de .env y rutas (ticket desde entorno)
  api_client.py                        cliente HTTP con reintentos/backoff
  download_ordenes_dia.py              Fase 0: baja 1 día de OC (listado) crudo
  download_detalle_oc.py               Fase 0: baja el detalle de UNA OC por código
  download_lote_detalles.py            Fase 1: baja el detalle de muchas OC (lote)
  parse_items.py                       Fase 1: JSON crudo -> tabla de ítems (CSV)
  comparador.py                        Fase 1: ranking de precio por producto
bajar_ordenes.py / bajar_detalle.py / bajar_lote.py / parsear_items.py / comparar_precios.py
                                       atajos para correr sin PYTHONPATH
data/raw|interim|processed/            datos (no versionados)
.env.example                           variables requeridas (sin valores)
requirements.txt
```

## Notas de cobertura (ver §11 de la referencia)

La data de Mercado Público OCDS **no cubre todo el gasto del Estado**: las empresas
públicas están excluidas. **Compra Ágil** no está en las descargas OCDS, pero **sí**
es accesible por la API (OC tipo `AG` y la API v2 `api2.mercadopublico.cl`). Todo
total es "del universo Mercado Público", no "todo el gasto público".
