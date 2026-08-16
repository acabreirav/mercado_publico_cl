# Consideraciones futuras — cosas para no perder de vista

> Backlog de **observaciones metodológicas y de análisis** que hay que tener presentes a medida
> que llega más data. No son bugs ni contradicciones de fuentes (eso está en
> `discrepancias-fuentes.md`); son **advertencias y decisiones pendientes** que afectan la
> validez de las conclusiones. Cada una dice **por qué importa** y **qué hacer cuando toque**.

---

## ⭐ 1. Estacionalidad (¡ojo cuando haya data de varios meses!)

**La observación (del usuario):** frutas, verduras y otros perecibles varían de precio de forma
**legítima por temporada y por día**. Un tomate en enero no vale lo mismo que en junio. Comparar
precios de un mismo producto en fechas distintas y llamar "sobreprecio" a la diferencia sería un
error grave.

**Por qué no lo vemos aún:** la muestra actual es de ~4 días → no hay spread temporal para medir
estacionalidad. Al forzar "mismo mes" el número colapsa, pero **es artefacto de muestra corta, no
evidencia** (ver `metodologia-y-limites.md` §3.3).

**Qué hacer cuando haya historia (meses/años):**
- Comparar perecibles **dentro de producto + región + mes** (ya soportado:
  `comparador_identicos.py --control region,mes`).
- Considerar desestacionalizar (comparar contra el precio típico de ESE mes) o usar índices.
- **Liderar la narrativa pública con productos ESTABLES** (útiles, aseo, aceite, IT, packaged),
  donde tiempo/lugar no confunden; perecibles siempre con el sello "controlado por temporada".

## 2. Geografía / transporte

- Regiones extremas (Magallanes, Aysén) pueden pagar legítimamente más por transporte.
- **Buena noticia:** en perecibles, el **ID de catálogo ya trae la región** ("KILO APROX. RM"),
  así que la geografía está en gran parte controlada. Controlar por región casi no movió el número.
- Igual, para productos sin región en el ID, comparar **dentro de la misma región** (soportado).

## 3. Unidad de medida (el problema base)

- La API de OC **no informa la unidad** (D11) → dos compras del mismo código pueden estar en
  unidades distintas. Es el mayor riesgo del comparador por UNSPSC.
- **Mitigación actual:** agrupar por **ID de catálogo** (mismo ID = misma presentación).
- **A verificar con OCDS:** el estándar OCDS **sí tiene campo `unit`** en los ítems → las descargas
  masivas podrían resolver esto. Confirmar al parsear un archivo real.

## 4. Descuento por volumen

- Precio unitario bajo se correlaciona con cantidades grandes (D15) → comprar al por mayor es
  eficiente, no sobreprecio.
- **Mitigación:** comparar dentro de bandas de cantidad; el estimador de ahorro ya lo hace.

## 5. Normalización de productos (el gran desbloqueo pendiente)

- UNSPSC es demasiado grueso (mezcla PC básico con workstation) → un "ahorro" del 51% a ese nivel
  es artefacto de heterogeneidad.
- **Avance logrado:** el **ID de catálogo** en la especificación normaliza el ~17% de los ítems.
- **Pendiente (Fase 4):** matching por descripción (fuzzy/embeddings) para el 83% restante, y traer
  el catálogo de Convenio Marco completo desde su fuente (el OC de CM no trae ni UNSPSC, D13).

## 6. Convenio Marco como consolidación existente

- Al medir fragmentación (H1) hay que **descontar lo que ya se consolida vía Convenio Marco** antes
  de decir "esto debería consolidarse". Pendiente en `analisis_fragmentacion.py`.

## 7. El ahorro se reporta como RANGO, nunca como número único

- Siempre `[conservador (→mediana), aspiracional (→p25)]`, con el supuesto explícito y etiqueta
  "potencial estimado, no garantizado". Ver `metodologia-y-limites.md` §5.

## 8. Clasificador perecible/estable es heurístico

- Hoy marca por palabras ("fresc"/"aprox") → no captó "SANDÍA/MELÓN UNIDAD". Perfeccionar (lista de
  rubros perecibles, o categoría UNSPSC de alimentos frescos).

## 9. Cobertura / sesgos a declarar siempre en el dashboard

- Empresas públicas excluidas; muestra parcial; Compra Ágil no está en OCDS (sí en API);
  rango temporal mezclado (D14). Toda cifra es "del universo Mercado Público", no "todo el gasto".

---

### Prioridad sugerida cuando llegue data histórica (OCDS)
1. Rehacer el comparador de idénticos con **meses reales** → medir estacionalidad de verdad (#1).
2. Verificar si OCDS trae **unidad de medida** (#3) → resolvería el problema base.
3. Descontar Convenio Marco en fragmentación (#6).
4. Ampliar normalización más allá del ID de catálogo (#5).
