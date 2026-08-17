# Investigación — Centralizar / dar "inteligencia" a las compras públicas

> Pregunta de política pública detrás del proyecto: ¿es factible una **capa que agregue
> solicitudes de compra**, busque el mejor proveedor y aproveche economías de escala? ¿Lo hace
> algún otro país? Este documento cruza **lo que muestra nuestra data** con **evidencia
> internacional**. Fuentes al final. Fecha: 2026-08.

---

## 1. Cómo funciona hoy la compra pública en Chile

El sistema es **muy descentralizado**: cada organismo compra por su cuenta a través de Mercado
Público (ChileCompra fija las reglas y la plataforma, pero **no compra por ellos**, salvo en los
mecanismos agregados del §2). Tipos de entidades compradoras (todas con presupuesto y autonomía
propios):

- **Gobierno central**: ministerios y servicios públicos.
- **Salud**: los Servicios de Salud y **cada hospital** — grandes compradores y **los más
  fragmentados** (en nuestra data, decenas de hospitales comprando el mismo insumo por separado).
- **Municipios** (345 comunas): muy autónomos, compran local.
- **Fuerzas Armadas y de Orden**, **universidades y CFT estatales**, poder judicial, etc.
- **Empresas públicas**: parcialmente **fuera** de la ley de compras.

**Lo que vimos en la data (este proyecto):** en 3 meses de Convenio Marco había **1.527 organismos
compradores distintos**; en la muestra de órdenes de compra, la salud domina la fragmentación. Es
decir, la demanda del Estado está **atomizada en cientos de compradores** que adquieren lo mismo
por separado.

## 2. Chile YA tiene mecanismos de centralización (parciales)

La idea del usuario **no parte de cero**: ChileCompra ya opera tres mecanismos de agregación, en
orden creciente de "centralización":

1. **Convenio Marco** — catálogo con precios pre-licitados; los organismos "compran en la tienda".
   Es agregación **de oferta** (un contrato marco para muchos), pero **cada organismo sigue
   eligiendo y pagando** → por eso vemos **dispersión de precio dentro del mismo ítem de catálogo**.
2. **Compra Coordinada / Compras Conjuntas** — **agregación de demanda**: 2+ organismos juntan su
   demanda en una sola licitación para mejores condiciones. Puede ser **por mandato** (la ejecuta
   la Dirección ChileCompra) o **conjunta** (los organismos con asesoría). Ej. real: **37
   organismos agregaron demanda para comprar computadores** (2021); en 2026 ChileCompra sigue
   invitando a procesos de Compra Coordinada.
3. **Compra Ágil** — mecanismo liviano para montos bajos (no centraliza, pero simplifica).

**La brecha:** la Compra Coordinada existe pero es **voluntaria, manual y caso-a-caso**. No hay una
**capa siempre-activa y basada en datos** que detecte automáticamente "50 hospitales van a comprar
lo mismo este mes → juntémoslos". **Eso** es lo que propone el usuario, y **es exactamente lo que
nuestro pipeline prototipa** (detectar productos idénticos comprados por muchos a precios distintos).

## 3. ¿Lo hace algún otro país? Sí — hay modelos maduros

**Organismos centrales de compra (Central Purchasing Bodies, CPB):**

| País | Plataforma / organismo | Qué hace de relevante |
|---|---|---|
| **Corea del Sur** | **KONEPS** (Public Procurement Service) | La **mayor plataforma de e-procurement del mundo**: ~US$130 mil millones/año, +60.000 instituciones. Ciclo completo (aviso→oferta→contrato→pago) y **tienda con demanda agregada**. Registro único del proveedor para participar en todo. |
| **Italia** | **Consip** (Ministerio de Economía) | Central de compras nacional; licitaciones agregadas y marketplace (MEPA). Para ciertas categorías, comprar por Consip es **obligatorio**. |
| **Francia** | **UGAP** | Central de compras; metas explícitas de **3% de ahorro** y **21% de contratos con PYMEs**. |
| **Reino Unido** | **Crown Commercial Service (CCS)** | Marcos y **"aggregation deals"**: junta demanda de todo el sector público (energía, vehículos, laptops). |
| **EE.UU.** | **GSA** | Schedules federales + marketplace (GSA Advantage) + compra cooperativa. |
| **Brasil** | **Sistema de Registro de Preços + "carona"** | Un acta de precios permite que **otros organismos se "suban" (carona)** a un precio ya licitado → agregación de demanda *legalmente* estructurada. |

**Tendencia de frontera:** Corea e Italia firmaron (2026) un MOU para **cooperar en procurement con
IA** — o sea, el mundo va justo hacia la "capa inteligente" que plantea el usuario. La idea está
**alineada con la dirección internacional**, no es exótica.

## 4. Factibilidad para Chile (honesta, con trade-offs)

**A favor (por qué es factible):**
- **La infraestructura ya existe**: plataforma (Mercado Público), datos (API + OCDS), y el
  mecanismo legal (Compra Coordinada, Convenio Marco). La "capa inteligente" es una **evolución
  incremental**, no un sistema nuevo.
