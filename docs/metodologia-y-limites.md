# Metodología y límites del análisis

> Este archivo explica **cómo comparamos precios y estimamos ahorros**, y —sobre todo— **qué NO
> podemos afirmar** con la data disponible. Es distinto de `discrepancias-fuentes.md` (que registra
> contradicciones entre fuentes): aquí van las **limitaciones metodológicas** que condicionan toda
> conclusión. Regla del proyecto: cada afirmación fuerte viene con el dato que la sostiene y el que
> la matiza.

---

## 1. La comparación de precios: qué significa y qué no

**Qué hacemos:** agrupamos ítems por `CodigoProducto` (UNSPSC) y comparamos el `PrecioNeto`
(precio unitario) que pagó cada organismo.

**El problema central — la unidad de medida.** La API de órdenes de compra **no informa la unidad
de medida** (`Unidad` viene vacía en el 100% de los ítems, ver D11). Consecuencia: dos compras del
mismo `CodigoProducto` pueden estar en **unidades distintas** — "por unidad" vs "por caja de 100" vs
"por kilo" — y eso se ve como una diferencia de precio gigante que **no es sobreprecio**.

Ejemplo real (papelería, UNSPSC 14111509): un organismo aparece pagando $26 y otro $719.551 por el
"mismo" producto. Casi seguro no es un sobreprecio de 27.000×, sino unidades/presentaciones distintas.

**Cómo lo mitigamos:**
- Excluimos ítems sin código UNSPSC (`CodigoProducto` 0/vacío, ~12%).
- Usamos **dispersión robusta (p75/p25)**, no máx/mín, para los titulares.
- Excluimos productos con dispersión implausible.
- **Nunca** presentamos el máx/mín como "sobreprecio"; lo llamamos **rango** y **señal para investigar**.

**Lo que NO podemos afirmar:** que una diferencia de precio sea sobreprecio, sin abrir el detalle y
verificar que se trata del mismo bien en la misma presentación. El comparador **señala dónde mirar**,
no dictamina culpables.

## 2. El descuento por volumen (compra al por mayor)

En la data, los precios unitarios más bajos se correlacionan con **cantidades grandes** (D15): quien
compra 1.000 unidades paga menos por unidad que quien compra 10. **Esto es esperable y correcto** —
comprar al por mayor es eficiente. Pero significa que **parte de la dispersión de precio es descuento
legítimo por volumen**, no ineficiencia.

**Implicancia para cualquier estimación de ahorro:** comparar el precio de una compra chica contra
el de una compra al por mayor y llamar "ahorro" a la diferencia es **incorrecto**. Hay que comparar
**dentro de rangos de cantidad parecidos**.

## 3. Cómo estimamos el ahorro potencial (método propuesto)

Objetivo: estimar cuánto podría ahorrar el Estado si las compras de un mismo producto se alinearan
a un precio de referencia razonable (idea del usuario: "cómo eficientar el Estado", agregando a nivel
nacional/regional).

**Método (control por volumen + benchmark conservador):**
1. Agrupar por `CodigoProducto` (UNSPSC) y **banda de cantidad** (por orden de magnitud: 1-9, 10-99,
   100-999, …). Así se compara "compra chica con compra chica" y "mayoreo con mayoreo".
2. Dentro de cada (producto, banda) con evidencia suficiente (≥3 compras, ≥2 organismos), fijar un
   **precio de referencia**:
   - **Conservador** = la **mediana** de la banda (piso creíble del ahorro).
   - **Aspiracional** = el **percentil 25** de la banda (si todos alcanzaran al cuartil eficiente).
3. Ahorro de una compra = `max(0, precio_pagado − referencia) × cantidad`. Solo cuenta lo que está
   **por encima** de la referencia (no penaliza a quien ya compra barato).
4. Sumar y reportar como **rango [conservador, aspiracional]**, nunca un número único.
5. Reportar solo sobre productos de **confiabilidad alta/media** (varios organismos y compras).

**Qué es y qué no es este número:**
- **Es:** una estimación de la dispersión de precio *dentro de cantidades comparables*, expresada
  en pesos, como orden de magnitud de la oportunidad.
- **No es:** una promesa de ahorro real (habría costos de coordinación, logística, contratos), ni
  una acusación de sobreprecio (puede haber calidad/urgencia/especificación distinta).
- **Etiqueta obligatoria en el dashboard:** "ahorro *potencial estimado* bajo el supuesto de alinear
  precios a volumen comparable — no es ahorro garantizado".

### 3.1 Resultado del primer prototipo (IMPORTANTE — leer)

Corrimos el estimador sobre la muestra (`estimar_ahorro.py`). Resultado:

| Universo | Gasto comparado | Ahorro conservador | % |
|---|--:|--:|--:|
| Todo (incluye servicios) | $22.584 M | $15.309 M | **67,8 %** |
| Solo bienes (UNSPSC < 70) | $7.259 M | $3.699 M | **51,0 %** |

**Un 51–68 % de "ahorro" NO es creíble — es una alarma, no un hallazgo.** ¿Qué nos dice? Que a
nivel de **código UNSPSC el producto es demasiado heterogéneo**: un mismo código mezcla un PC básico
con una workstation, un reactivo con otro, etc. El número mide **heterogeneidad de producto**, no
ineficiencia del Estado. Los servicios (construcción, limpieza, personal) lo inflan aún más porque
no tienen "unidad" comparable.

