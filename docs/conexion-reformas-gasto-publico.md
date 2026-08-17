# Conexión con las reformas al gasto público (informe 2025) — Propuestas 4 y 7

> La **Comisión Asesora para Reformas Estructurales al Gasto Público** (informe final 2025, DIPRES)
> incluye dos propuestas que tocan directo lo que analiza este proyecto. Aquí registramos la
> conexión, y —lo más importante— cómo nuestra data **valida** y **puede dar seguimiento** a estas
> reformas. (El usuario aportó el texto de las propuestas; ver fuente al final.)

---

## Propuesta 4 — Eficiencia hospitalaria y del sistema público de salud

**Qué propone (resumen):** una agenda **obligatoria** de eficiencia hospitalaria: **Compra
Coordinada obligatoria con metas mínimas por hospital**, paquetización quirúrgica, trazabilidad de
insumos, logística profesionalizada (centros de almacenamiento regionales), y **revisar las
comisiones de CENABAST y su coordinación con ChileCompra**. Con un **sistema de seguimiento
centralizado obligatorio**.

**Datos que cita (CNEP):**
- 75% del gasto en fármacos y dispositivos médicos (F+DM) se concentra en 17% de los hospitales.
- En 2022, **solo 5% del gasto F+DM** pasó por Compra Coordinada; el mecanismo ha mostrado
  reducciones **de hasta 59%** en algunos insumos.
- Altísima **fragmentación logística**: 61% de hospitales con sistemas propios de inventario, 13%
  con Excel, 4% sin sistema; 40% del inventario en bodegas periféricas sin registro; 1,28% de
  pérdida de medicamentos; mantenimiento 0,14% del presupuesto vs 6% estándar internacional.
- **Ahorro estimado total ~USD$101 MM/año.**

### 🎯 Cómo conecta con NUESTRO análisis
1. **Es, literalmente, nuestra hipótesis H1 (fragmentación) aplicada a salud.** En nuestra data, el
   **sector salud es el más fragmentado** (decenas de hospitales comprando lo mismo por separado).
   La propuesta lo confirma con cifras oficiales.
2. **Coincide con nuestro hallazgo de que en Convenio Marco la ineficiencia es de PROCESO, no de
   precio.** El "solo 5% vía Compra Coordinada" es exactamente el problema de **demanda no
   agregada** que medimos (cientos de compras separadas del mismo ítem).
3. **El "sistema de seguimiento centralizado obligatorio" que pide la propuesta es, en esencia, lo
   que este proyecto prototipa:** detectar productos idénticos, medir dispersión y fragmentación,
   con drill-down auditable. Nuestro pipeline podría **monitorear la adopción de Compra Coordinada,
   la fragmentación por hospital y la dispersión de precios en salud**.

### ✅ Validación cruzada de nuestra cifra de ahorro (importante)
El informe estima el ahorro por **compras coordinadas** en **1,5%–2,5%** (promedio) sobre ~USD$1.600
MM de F+DM. **Nuestro análisis independiente** de productos idénticos de Convenio Marco arrojó
**~1,7% (con control por región y mes) a ~4,8% (aspiracional)**. → **Coinciden en orden de
magnitud.** El "hasta 59%" del informe es el **mejor caso puntual** en insumos específicos, **no el
promedio** — igual que nosotros vimos productos con dispersión de 2–3× junto a muchos casi
alineados. Que dos metodologías distintas (la nuestra, bottom-up desde OCDS; la de CNEP) lleguen al
mismo ~2% promedio es una **fuerte señal de que la estimación es correcta**, y desmiente los
titulares de "ahorros gigantes" en el promedio.

> Matiz honesto: nuestro universo (todo Convenio Marco) y el del informe (F+DM de salud) no son
> idénticos; la coincidencia es de **orden de magnitud**, no exacta. Con la data de salud podríamos
> replicar su cifra directamente.

## Propuesta 7 — Traspaso funcional de CENABAST a ChileCompra

**Qué propone:** traspasar funcionalmente **CENABAST** (central de abastecimiento de salud) a
**ChileCompra** para mejorar la eficiencia de la compra pública. Legal, mediano plazo, **sin
cuantificación disponible** en el informe.

### 🎯 Cómo conecta
- Nuestra guía experta ya identificaba a **CENABAST como la central de compras sectorial de salud**,
  separada de ChileCompra. Esta propuesta apunta a **unificar** esa gobernanza.
- Como **salud es el sector más fragmentado** en nuestra data, una gobernanza unificada de compras
  de salud es coherente con lo que muestran los números.
- **Oportunidad de análisis:** con data de salud podríamos estimar la **duplicidad/coordinación**
  entre lo que hoy pasa por CENABAST vs. por Mercado Público, insumo directo para evaluar el traspaso.

---

## Qué implica para el proyecto (reencuadre de valor)

Estas propuestas **suben la apuesta** de lo que estamos haciendo: pasamos de "hay dispersión de
precios" a **"herramienta de evidencia y monitoreo para reformas concretas que el Estado ya está
impulsando"**. Líneas de trabajo que quedan habilitadas:

1. **Medir la fragmentación en salud** (H1) por hospital / servicio de salud, y el **% que pasa por
   Compra Coordinada** vs. compra separada → seguimiento directo de la Propuesta 4.
2. **Replicar la cifra de ahorro** de compras coordinadas con nuestra metodología sobre F+DM.
3. **Cuantificar CENABAST vs Mercado Público** (Propuesta 7) si conseguimos data de ambos.
4. Posicionar el pipeline como **prototipo del "sistema de seguimiento centralizado"** que la
   Propuesta 4 exige.

**Pendiente de data:** para esto conviene traer **más períodos (2025-2026)** y, si es posible,
**data de salud / CENABAST**. Ya está en curso la descarga de Convenio Marco 2025-2026.

---

## Fuente
- Comisión Asesora para Reformas Estructurales al Gasto Público — Informe Final (2025), DIPRES:
  <https://www.dipres.gob.cl/598/articles-383579_doc_pdf.pdf>
  (Propuesta 4: eficiencia hospitalaria; Propuesta 7: traspaso funcional de CENABAST a ChileCompra.)
