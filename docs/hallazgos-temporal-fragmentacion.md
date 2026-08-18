# Hallazgo — Fragmentación de Convenio Marco en el tiempo (2024 → 2026)

> Evaluación de impacto preliminar: ¿la fragmentación/dispersión en Convenio Marco se controló,
> amplificó o mantuvo del 2024 a hoy? Muestra OCDS de CM, enero-marzo de cada año.

## El error que evitamos
Los conteos crudos daban una caída fuerte (fragmentados 1.296 → 580 → 270), pero **las muestras por
año NO eran del mismo tamaño** (2024: 5.395 awards; 2025 y 2026: 2.400 c/u). Esa "caída" era un
**artefacto del tamaño de muestra**, no fragmentación real.

## Comparación justa (muestras parejas: 2.400 awards/año)

| Año | Fragmentados (3+ org) | Dispersión precio (mediana) | org/producto |
|---|--:|--:|--:|
| 2024 | 426 | 1,08× | 5,4 |
| 2025 | 580 | 1,04× | 4,6 |
| 2026 | 270 | 1,06× | 5,2 |

**Lectura honesta: no hay tendencia clara.** La fragmentación sube y baja sin patrón (2025 incluso
más alta que 2024); la **dispersión de precio se mantiene plana (~1,05×)**. → El efecto se ve
**MANTENIDO/estable**, no claramente controlado ni amplificado.

## Por qué NO podemos concluir "impacto de la reforma" (todavía)
1. **Muestra pequeña y ruidosa:** 2.400 awards/año es una fracción del universo; el año-a-año tiene
   mucho ruido. Para detectar un cambio real se necesita el **universo completo** (o muestras
   mucho mayores) por período.
2. **2026 es muy temprano:** las medidas del Presupuesto 2025 (ej. ≥80% de la canasta de
   medicamentos vía CENABAST) recién empiezan; su efecto no alcanzaría a verse aún.
3. **Segmento equivocado para la reforma:** la Propuesta 4 apunta a **salud (fármacos y dispositivos
   médicos)**, y **gran parte de eso pasa por CENABAST, no por Convenio Marco de Mercado Público**.
   Estamos mirando todo CM, no el segmento que la reforma toca. Para evaluar la reforma hay que
   **aislar salud / F+DM** y, si es posible, sumar data de CENABAST.
4. **En CM el precio ya está casi alineado (~1,05×):** hay poco margen para que una mejora de
   "coordinación de precio" se note aquí; la palanca real es de **proceso** (nº de compras
   separadas), que exige métricas más finas y universo completo.

## Qué se necesita para una evaluación de impacto seria
- Descargar el **universo completo** de CM (sin `--limit-detalle`) por período, o muestras grandes y
  parejas.
- **Aislar salud / F+DM** y, ojalá, incorporar **data de CENABAST**.
- Definir el "antes/después" respecto de la fecha de entrada en vigor de cada medida.
- Métricas de proceso (compras separadas por organismo/producto), no solo dispersión de precio.

**Conclusión:** con la data actual, la fragmentación de Convenio Marco luce **estable 2024→2026**,
pero es un resultado **sugerente, no concluyente** — la muestra es chica, 2026 es temprano y la
reforma apunta a un segmento (salud/CENABAST) que esta data no aísla. Es, en sí mismo, un hallazgo
honesto: **medir el impacto requiere mejor data, no más titulares.**
