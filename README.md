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

## Estructura

```
docs/                                  contexto y documentación del proyecto
src/mercadopublico/
  config.py                            carga de .env y rutas (ticket desde entorno)
  download_ordenes_dia.py              Fase 0: baja 1 día de OC y lo guarda crudo
data/raw/                              JSON crudo de la API (no versionado)
.env.example                           variables requeridas (sin valores)
requirements.txt
```

## Notas de cobertura (ver §6 del contexto)

La data de Mercado Público OCDS **no cubre todo el gasto del Estado**: las empresas
públicas están excluidas y **Compra Ágil no se publica en la API OCDS**. Todo total
es "del universo Mercado Público", no "todo el gasto público".