- **La data lo permite**: podemos detectar productos idénticos, cuantificar dispersión y estimar
  ahorro (lo hicimos). Una capa así se alimentaría de exactamente estas señales.
- **Hay margen real** (ver §5): dispersión de precio medible en productos idénticos.

**En contra / cuidados (la evidencia OCDE es clara):**
- **⚠️ Riesgo PYME / competencia:** el mayor problema de sobre-centralizar es que **los contratos
  grandes dejan fuera a las PYMEs**. En Chile el **91% de los proveedores son micro y pequeñas
  empresas** → sería políticamente y económicamente costoso. Mitigación: **lotes**, cuotas
  regionales, permitir ofertas conjuntas (como hacen las CPB para equilibrar).
- **Logística y oportunidad:** un hospital necesita el insumo **cuando lo necesita**; agregar a
  nivel nacional puede empeorar tiempos de entrega. La agregación funciona mejor en
  **commodities estandarizables**, no en todo.
- **Estacionalidad y geografía:** parte de la dispersión es **legítima** (temporada, transporte a
  regiones extremas) — lo documentamos. Una capa inteligente debe **descontar** eso, no forzar un
  precio único.
- **Autonomía y presupuesto:** municipios y servicios tienen autonomía; obligar a centralizar
  choca con eso (por algo la Compra Coordinada es voluntaria).

## 5. Qué dice NUESTRA data (y cómo calza con el mundo)

- Sobre **productos idénticos de Convenio Marco** (mismo ID de catálogo, 3 meses, 1.527
  organismos), el ahorro potencial por **alinear precios al mediano** es **~2,7% conservador a
  nivel producto, y ~1,7% controlando por región y mes** (rango 1,7%–4,8%).
- Eso **coincide con el orden de magnitud internacional**: la francesa UGAP fija metas de **~3%**.
  No es el "50%" de los titulares — es un ahorro **modesto pero real y defendible**.
- **El prize más grande probablemente NO es el precio**, sino:
  1. **Reducir fragmentación** (H1): menos procesos separados = menos costo administrativo (cientos
     de compradores tramitando lo mismo).
  2. **Ampliar cobertura**: llevar a convenio/coordinación categorías que hoy se compran sueltas.
  3. **Estandarizar especificaciones**: gran parte de la "dispersión" viene de que cada organismo
     describe distinto — normalizar habilita comparar y agregar.

## 6. Conclusión / recomendación

**Es factible y es la dirección correcta**, con tres matices: (a) Chile ya tiene los ladrillos
(Convenio Marco + Compra Coordinada + datos), así que se trata de **darle inteligencia y
continuidad** a algo que hoy es manual y voluntario; (b) el ahorro por precio es **modesto (~2-4%)**
— vender la idea como "ahorro gigante" sería deshonesto; el caso fuerte está en **eficiencia de
proceso, estandarización y cobertura**; (c) el diseño debe **proteger a las PYMEs** (lotes,
regionalización) o repetirá el error que la OCDE advierte. Nuestro pipeline es, de hecho, un
**prototipo del "motor de detección"** que una capa así necesitaría: identifica productos idénticos,
mide dispersión, descuenta temporada/región y estima ahorro con drill-down auditable.

**Siguiente paso natural del análisis** (si se quiere sustentar esto con evidencia): medir el
**tamaño de la fragmentación** (cuántos organismos compran cada commodity por separado y cuánto
gastan) y simular el ahorro de agregarlos por categoría/región — pasando de "hay dispersión de
precio" a "esto es lo que rendiría coordinar la compra de X".

---

## Fuentes

- ChileCompra — Compras Coordinadas (agregación de demanda): <https://www.chilecompra.cl/comprascoordinadas/> y <https://www.chilecompra.cl/compras-conjuntas/>
- ChileCompra — 37 organismos agregan demanda para comprar computadores (2021): <https://www.chilecompra.cl/2021/04/37-organismos-publicos-agregan-demanda-para-la-compra-coordinada-de-computadores/>
- ChileCompra — Convenio Marco: <https://www.chilecompra.cl/convenio-marco-3/>
- Corea — KONEPS / Public Procurement Service: <https://pps.go.kr/eng/content.do?key=00777> ; OCDE (ficha KONEPS): <https://infrastructure-toolkit.oecd.org/wp-content/uploads/Korea_KONEPS.pdf>
- Corea–Italia, cooperación en procurement con IA (Consip): <http://www.koreapost.com/news/articleView.html?idxno=48618>
- OCDE — SMEs in Public Procurement (riesgo de agregación para PYMEs; meta 3% UGAP): <https://www.oecd.org/en/publications/smes-in-public-procurement_9789264307476-en/full-report/component-7.html>
- OCDE/SIGMA — Centralised and Decentralised Public Procurement: <https://www.oecd.org/content/dam/oecd/en/publications/reports/2000/01/centralised-and-decentralised-public-procurement_g17a1de8/5kml60w5dxr1-en.pdf>
- Reino Unido — lista de central purchasing bodies: <https://en.wikipedia.org/wiki/List_of_central_purchasing_bodies_in_the_United_Kingdom>
