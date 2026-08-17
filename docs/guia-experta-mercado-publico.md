# Guía experta — Mercado Público de Chile (de lo macro a lo micro)

> Documento para entender el sistema de compras públicas chileno de punta a punta: el modelo, quién
> lo lidera, cómo funciona, cómo se transparenta, cómo se le conoce en el mundo, y las trampas
> finas que descubrimos con datos en este proyecto. Va de lo **macro** (institucional/legal) a lo
> **micro** (mecanismos, flujo, datos, hallazgos). Fuentes al final. Fecha: 2026-08.

---

## 0. El modelo en una frase

Chile centralizó las **reglas y la plataforma** de compra (un solo sistema electrónico obligatorio,
**Mercado Público**, operado por **ChileCompra**), pero **descentralizó la ejecución**: cada uno de
los ~850 organismos del Estado compra por su cuenta dentro de ese sistema. Es un modelo de
**"mercado electrónico regulado y transparente"**, reconocido internacionalmente como pionero en
**contratación abierta**.

---

## 1. Macro — el sistema y su escala

- **Nombre del sistema:** *Mercado Público* (la plataforma, `mercadopublico.cl`).
- **Quién lo lidera:** **ChileCompra** — nombre común de la **Dirección de Compras y Contratación
  Pública (DCCP)**, un servicio público **dependiente del Ministerio de Hacienda**, creado por la
  Ley 19.886 a principios de los 2000. ChileCompra **no compra por los organismos**: fija reglas,
  opera la plataforma, administra el catálogo de Convenio Marco, capacita, fiscaliza y propone
  política.
- **Tamaño (orden de magnitud):**
  - **~$15,5 billones de pesos** proyectados en compras públicas para 2026 (miles de millones de USD).
  - **+440.000 empresas** venden al Estado; **~850 organismos** compradores.
  - **Ahorros reportados 2025: US$381 millones** (US$305M por licitaciones, comparando precio
    adjudicado vs. oferta promedio).
- **Relevancia:** la compra pública es una porción grande del gasto del Estado y una política de
  competencia, transparencia y desarrollo de proveedores (especialmente **MIPYME**).

## 2. Quién es quién (institucional)

| Actor | Rol |
|---|---|
| **ChileCompra (DCCP)** | Rectoría del sistema, plataforma Mercado Público, Convenio Marco, fiscalización, Observatorio. Depende de Hacienda. |
| **Mercado Público** | La plataforma transaccional donde ocurren licitaciones y órdenes de compra. |
| **CENABAST** | Central de Abastecimiento del sistema de salud — **central de compras sectorial** de medicamentos e insumos (caso emblemático de contratación abierta bajando precios de remedios). |
| **Contraloría General de la República** | Control de legalidad (toma de razón) y auditoría del gasto. |
| **Tribunal de Contratación Pública** | Resuelve impugnaciones sobre licitaciones. |
| **Observatorio ChileCompra** | Monitoreo, alertas de probidad y panel público de estadísticas (abierto a la ciudadanía desde 2024-2025). |

## 3. El marco legal (y la gran reforma reciente)

- **Ley 19.886** (Ley de Bases sobre Contratos Administrativos de Suministro y Prestación de
  Servicios) + su **Reglamento**: la columna vertebral del sistema.
- **Ley 21.634 (2023)** — *moderniza* la Ley 19.886. Es el cambio más importante en 20 años:
  - Objetivos: **mejorar la calidad del gasto**, subir estándares de **probidad y transparencia**,
    fortalecer a **MIPYMEs y proveedores locales**, e introducir **economía circular**.
  - Nuevos mecanismos: **subasta inversa electrónica**, **contratos de innovación**, **diálogos
    competitivos**.
  - Da a ChileCompra más facultades de **monitoreo** y de **propuesta de política**.
- **Implicancia para el análisis:** las reglas cambiaron hace poco → algunos comportamientos
  (mecanismos usados, montos) pueden variar 2024→2026; por eso miramos la **evolución temporal**.

## 4. Micro — cómo se compra: los mecanismos

De más formal/pesado a más liviano. (Los códigos son los que aparecen en la data; ver
`mercado-publico-referencia.md` §9.)

