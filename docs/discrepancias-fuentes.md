# Discrepancias entre fuentes — para revisar

> Registro de **contradicciones y dudas** detectadas al consolidar la documentación oficial de
> Mercado Público (ver `docs/fuentes/`). No bloquean el trabajo: para cada una hay un criterio
> provisional ("Qué usamos"), pero conviene **verificarlas contra la API real** antes de publicar
> conclusiones. Marcar ✅ cuando se resuelva.
>
> Fuentes citadas:
> - **PDF-OC** = `fuentes/diccionario-datos-ordenes-de-compra.pdf`
> - **PDF-LIC** = `fuentes/diccionario-datos-licitaciones.pdf`
> - **PDF-CA** = `fuentes/guia-api-compra-agil-v3.0.pdf`
> - **WEB** = `fuentes/api-mercadopublico-web-copia.md` (copia de la web, pegada por el usuario)
> - **HANDOFF** = `fuentes/contexto-original-handoff.md` (contexto original del proyecto)
> - **REAL** = respuesta real observada de la API (muestras en `data/raw/`)

---

## D1 — Forma de pago (OC): códigos 48 y 49
- **WEB:** incluye `48 = A 45 días` y `49 = A más de 30 días`.
- **PDF-OC:** la tabla de Forma de Pago solo llega hasta `47` (1, 2, 39, 46, 47).
- **Qué usamos:** tabla del PDF-OC como base; 48/49 quedan anotados como "solo en WEB".
- **Estado:** ⬜ Pendiente. **Verificar:** ¿aparecen 48/49 en OC reales? Puede ser que el PDF
  esté truncado o que WEB traiga códigos adicionales válidos.

## D2 — Modalidad de pago (Licitación): orden de los valores
- **PDF-LIC (3.4):** `5 = Pago Bimensual`, `10 = Pago a 60 días` (entre otros).
- **WEB:** ordena distinto; p. ej. asocia `5` a "Pago a 60 días".
- **Qué usamos:** **PDF-LIC** (autoritativo). Ver §9.10 del maestro.
- **Estado:** ⬜ Pendiente. **Verificar:** cruzar contra una licitación real con modalidad conocida.

## D3 — Tipo de acto administrativo que adjudica (Licitación): 3 y 5
- **PDF-LIC (3.7):** `3 = Acuerdo`, `5 = Otros`.
- **WEB:** `3 = Otros`, `5 = Acuerdo` (invertido).
- **Qué usamos:** **PDF-LIC**. Ver §9.11 del maestro.
- **Estado:** ⬜ Pendiente. **Verificar:** revisar una licitación adjudicada con acto conocido.

## D4 — Tipo de licitación: definición de LP y bandas nuevas (LQ, LR)
- **PDF-LIC (3.1):** `LP = ≥1.000 y <2.000 UTM`, y agrega `LQ = 2.000–5.000`, `LR = ≥5.000`.
  También bandas privadas nuevas (`B2`, `H2`, `I2`).
- **WEB / HANDOFF:** `LP = > 1.000 UTM` (sin LQ/LR) y una lista larga de tipologías antiguas
  (A1, B1, J1, F1, E1, D1, C2, C1, F2, F3, G2, G1, R1, CA, SE…) marcadas como "ya no existen".
- **Qué usamos:** **PDF-LIC** para lo vigente; las tipologías antiguas se mapean como *legacy*
  si aparecen en data histórica. Ver §9.5 del maestro.
- **Estado:** ⬜ Pendiente. **Verificar:** confirmar bandas UTM vigentes en normativa actual y qué
  tipos aparecen realmente en el histórico OCDS.

## D5 — Endpoint de detalle de OC: ruta singular vs plural
- **PDF-OC:** documenta `.../publico/OrdenCompra.json?codigo=...` (singular).
- **REAL / HANDOFF:** `.../publico/ordenesdecompra.json?codigo=...` (plural) **funciona** y
  devuelve el detalle completo (verificado con `1001546-22-AG24`).