**Conclusión metodológica:** la estimación de ahorro **no es defendible al nivel de UNSPSC**. Para
que el número valga, hace falta **igualar productos verdaderamente idénticos** (misma especificación
y unidad) — es el "problema difícil de normalización de productos" (§5 del maestro). Caminos:
1. **Convenio Marco / catálogo estándar**: ítems con ID de catálogo real (no el UNSPSC) → comparación
   limpia. Requiere otra fuente (el OC de CM no trae ni UNSPSC, ver D13).
2. **Curar a mano** un puñado de productos genuinamente homogéneos (ej. una resma específica) y
   estimar ahorro solo ahí, con drill-down. Creíble y demostrable.
3. **Matching por descripción** (texto → fuzzy/embeddings) para afinar dentro de un UNSPSC. Fase 4.

**Qué haremos:** el estimador queda como herramienta, pero el número agregado **no se publica** como
"ahorro del Estado" hasta tener normalización fina. Sí se puede mostrar en productos curados.

### 3.2 El desbloqueo — agrupar por ID de catálogo (producto IDÉNTICO)

La especificación de muchos ítems trae un **ID de catálogo de Convenio Marco** entre paréntesis
(ej. `(1573012) ARROZ TUCAPEL GRADO 1 BOLSA 1K`). **Mismo ID = producto y presentación idénticos.**
Está en ~17% de los ítems, pero da **normalización real** donde el UNSPSC no alcanzaba. Implementado
en `comparador_identicos.py` (extracción del ID en `parse_items.extraer_catalogo_id`).

Agrupando por ID de catálogo, excluyendo grupos con dispersión implausible (> 3×, que son contratos
marco variables como combustible/alimentación, no productos unitarios), el ahorro estimado cae a un
nivel **creíble**:

| Método de agrupación | Gasto comparado | Ahorro conservador | Veredicto |
|---|--:|--:|:--|
| UNSPSC (grueso) | $7.259 M | 51 % | ❌ artefacto de heterogeneidad |
| **ID de catálogo (idéntico), disp. ≤ 3×** | $260 M | **3,1 %** (6 % aspiracional) | ✅ **defendible** |

Ejemplos de la muestra (mismo ID, unidad clara, dispersión real y modesta): papa fresca, pechuga de
pollo congelado, huevo primera, plátano/kilo, aceite 1 L, quesillo 300 g, zanahoria/kilo — con
diferencias de precio de 1,1× a 2,2× entre organismos.

**Lectura:** aun comprando el **mismo producto por el mismo catálogo**, hay una dispersión de precio
real de ~3–6 %. Eso sí es un ahorro potencial creíble y publicable (con drill-down). Escala a medida
que (a) baje más data y (b) extendamos la normalización más allá del ID de catálogo (Fase 4).

### 3.3 Homogeneizar tiempo y lugar (perecibles)

Riesgo válido: frutas/verduras/frescos varían de precio **por temporada, por día y por región**
(transporte). Comparar sin controlar eso confundiría variación legítima con sobreprecio.

Qué encontramos y cómo lo tratamos (`comparador_identicos.py --control region,mes`):

| Nivel de control | Grupos | Gasto comp. | Ahorro cons. | % |
|---|--:|--:|--:|--:|
| Mismo producto (ID catálogo) | 74 | $260 M | $8,2 M | 3,1 % |
| + misma región | 63 | $216 M | $7,9 M | 3,7 % |
| + mismo mes | 27 | $63 M | $0,3 M | 0,5 % |

- **Región casi no mueve el número** porque el ID de catálogo de frutas/verduras **ya trae la
  región** ("KILO APROX. RM", "XI REGIÓN") → la geografía ya está en gran parte controlada.
- **El control por mes hace caer el número a 0,5%, pero es un ARTEFACTO de muestra corta** (4 días
  no tienen meses distintos → quedan 27 grupos diminutos). **No es evidencia de que el ahorro
  desaparezca al controlar temporada**; es evidencia de que **falta cobertura temporal**.

**Decisiones metodológicas:**
1. **Liderar la narrativa pública con productos ESTABLES** (útiles, aseo, aceite, IT, packaged),
   donde tiempo/lugar no confunden. Es la señal más limpia de ineficiencia.
2. **Perecibles: comparar dentro de producto + región + mes**, y solo con **data histórica**
   (meses). Marcados con `perecible` en la salida (heurística por descripción — perfeccionable).
3. **Esto es otro argumento fuerte para las descargas OCDS históricas** (cobertura temporal).

## 4. Límites de cobertura (recordatorio)

- **Muestra parcial**, no todo el gasto del Estado; empresas públicas excluidas.
- **Rango temporal 2019–2024** (mayoría 2024); para rigor, filtrar por año o normalizar a UF/UTM.
- **Convenio Marco** ya es un mecanismo de consolidación: al hablar de "ahorro por consolidar",
  descontar lo que ya pasa por CM (pendiente).
- **Compra Ágil** está en la API pero **no en OCDS**; un análisis solo-OCDS sesga H3.

## 5. Estándar de presentación (para no engañar)

1. Todo agregado (ahorro, dispersión) es **abrible** hasta las órdenes de compra que lo componen.
2. Los números de ahorro van **como rango**, con el supuesto explícito.
3. Los extremos (máx/mín) se muestran como contexto, nunca como el titular.
4. Cada vista lleva su nota de cobertura y de unidad de medida.