| Mecanismo | Qué es | Cuándo se usa |
|---|---|---|
| **Licitación pública** (L1/LE/LP/LQ/LR) | Concurso abierto, competitivo, formal. El tipo depende del monto en UTM. | La regla general; montos medianos/grandes. |
| **Licitación privada** | Concurso restringido (por invitación), con causal. | Excepcional. |
| **Trato Directo** (varios códigos) | Compra directa a un proveedor, con causal justificada (proveedor único, urgencia, etc.). | Cuando no aplica licitación; **hay que vigilar abusos**. |
| **Convenio Marco** (CM) | Catálogo con precios pre-licitados; el organismo "compra en la tienda". | Productos comunes/estandarizados. |
| **Compra Ágil** (AG) | Mecanismo liviano para **montos bajos**, cotización rápida a proveedores. | Compras pequeñas y frecuentes. |
| **Compra Coordinada / Conjunta** | Varios organismos **agregan demanda** en una sola compra. | Cuando conviene comprar en volumen. |
| **Microcompra / OC menor a 3 UTM** | Compras mínimas. | Montos ínfimos. |

**Convenio Marco vs. Compra Coordinada (clave):** el **Convenio Marco agrega la OFERTA** (un
catálogo que muchos usan, pero cada uno compra solo) → por eso quedan cientos de compras separadas.
La **Compra Coordinada agrega la DEMANDA** (muchos organismos compran juntos para mejor precio por
volumen), y suele ejecutarse **sobre** un Convenio Marco.

## 5. Micro — el flujo de un proceso (y las etapas OCDS)

```
Planificación → Llamado/Publicación → Recepción de ofertas → Evaluación →
Adjudicación → Orden de Compra (OC) → Recepción conforme → Pago
```
- En **licitaciones** existen todas las etapas OCDS (tender → award → contract).
- En **Trato Directo y Convenio Marco**, la data OCDS sólo tiene **adjudicación y contrato** (no
  hay etapa de licitación previa).
- La **Orden de Compra** es el **gasto efectivo** (código tipo `2097-241-SE14`); su **ítem/línea**
  (producto, cantidad, precio unitario) es el corazón del análisis de precios.

## 6. Micro — los actores del mercado

- **Compradores** (~850 organismos): gobierno central (ministerios/servicios), **salud** (servicios
  de salud y **cada hospital** — los más fragmentados), **municipios** (345 comunas, muy
  autónomos), **FFAA y de Orden**, **universidades/CFT estatales**, poder judicial, etc.
  **Empresas públicas: parcialmente fuera** de la ley.
- **Proveedores** (+440.000 empresas): **~91% son micro y pequeñas empresas (MIPYME)**. Pero la
  **concentración es alta**: **el 1% de los proveedores concentra ~80% del gasto**. Este contraste
  (muchos chicos, pocos grandes que se llevan casi todo) es central para el análisis de
  competencia y "quién siempre gana".

## 7. Micro — cómo se transparenta la data (y por qué Chile es pionero)

- **Plataforma:** Mercado Público publica licitaciones y OC en línea.
- **Acceso a datos:** **API** (tiempo real, con ticket) y **descargas masivas / OCDS**.
- **OCDS (Open Contracting Data Standard):** Chile **publica en OCDS desde 2018**, cubriendo cada
  vez más etapas (de la planificación al pago). Es un **estándar internacional** de datos abiertos
  de contratación.
- **Observatorio + panel público** de estadísticas (abierto a la ciudadanía, 2024-2025), con
  indicadores de tratos directos, proveedores, reclamos y pago oportuno.
- **Reconocimiento:** ChileCompra es citado por la **Open Contracting Partnership**, la **OCDE** y
  la **Open Government Partnership** como referente de **contratación abierta y gobierno digital**.
  Caso famoso: la apertura de datos ayudó a **bajar el precio de medicamentos** (vía CENABAST).

## 8. Cómo se conoce esto en el mundo

- **Concepto global:** "**e-procurement**" + "**open contracting**" + "**central purchasing
  bodies (CPB)**". Chile es un caso temprano y citado.
- **Referentes internacionales** (ver `investigacion-centralizacion-compras.md`):
  **KONEPS (Corea)** — la mayor plataforma del mundo; **Consip (Italia)**; **UGAP (Francia)**;
  **Crown Commercial Service (Reino Unido)**; **GSA (EE.UU.)**; **registro de preços/"carona"
  (Brasil)**. La frontera hoy: **agregación de demanda con IA** (Corea e Italia ya cooperan en eso).

## 9. Micro-micro — las trampas y hallazgos (lo que descubrimos con datos)

