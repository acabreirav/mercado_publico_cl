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

## D11 — `Unidad` del ítem viene SIEMPRE vacía (API de OC)
- **PDF-OC:** no lista un campo "Unidad" de ítem como obligatorio, pero la respuesta real trae la
  clave `Unidad`.
- **REAL:** en un día completo (04-03-2024, 1.067 ítems), **el 100% tiene `Unidad` vacía/null**.
- **Impacto:** no se puede normalizar la **unidad de medida** desde este campo → un mismo
  `CodigoProducto` puede mezclar "unidad" vs "caja" vs "kg", inflando los ratios del comparador.
  Por eso el comparador marca `revisar=1` cuando el ratio es implausible.
- **Qué usamos:** tratar la unidad como **desconocida**; apoyarse en `EspecificacionComprador`
  (texto) y en el drill-down. Evaluar si la unidad viene en la API de Licitaciones (`UnidadMedida`,
  campo 92) o en Compra Ágil (`unidad_medida`), que sí la documentan.
- **Estado:** ⬜ Pendiente. **Verificar:** ¿`UnidadMedida` viene poblada en licitaciones/Compra Ágil?

## D12 — `CodigoProducto = 0` en ~12% de los ítems de OC
- **REAL:** en el día 04-03-2024, **125/1.067 ítems (12%)** traen `CodigoProducto` vacío o `0`
  (sin código UNSPSC). No corresponden a un producto identificable.
- **Impacto:** si se agrupan por código, todos los "0" caen en un mismo grupo falso → falsos
  sobreprecios gigantes (ej. un "producto" con ratio 89.312x que mezclaba jamón, servicios, etc.).
- **Qué usamos:** el comparador **excluye** `CodigoProducto` vacío/`0`. Ver `comparador.py`.
- **Estado:** ✅ Resuelto en código. **Verificar:** ¿qué tipos de OC concentran el código 0?
  (posiblemente servicios/trato directo sin catálogo).

## D13 — Convenio Marco NO trae `CodigoProducto` en la API de OC (98% en 0)
- **HANDOFF (§5):** proponía empezar el comparador por **Convenio Marco** porque "trae ID de
  catálogo estándar → comparación directa y confiable".
- **REAL:** en ~3.159 ítems CM de la muestra, **el 98% trae `CodigoProducto` vacío/`0`**. El ID
  del catálogo de Convenio Marco NO viaja en el campo `CodigoProducto` de la OC (vive en el
  catálogo CM / otra fuente).
- **Impacto:** vía la **API de OC**, CM es un **callejón sin salida** para agrupar por producto
  (solo 2 productos CM comparables en toda la muestra). El camino que sí funciona es agrupar por
  `CodigoProducto` UNSPSC del universo general (SE/AG traen código con más frecuencia).
- **Qué usamos:** comparador general por UNSPSC. CM queda pendiente de otra fuente (catálogo CM
  u OCDS) si se quiere su ID limpio.
- **Estado:** ⬜ Estratégico. **Verificar:** ¿de dónde se obtiene el ID de producto de Convenio
  Marco? (catálogo CM, descargas OCDS). Reevaluar la estrategia del §5 del maestro.

## D14 — El listado "por día" incluye OC creadas en otras fechas (rango 2019–2024)
- **REAL:** al bajar `fecha=04-08 marzo 2024`, los detalles traen `FechaCreacion` desde 2019 a
  2024 (aunque el 88% es 2024). La `fecha` de consulta NO equivale a fecha de creación de la OC.
- **Impacto:** comparar precios entre años mezcla **inflación**. Menor de lo temido (88% es 2024),
  pero para rigor conviene filtrar por año o normalizar a UF/UTM.
- **Qué usamos:** por ahora, sin filtro (dominado por 2024). Documentar el caveat en el dashboard.
- **Estado:** ⬜ Pendiente. **Verificar:** qué significa exactamente el parámetro `fecha` en la
  API de OC (¿fecha de envío? ¿de última modificación?).

## D15 — Precio unitario bajo se correlaciona con cantidades grandes (descuento por volumen)
- **REAL:** en el drill-down de "Artículos de papelería", los precios unitarios más bajos vienen
  con cantidades enormes ($26/unidad por 1.000 unidades; $120 por 7.500) y los altos con
  cantidades chicas. Parte de la dispersión de precio es **descuento por volumen**, no sobreprecio.
- **Impacto:** al medir "sobreprecio" hay que considerar la **cantidad**. Comparar precios a
  volúmenes parecidos, o modelar precio vs. cantidad (curva de descuento) antes de acusar.
- **Qué usamos:** por ahora se muestra la cantidad en el drill-down y se enmarca como "señal para
  investigar". Pendiente: normalizar/segmentar por rango de cantidad en el comparador.
- **Estado:** ⬜ Pendiente (mejora de Fase 1/2). Suma al caveat de unidad (D11).

## D16 — El límite que MUERDE es la ráfaga (429), no el tope diario de 10.000
- **REAL:** al bajar detalles seguidos, la API devuelve `HTTP 429` con altísima frecuencia y una
  espera efectiva de ~6-7 s por request (1.500 detalles tardaron ~2h50m). El tope de 10.000/día
  casi nunca se alcanza en un día de muestreo; el cuello de botella es un **límite de ráfaga**
  (por ventana corta) no documentado en números.
- **Qué usamos:** ritmo **adaptativo AIMD** en `download_lote_detalles` (sube la pausa ante 429,
  baja si va limpio) + honrar `Retry-After` + contador de cuota diaria persistente (`quota.py`).
  La concurrencia NO ayuda (el límite es del servidor) → para volumen real, usar **descargas
  masivas OCDS** (ver §3.3 del maestro), no la API detalle-a-detalle.
- **Estado:** ⬜ Mitigado en código. **Verificar:** medir el ritmo sostenible real que encuentra
  el AIMD en una corrida nocturna; confirmar si hay un header/documento con el límite exacto.

---

### Resumen de verificaciones pendientes (checklist)
- [ ] D1 — ¿existen forma de pago 48/49 en OC reales?
- [ ] D2 — modalidad de pago 5 y 10 contra licitación real
- [ ] D3 — acto administrativo 3/5 contra licitación adjudicada real
- [ ] D4 — bandas UTM vigentes de tipos de licitación + legacy en histórico
- [ ] D5 — endpoint singular vs plural de detalle de OC
- [ ] D7 — % de ítems con `Total = 0` en un día completo
- [ ] D9 — strings exactos de `estado=` para OC (posibles typos)
- [ ] D11 — ¿`UnidadMedida` viene poblada en Licitaciones / Compra Ágil?
- [ ] D12 — ¿qué tipos de OC concentran `CodigoProducto = 0`?
- [ ] D15 — normalizar/segmentar precio por cantidad (descuento por volumen)
- [ ] D16 — medir el ritmo sostenible del AIMD; buscar el límite de ráfaga exacto