- **Qué usamos:** ruta **plural** `ordenesdecompra.json?codigo=` (probada).
- **Estado:** ⬜ Pendiente. **Verificar:** si ambas rutas existen y si devuelven el mismo shape.

## D6 — `PrecioNeto` es precio unitario (no dividir)
- **PDF-OC (campo 70):** `PrecioNeto` = *"Precio neto **o precio unitario** del producto"*.
- **Error previo nuestro:** en un mensaje se dijo "precio unitario = PrecioNeto / Cantidad".
- **Qué usamos:** `PrecioNeto` **ya es** el unitario; total de línea ≈ `PrecioNeto × Cantidad`.
- **Estado:** ✅ Resuelto (corregido en el maestro §6 y §10). Igual conviene confirmar con una OC
  de cantidad > 1 y precio unitario conocido.

## D7 — Campo `Total` del ítem viene en 0.0 (dato sucio)
- **PDF-OC (campo 74):** `Total` = "Total final de precios de los productos".
- **REAL:** en la muestra `1001546-22-AG24`, el ítem trae `PrecioNeto = 1.285.125` pero
  `Total = 0.0` (mientras el `TotalNeto` de la OC sí es correcto).
- **Qué usamos:** **no confiar** en `Total` del ítem; derivar `PrecioNeto × Cantidad` y marcar
  outliers.
- **Estado:** ⬜ Pendiente. **Verificar:** ¿es sistemático en OC tipo AG o solo en esta? Medir
  el % de ítems con `Total = 0` en un día completo.

## D8 — Compra Ágil: ¿ausente o accesible?
- **HANDOFF (§6):** "Compra Ágil no se publica en la API OCDS" → implicaba que sesga H3 por ausencia.
- **PDF-CA + REAL:** Compra Ágil **sí** es accesible: como OC tipo `AG` en la API de OC, y por la
  **API v2 dedicada** (`api2.mercadopublico.cl`).
- **Qué usamos:** Compra Ágil es capturable por API; el sesgo de OCDS aplica **solo** si te limitas
  a descargas masivas. Ver §3, §8, §11 del maestro.
- **Estado:** ✅ Aclarado (documentado en el maestro). Queda **verificar** la cobertura real de
  `AG` en la API de OC vs. la API v2 (¿todas las Compras Ágiles emiten OC tipo AG?).

## D9 — Nomenclaturas de estado de OC con posibles typos
- **WEB:** para el filtro `estado=`, lista `recepcionaceptadacialmente` (estado 14) y
  `recepecionconformeincompleta` (estado 15) — se ven como **errores de tipeo** de la fuente.
- **Qué usamos:** los valchados tal cual figuran, pero **con sospecha**.
- **Estado:** ⬜ Pendiente. **Verificar:** probar los strings exactos contra la API; si fallan,
  descubrir la nomenclatura correcta.

## D10 — Unidad monetaria: orden de UTM/EUR entre docs
- **PDF vs WEB:** listan CLP/CLF/USD/UTM/EUR en orden ligeramente distinto (trivial).
- **Qué usamos:** el conjunto de valores es el mismo; el orden no importa. Ver §9.7.
- **Estado:** ✅ Sin impacto (solo cosmético).

---

### Resumen de verificaciones pendientes (checklist)
- [ ] D1 — ¿existen forma de pago 48/49 en OC reales?
- [ ] D2 — modalidad de pago 5 y 10 contra licitación real
- [ ] D3 — acto administrativo 3/5 contra licitación adjudicada real
- [ ] D4 — bandas UTM vigentes de tipos de licitación + legacy en histórico
- [ ] D5 — endpoint singular vs plural de detalle de OC
- [ ] D7 — % de ítems con `Total = 0` en un día completo
- [ ] D9 — strings exactos de `estado=` para OC (posibles typos)