Esto es lo que te vuelve **experto de verdad**: no solo cómo funciona, sino **dónde engaña la data**
(detalle en `discrepancias-fuentes.md`, `metodologia-y-limites.md`, `consideraciones-futuras.md`):

1. **Cobertura ≠ todo el gasto:** empresas públicas excluidas; **Compra Ágil no está en OCDS** (sí
   en la API). Todo total es "del universo Mercado Público".
2. **Dos fuentes, distintos propósitos y campos:** la **API con ticket** (operacional, trae UNSPSC,
   no trae unidad de medida) vs. **OCDS** (transparencia/masivo, trae unidad, no trae UNSPSC en
   Trato Directo). Y **cada categoría OCDS** trae identificadores distintos (Convenio Marco trae
   ID de catálogo al 100%; Trato Directo casi nada).
3. **Normalización de producto = el problema difícil:** el código UNSPSC es muy grueso; el **ID de
   catálogo de Convenio Marco** es la mejor clave de identidad. Comparar precios sin igualar
   producto/unidad **infla falsos "sobreprecios"** (vimos un 51% que era puro artefacto).
4. **Unidad de medida y descuento por volumen:** sin unidad no se compara bien; comprar al por
   mayor baja el precio legítimamente. Hay que controlar por cantidad.
5. **Estacionalidad y geografía:** perecibles varían por temporada y región → controlar antes de
   concluir.
6. **El ahorro por precio es modesto (~2-4%)** en productos idénticos — coincide con metas
   internacionales (~3%). El premio grande está en **reducir fragmentación de proceso**,
   **estandarizar** y **ampliar cobertura**, no en el precio.
7. **En Convenio Marco el precio ya está casi alineado** (dispersión ~1,05×): la ineficiencia ahí
   es de **proceso** (cientos de organismos comprando lo mismo por separado), no de precio.

## 10. Glosario rápido

- **DCCP / ChileCompra:** el organismo rector (Min. Hacienda).
- **Mercado Público:** la plataforma transaccional.
- **Licitación (L1/LE/LP…):** concurso abierto; la letra/monto en UTM define el tipo.
- **Trato Directo:** compra directa con causal.
- **Convenio Marco (CM):** catálogo pre-licitado (agrega oferta).
- **Compra Ágil (AG):** mecanismo liviano para montos bajos.
- **Compra Coordinada:** agregación de demanda (varios compran juntos).
- **Orden de Compra (OC):** el gasto efectivo.
- **UTM:** Unidad Tributaria Mensual (define umbrales de monto).
- **UNSPSC:** código estándar ONU de productos/servicios.
- **OCDS:** estándar internacional de datos abiertos de contratación.
- **CENABAST:** central de compras de salud.
- **MIPYME:** micro, pequeña y mediana empresa (91% de los proveedores).

---

## Fuentes

- ChileCompra — Ley 21.634 moderniza el sistema (2023): <https://www.chilecompra.cl/2023/12/ya-es-ley-la-modernizacion-al-sistema-de-compras-publicas/>
- Ministerio de Hacienda — promulgación Ley 21.634: <https://www.hacienda.cl/subsecretaria/noticias/presidente-boric-promulgo-ley-que-moderniza-las-compras-publicas-y-destaco-que>
- ChileCompra — Cuenta Pública: ahorros US$381M en 2025 y herramientas con IA para 2026: <https://www.chilecompra.cl/2026/07/cuenta-publica-participativa-de-chilecompra-destaca-ahorros-por-us-381-millones-en-2025-y-presenta-nuevas-herramientas-con-inteligencia-artificial-para-2026/>
- ChileCompra — Estadísticas Mercado Público: <https://www.chilecompra.cl/estadisticas-mercado-publico/>
- Open Contracting Partnership — Chile y el costo de los medicamentos: <https://www.open-contracting.org/2021/01/29/diagnosis-open-how-open-contracting-is-bringing-down-the-cost-of-medicines-in-chile/>
- Open Contracting Partnership — Observatorio de compras abierto a la ciudadanía (2024): <https://www.open-contracting.org/2024/11/04/el-observatorio-de-compras-visible-a-la-ciudadania-en-chile/>
- Open Government Partnership — implementación de OCDS en Chile: <https://www.opengovpartnership.org/members/chile/commitments/CL0062/>
- OCDE — Gobierno Digital en Chile: <https://www.oecd.org/en/publications/digital-government-in-chile_d1b72d93-en.html>
- (Compras coordinadas y modelos internacionales: ver `docs/investigacion-centralizacion-compras.md`.)
