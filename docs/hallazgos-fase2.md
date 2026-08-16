# Hallazgos preliminares — Fase 2 (fragmentación H1 y tipo de proceso H3)

> Análisis sobre la **muestra actual** (~18.700 ítems de OC, mayoría 2024, 296 organismos).
> **No es el universo completo** ni una conclusión: es una primera medición reproducible.
> Generado por `python -m mercadopublico.analisis_fragmentacion` (`data/processed/fragmentacion.csv`).

## H1 — Micro-fragmentación (¿todos compran lo mismo por separado?)

En la muestra, **291 productos** (código UNSPSC real) fueron comprados por **5 o más organismos
distintos**, cada uno con sus propias órdenes. Los rubros más fragmentados:

| Producto | Organismos | Órdenes | Líneas | Gasto (muestra) |
|---|--:|--:|--:|--:|
| Servicios de limpieza de edificios | 39 | 51 | 58 | $3.066 M |
| Exámenes médicos | 34 | 96 | 185 | $470 M |
| Servicios de vigilancia | 31 | 49 | 67 | $1.160 M |
| Verduras frescas | 24 | 52 | 522 | $176 M |
| Sondas quirúrgicas | 23 | 43 | 85 | $33 M |
| Computadores de escritorio | 22 | 29 | 41 | $884 M |
| Reactivos de analizadores químicos | 21 | 55 | 302 | $322 M |
| Fruta fresca | 21 | 33 | 295 | $127 M |

**Lectura preliminar:** hay evidencia de que commodities (alimentos, aseo, insumos médicos) se
compran de forma atomizada entre muchos organismos. Es consistente con H1, **pero falta el paso
crítico del §2:** descontar lo que **ya está consolidado vía Convenio Marco** antes de afirmar
que la fragmentación es evitable. La muestra incluye CM; el próximo paso es separar "fragmentación
evitable" de "compra estándar vía convenio".

**Caveats:** muestra parcial (no todo 2024); un mismo rubro UNSPSC agrupa variedades distintas
(D11/D15); no todo lo fragmentado es consolidable (urgencias, perecibles locales).

## H3 (parcial) — Tipo de proceso vs. monto

Monto de línea (precio × cantidad) por tipo de orden de compra:

| Tipo | Líneas | Mediana | p90 |
|---|--:|--:|--:|
| SE — Sin emisión automática | 11.824 | $246.966 | $4.252.500 |
| AG — Compra Ágil | 3.546 | $116.540 | $1.125.000 |
| CM — Convenio Marco | 3.159 | $151.020 | $2.058.400 |
| CC — Compra Coordinada | 182 | $469.790 | $12.600.000 |

**Lectura preliminar:** **Compra Ágil (AG)** —el mecanismo liviano para montos bajos— efectivamente
tiene la **mediana más baja**, lo que sugiere que se usa para lo que corresponde. Compra Coordinada
(CC), pensada para agregación, muestra los montos más altos (coherente).

**Límite importante:** H3 real (§2) es "¿se usa **licitación completa** para montos triviales?".
Eso vive en la **API de Licitaciones** (tipos L1/LE/LP…), **no** en las órdenes de compra. Con la
data de OC solo vemos el mecanismo de la *orden*, no el peso del *proceso* previo. Para H3 completo
hay que cruzar con licitaciones (Fase 2/3). Y recordar: **Compra Ágil no está en OCDS** pero sí en
la API (§8 del maestro), así que un análisis basado solo en descargas OCDS **sobreestimaría** H3.

## Próximos pasos sugeridos
1. Restar Convenio Marco al medir fragmentación evitable (H1 depurado).
2. Traer licitaciones (API/OCDS) para el cruce tipo-de-proceso × monto real (H3).
3. Segmentar precio por cantidad (D15) para no confundir descuento por volumen con sobreprecio.
