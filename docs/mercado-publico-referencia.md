# Mercado Público de Chile — Referencia única del proyecto

> **Archivo maestro.** Es la **fuente única de verdad** del proyecto: contexto, fuentes de
> datos, ambas APIs, los diccionarios de datos completos, las tablas de códigos validadas y
> las trampas conocidas. Está pensado para que cualquier persona —o Claude— se oriente
> leyendo **solo este archivo**.
>
> **Trazabilidad / auditoría:** todo lo técnico aquí proviene de la documentación oficial de
> ChileCompra, conservada sin modificar en [`docs/fuentes/`](./fuentes/). Cada sección de datos
> cita su fuente. Si algo en este maestro y una fuente difieren, **manda la fuente**; corrige el
> maestro y deja nota.
>
> Última consolidación: 2026-08-14.

## Tabla de contenido

1. [Objetivo del proyecto](#1-objetivo-del-proyecto)
2. [Hipótesis a validar](#2-hipótesis-a-validar)
3. [Fuentes de datos](#3-fuentes-de-datos)
4. [Manejo del ticket, autenticación y límites de uso](#4-manejo-del-ticket-autenticación-y-límites-de-uso)
5. [Modelo de datos (entidades)](#5-modelo-de-datos-entidades)
6. [Diccionario de datos — Órdenes de Compra](#6-diccionario-de-datos--órdenes-de-compra)
7. [Diccionario de datos — Licitaciones](#7-diccionario-de-datos--licitaciones)
8. [API v2 Compra Ágil (`api2.mercadopublico.cl`)](#8-api-v2-compra-ágil-api2mercadopublicocl)
9. [Tablas de códigos (validadas)](#9-tablas-de-códigos-validadas)
10. [Normalización de productos (UNSPSC)](#10-normalización-de-productos-unspsc)
11. [Límites, validaciones y correcciones conocidas](#11-límites-validaciones-y-correcciones-conocidas)
12. [Arquitectura sugerida](#12-arquitectura-sugerida)
13. [Plan por fases](#13-plan-por-fases)
14. [Decisiones pendientes](#14-decisiones-pendientes)
15. [Legal / ético](#15-legal--ético)
16. [Enlaces y fuentes](#16-enlaces-y-fuentes)

---

## 1. Objetivo del proyecto

Construir un pipeline de ingesta + un **informe / web interactiva** sobre las compras del
Estado chileno, apuntando a análisis que **hoy casi nadie hace bien**. El foco NO es "cuánto
gasta el Estado" (eso ya existe), sino **evidencia navegable** que un ciudadano pueda explorar.

**Diferenciador:** ya hay gente publicando *conclusiones* sobre estos problemas (ver §2), pero
sin mostrar la data. Nuestro valor es lo contrario: **cada afirmación respaldada por evidencia
con drill-down** hasta las licitaciones/órdenes concretas. La web interactiva es el entregable
estrella, no un PDF con gráficos estáticos.

Visualizaciones núcleo:

1. **Comparador de precios**: el mismo producto pagado a precios distintos entre
   organismos/comunas → sobreprecios.
2. **Concentración de proveedores**: quién "siempre gana" en cierta repartición/comuna; grafo
   comprador↔proveedor.
3. **Fragmentación y tipo de proceso**: cuánto se licita por separado que podría consolidarse;
   proceso pesado vs. monto.

Prioridad: MVP con #1 y una versión medible de #3.

---

## 2. Hipótesis a validar

Circulan análisis (LinkedIn, prensa) que afirman que Mercado Público está "roto". Los tratamos
como **hipótesis testeables, no como verdades**. El proyecto las verifica con data y reporta lo
que la data muestre, **incluida la contra-evidencia**. Objetivo: un informe imparcial y
reproducible, no un panfleto.

### H1 — Micro-fragmentación
*Tesis:* cientos de escuelas/hospitales/municipios licitan por separado los mismos insumos
cotidianos en vez de consolidar demanda.
- **Cómo medirlo:** para una categoría commodity (útiles, agua, carpas), contar procesos
  distintos por N organismos en una ventana; % de procesos bajo cierto umbral de monto.
- **Contra-evidencia:** parte de esa demanda **ya está consolidada vía Convenio Marco** → hay
  que descontar lo agregado antes de gritar fragmentación.

### H2 — Silos tecnológicos
*Tesis:* servidores, parches de software y sitios web se licitan pieza por pieza, ignorando
infraestructura centralizada.
- **Cómo medirlo:** filtrar rubros TI (códigos de categoría UNSPSC de tecnología); contar
  contratos pequeños/aislados; dispersión de proveedores y montos por organismo.
- **Contra-evidencia:** parte puede estar bajo convenios marco de tecnología.

### H3 — Proceso pesado para compras triviales
*Tesis:* se usa el proceso de licitación completo (largo, formal) para comprar cosas de bajo monto.
- **Cómo medirlo:** cruzar **tipo de proceso** (licitación L1/LE/LP vs. trato directo vs.
  convenio marco vs. compra ágil) contra **monto**; destacar licitaciones completas de montos bajos.
- **⚠️ CAVEAT ACTUALIZADO (antes se creía peor):** el documento original decía que "Compra Ágil
  no está en el dataset y eso sesga H3". **Eso ya no es del todo cierto:** Compra Ágil **sí es
  accesible** por dos vías (ver §3 y §8): aparece como orden de compra tipo `AG` en la API de OC,
  y además tiene una **API dedicada** (`api2.mercadopublico.cl/v2/compra-agil`). Sigue estando
  **ausente de las descargas masivas OCDS**, así que el sesgo existe *solo si te limitas a OCDS*.
  Con las APIs se puede capturar. Documentarlo explícito en el informe.
- **Ojo con supuestos:** "horas-hombre desperdiciadas" NO está en la data; es una estimación.
  Si se muestra, etiquetar como *modelo*, no como *dato*.

**Regla editorial:** toda conclusión fuerte va acompañada del dato que la sostiene y del que la
matiza. El drill-down es la prueba.

---

## 3. Fuentes de datos

Hay **tres** caminos. Se usan combinados.

### 3.1 API REST "clásica" v1 — `api.mercadopublico.cl`
Buena para: datos frescos, un proceso puntual, el día actual. Mala para: histórico masivo.

- **Base:** `https://api.mercadopublico.cl/servicios/v1/publico/`
- **Formatos:** `.json` (default), `.jsonp`, `.xml`
- **Auth:** parámetro `&ticket=<TICKET>` en la URL de cada request.
- **Formato de fecha:** `ddmmaaaa` sin separadores (ej. `02022014` = 2-feb-2014).
- **Patrón de dos pasos:** la consulta "por día" devuelve un **listado liviano** (solo
  `Codigo`, `Nombre`, `CodigoEstado`); el **detalle completo** (ítems, precios, proveedor,
  organismo) se pide **por `codigo`**. No existe método que devuelva la ficha completa en una
  sola llamada.

**Endpoints — Licitaciones:**
```
# Del día actual (todos los estados)
GET /servicios/v1/publico/licitaciones.json?ticket=<TICKET>
# De una fecha
GET /servicios/v1/publico/licitaciones.json?fecha=02022014&ticket=<TICKET>
# Por código (detalle; la fecha es irrelevante)
GET /servicios/v1/publico/licitaciones.json?codigo=1509-5-L114&ticket=<TICKET>
# Por fecha + estado
GET /servicios/v1/publico/licitaciones.json?fecha=02022014&estado=adjudicada&ticket=<TICKET>
# Por proveedor / organismo (en una fecha)
GET /servicios/v1/publico/licitaciones.json?fecha=02022014&CodigoProveedor=17793&ticket=<TICKET>
GET /servicios/v1/publico/licitaciones.json?fecha=02022014&CodigoOrganismo=6945&ticket=<TICKET>
```

**Endpoints — Órdenes de Compra:**
```
# Del día actual por estado
GET /servicios/v1/publico/ordenesdecompra.json?estado=todos&ticket=<TICKET>
# De una fecha
GET /servicios/v1/publico/ordenesdecompra.json?fecha=02022014&ticket=<TICKET>
# Por código (detalle completo)
GET /servicios/v1/publico/ordenesdecompra.json?codigo=2097-241-SE14&ticket=<TICKET>
# Por fecha + estado / organismo / proveedor
GET /servicios/v1/publico/ordenesdecompra.json?fecha=02022014&estado=aceptada&ticket=<TICKET>
GET /servicios/v1/publico/ordenesdecompra.json?fecha=02022014&CodigoOrganismo=6945&ticket=<TICKET>
```
> Nota: el diccionario oficial de OC menciona también la ruta singular
> `OrdenCompra.json?codigo=...`. En la práctica, `ordenesdecompra.json?codigo=...` funciona y
> devuelve el detalle completo (verificado con `1001546-22-AG24`).

**Empresas / organismos:**
```
# Proveedor por RUT (con puntos, guión y DV)
GET /servicios/v1/Publico/Empresas/BuscarProveedor?rutempresaproveedor=70.017.820-k&ticket=<TICKET>
# Listado de organismos compradores
GET /servicios/v1/Publico/Empresas/BuscarComprador?ticket=<TICKET>
```

### 3.2 API v2 Compra Ágil — `api2.mercadopublico.cl`
API moderna, separada, **solo para Compra Ágil**. Autenticación por header, paginada, con
filtros por región/estado/fecha/palabra clave. Detalle completo en §8.

### 3.3 Descargas masivas + OCDS — `datos-abiertos.chilecompra.cl`
Buena para: **histórico y masivo** (el 90% del proyecto). Camino correcto para poblar la base
la primera vez.
- **Procesos OCDS:** `https://datos-abiertos.chilecompra.cl/descargas/procesos-ocds`
- **Descargas masivas OC y licitaciones:** `https://datos-abiertos.chilecompra.cl/descargas/ordenes-y-licitaciones`
- **⚠️ Compra Ágil NO está en OCDS** → para capturarla, usar las APIs (§3.1 tipo `AG`, o §8).

**Estrategia:** cargar histórico desde descargas masivas/OCDS → mantener al día con la API por
incrementales. No reconstruir el histórico llamando la API día por día.

---

## 4. Manejo del ticket, autenticación y límites de uso

### 4.1 El ticket (SECRETO)
El ticket es una credencial de solo lectura sobre datos públicos, pero **se trata como secreto**:
- Va en `.env` en la raíz del repo: `MERCADO_PUBLICO_TICKET=...`
- **`.env` está en `.gitignore`.** Nunca commitear el ticket. Nunca hardcodearlo.
- El código lo lee del entorno (`os.environ` / `python-dotenv`).
- Hay un `.env.example` (sin valor) para documentar qué variables se necesitan.
- Se solicita en <https://www.chilecompra.cl/api/> ("Pide tu ticket", con Clave Única). Se
  entrega **un ticket por persona** (RUT). Llega por correo.
- Ticket de **prueba** público (solo pruebas): `F8537A18-6766-4DEF-9E59-426B4FEE2844`

### 4.2 Autenticación por API
| API | Cómo se envía el ticket |
|---|---|
| v1 clásica (`api.mercadopublico.cl`) | Query param `&ticket=<TICKET>` en la URL |
| v2 Compra Ágil (`api2.mercadopublico.cl`) | **Header HTTP** `ticket: <TICKET>` (no en la URL) |

### 4.3 Límites de uso (rate limiting)
- **API v1:** límite de **10.000 solicitudes diarias por ticket** (no modificable). Monitoreo
  por IP. Para descargas masivas se recomienda horario nocturno (**22:00–07:00**).
- **API v2 Compra Ágil:** cuota diaria por ticket (según tipo de ticket; `-1` = ilimitada). El
  contador se reinicia por **día calendario**. Al agotarse devuelve **HTTP 429**.
- **⚠️ Lo aprendido en la práctica (ver discrepancia D16):** el límite que realmente muerde **no**
  es el tope diario, sino un **límite de ráfaga** (por ventana corta). Al pedir detalles seguidos,
  la API responde `429` muy seguido con espera efectiva de ~6-7 s por request (1.500 detalles ≈
  2h50m). El tope de 10.000/día casi no se alcanza en un día de muestreo.
- **Estrategia de ingesta eficiente (implementada):**
  1. **Ritmo adaptativo AIMD** (`download_lote_detalles`): la pausa sube ante `429` y baja si va
     limpio → converge al ritmo más rápido que la API tolera sin malgastar esperas.
  2. **Honrar `Retry-After`** cuando viene (`api_client`).
  3. **Contador de cuota diaria persistente** (`quota.py`): respeta el tope de 10.000 aunque se
     corra en varias sesiones; el descargador corta y avisa "sigue mañana" (es idempotente).
  4. **La concurrencia NO ayuda** (el límite es del servidor, no de latencia del cliente).
  5. Para **volumen histórico real**, NO usar la API detalle-a-detalle → usar **descargas masivas
     OCDS** (§3.3). Ese es el camino correcto para poblar la base la primera vez.

---

## 5. Modelo de datos (entidades)

```
Organismo comprador ──< Licitación ──< Adjudicación ──< Orden de Compra ──< Ítem (línea)
                                                              │                    │
                                                         Proveedor (RUT)      Producto/Rubro (UNSPSC)
```

- **Licitación:** tipo por monto (ver §9.5). Estados: publicada, cerrada, desierta, adjudicada,
  revocada, suspendida.
- **Orden de Compra:** el **gasto efectivo**. Código tipo `2097-241-SE14`. Puede o no venir de
  una licitación (`CodigoLicitacion` puede estar vacío, p. ej. en Compra Ágil / trato directo).
- **Ítem / línea:** `CodigoProducto` (UNSPSC), `Cantidad`, `PrecioNeto` (= precio unitario),
  `CodigoCategoria`. **Corazón del comparador de precios.**
- **Proveedor:** identificado por **RUT** → grafos de concentración.
- **Organismo comprador:** repartición/comuna → comparación de precios y fragmentación.

---

## 6. Diccionario de datos — Órdenes de Compra

> Fuente: [`docs/fuentes/diccionario-datos-ordenes-de-compra.pdf`](./fuentes/diccionario-datos-ordenes-de-compra.pdf)
> (Diccionario de Datos oficial, `api.mercadopublico.cl`). Ruta base de cada campo:
> `Listado/…`. `Cantidad`, `FechaCreacion` y `Version` son de nivel superior de la respuesta.

| # | Campo | Descripción | Tipo | Largo |
|---|---|---|---|---|
| 1 | `Cantidad` | Cantidad de OC consultadas | Int | |
| 2 | `FechaCreacion` | Fecha de consulta | DateTime | |
| 3 | `Version` | Versión del API | texto | |
| 4 | `Listado/Codigo` | **Código de la OC** | Nvarchar | 50 |
| 5 | `Listado/Nombre` | Nombre de la OC | Nvarchar | 255 |
| 6 | `Listado/CodigoEstado` | Código de estado de la OC (§9.1) | Int | 4 |
| 7 | `Listado/CodigoLicitacion` | Código de la licitación asociada (puede ir vacío) | Nvarchar | 50 |
| 8 | `Listado/Descripcion` | Descripción de la OC | Nvarchar | 2000 |
| 9 | `Listado/CodigoTipo` | Código del tipo de OC | Nvarchar | 80 |
| 10 | `Listado/Tipo` | Tipo de OC (§9.3) | Nvarchar | 2 |
| 11 | `Listado/TipoMoneda` | Moneda de la OC (§9.7) | Nvarchar | 255 |
| 12 | `Listado/CodigoEstadoProveedor` | Código estado del proveedor | Int | |
| 13 | `Listado/EstadoProveedor` | Estado del proveedor | Nvarchar | 255 |
| 14 | `Listado/Fechas/FechaCreacion` | Fecha de creación de la OC | DateTime | |
| 15 | `Listado/Fechas/FechaEnvio` | Fecha de envío | DateTime | |
| 16 | `Listado/Fechas/FechaAceptacion` | Fecha de aceptación | DateTime | |
| 17 | `Listado/Fechas/FechaCancelacion` | Fecha de cancelación | DateTime | |
| 18 | `Listado/Fechas/FechaUltimaModificacion` | Última modificación | DateTime | |
| 19 | `Listado/TieneItems` | ¿Tiene ítems? 1=Sí, 0=No | Nvarchar | 255 |
| 20 | `Listado/PromedioCalificacion` | Promedio de calificación del proveedor | Float | |
| 21 | `Listado/CantidadEvaluacion` | Nº evaluaciones del proveedor | Int | |
| 22 | `Listado/Descuentos` | Descuento aplicado a la OC | Float | |
| 23 | `Listado/Cargos` | Cargos aplicados a la OC | Float | |
| 24 | `Listado/TotalNeto` | Total neto de la OC | Float | |
| 25 | `Listado/PorcentajeIva` | % IVA aplicado | Float | |
| 26 | `Listado/Impuestos` | Impuesto aplicado | Float | |
| 27 | `Listado/Total` | Total de la OC | Float | |
| 28 | `Listado/Financiamiento` | Fuente de financiamiento | Nvarchar | 255 |
| 29 | `Listado/Pais` | País de la OC | Nvarchar | 255 |
| 30 | `Listado/TipoDespacho` | Tipo de despacho (§9.6) | Nvarchar | 255 |
| 31 | `Listado/FormaPago` | Forma de pago (§9.4) | Nvarchar | 255 |
| 32 | `Listado/Comprador/CodigoOrganismo` | Código del organismo comprador | Nvarchar | 20 |
| 33 | `Listado/Comprador/NombreOrganismo` | Nombre del organismo | Nvarchar | 255 |
| 34 | `Listado/Comprador/RutUnidad` | RUT de la unidad | Nvarchar | 20 |
| 35 | `Listado/Comprador/CodigoUnidad` | Código de unidad | Nvarchar | 20 |
| 36 | `Listado/Comprador/NombreUnidad` | Nombre de unidad | Nvarchar | 255 |
| 37 | `Listado/Comprador/Actividad` | Actividad del comprador | Nvarchar | 255 |
| 38 | `Listado/Comprador/DireccionUnidad` | Dirección de la unidad | Nvarchar | 255 |
| 39 | `Listado/Comprador/ComunaUnidad` | **Comuna** de la unidad compradora | Nvarchar | 255 |
| 40 | `Listado/Comprador/RegionUnidad` | **Región** de la unidad compradora | Nvarchar | 255 |
| 41 | `Listado/Comprador/Pais` | País de la unidad | Nvarchar | 255 |
| 42 | `Listado/Comprador/NombreContacto` | Nombre contacto | Nvarchar | 255 |
| 43 | `Listado/Comprador/CargoContacto` | Cargo del contacto | Nvarchar | 255 |
| 44 | `Listado/Comprador/FonoContacto` | Teléfono del contacto | Nvarchar | 100 |
| 45 | `Listado/Comprador/MailContacto` | Email del contacto | Nvarchar | 50 |
| 46 | `Listado/Proveedor/Codigo` | Código del proveedor | Nvarchar | 20 |
| 47 | `Listado/Proveedor/Nombre` | Nombre del proveedor | Nvarchar | 255 |
| 48 | `Listado/Proveedor/Actividad` | Actividad del proveedor | Nvarchar | 255 |
| 49 | `Listado/Proveedor/CodigoSucursal` | Código de la sucursal | Nvarchar | 20 |
| 50 | `Listado/Proveedor/NombreSucursal` | Nombre de la sucursal | Nvarchar | 255 |
| 51 | `Listado/Proveedor/RutSucursal` | **RUT del proveedor** | Nvarchar | 20 |
| 52 | `Listado/Proveedor/Direccion` | Dirección del proveedor | Nvarchar | 255 |
| 53 | `Listado/Proveedor/Comuna` | Comuna del proveedor | Nvarchar | 255 |
| 54 | `Listado/Proveedor/Region` | Región del proveedor | Nvarchar | 255 |
| 55 | `Listado/Proveedor/Pais` | País del proveedor | Nvarchar | 255 |
| 56 | `Listado/Proveedor/NombreContacto` | Nombre contacto proveedor | Nvarchar | 255 |
| 57 | `Listado/Proveedor/CargoContacto` | Cargo contacto proveedor | Nvarchar | 255 |
| 58 | `Listado/Proveedor/FonoContacto` | Teléfono contacto proveedor | Nvarchar | 255 |
| 59 | `Listado/Proveedor/MailContacto` | Email contacto proveedor | Nvarchar | 255 |
| 60 | `Listado/Items/Cantidad` | Nº de ítems (productos) de la OC | Int | |
| 61 | `Listado/Items/Listado` | Listado de ítems | | |
| 62 | `Listado/Items/Listado/Correlativo` | Correlativo del ítem | BigInt | |
| 63 | `Listado/Items/Listado/CodigoCategoria` | Código de categoría UNSPSC (§10) | Int | |
| 64 | `Listado/Items/Listado/Categoria` | Nombre de la categoría | Varchar | 400 |
| 65 | `Listado/Items/Listado/CodigoProducto` | **Código de producto UNSPSC** (§10) | Int | |
| 66 | `Listado/Items/Listado/EspecificacionComprador` | Especificación pedida por el comprador | Nvarchar | -1 |
| 67 | `Listado/Items/Listado/EspecificacionProveedor` | Especificación provista por el proveedor | Nvarchar | 510 |
| 68 | `Listado/Items/Listado/Cantidad` | Cantidad de productos | Float | |
| 69 | `Listado/Items/Listado/Moneda` | Moneda del producto | Nvarchar | 100 |
| 70 | `Listado/Items/Listado/PrecioNeto` | **Precio neto O PRECIO UNITARIO del producto** | Float | |
| 71 | `Listado/Items/Listado/TotalCargos` | Total cargos (sobre PrecioNeto×Cantidad) | Float | |
| 72 | `Listado/Items/Listado/TotalDescuentos` | Total descuentos (sobre PrecioNeto×Cantidad) | Float | |
| 73 | `Listado/Items/Listado/TotalImpuestos` | Total impuestos (sobre PrecioNeto×Cantidad) | Float | |
| 74 | `Listado/Items/Listado/Total` | Total final de la línea | Float | |

> **🔑 Corrección clave (leer):** el campo **`PrecioNeto` (70) ya ES el precio unitario** — no
> se divide por la cantidad. El total de la línea ≈ `PrecioNeto × Cantidad` (± cargos/descuentos/
> impuestos). **Ojo con la calidad del dato:** en muestras reales el campo `Total` (74) del ítem
> ha venido en `0.0` aunque `PrecioNeto` traía el valor correcto → no confiar ciegamente en
> `Total`; derivar el total de la línea desde `PrecioNeto × Cantidad` y marcar outliers.

---

## 7. Diccionario de datos — Licitaciones

> Fuente: [`docs/fuentes/diccionario-datos-licitaciones.pdf`](./fuentes/diccionario-datos-licitaciones.pdf).
> Ruta base de cada campo: `Licitaciones/Listado/Licitacion/…`.

| # | Campo (`…/Licitacion/…`) | Descripción | Tipo | Largo |
|---|---|---|---|---|
| 1 | `Cantidad` | Nº licitaciones consultadas | entero | |
| 2 | `FechaCreacion` | Fecha de consulta | datetime | |
| 3 | `Version` | Versión del API | texto | |
| 4 | `CodigoExterno` | **Código de la licitación** | nvarchar | 100 |
| 5 | `Nombre` | Nombre de la licitación | nvarchar | 255 |
| 6 | `CodigoEstado` | Código de estado (§9.2) | entero | 4 |
| 7 | `FechaCierre` | Fecha de cierre | DateTime | |
| 8 | `Descripcion` | Descripción / objeto de la contratación | nvarchar | max |
| 9 | `Estado` | Estado (texto) | nvarchar | 510 |
| 10 | `Comprador/CodigoOrganismo` | Código del organismo responsable | nvarchar | 100 |
| 11 | `Comprador/NombreOrganismo` | Nombre del organismo | nvarchar | 510 |
| 12 | `Comprador/RutUnidad` | RUT del organismo | nvarchar | 100 |
| 13 | `Comprador/CodigoUnidad` | Código del organismo | nvarchar | 100 |
| 14 | `Comprador/NombreUnidad` | Nombre de la unidad de compra | nvarchar | 510 |
| 15 | `Comprador/DireccionUnidad` | Dirección de la unidad | nvarchar | 510 |
| 16 | `Comprador/ComunaUnidad` | Comuna de la unidad | nvarchar | 510 |
| 17 | `Comprador/RegionUnidad` | Región de la unidad | nvarchar | 510 |
| 18 | `Comprador/RutUsuario` | RUT del usuario responsable | nvarchar | 100 |
| 19 | `Comprador/CodigoUsuario` | Código del usuario | nvarchar | 100 |
| 20 | `Comprador/NombreUsuario` | Nombre del usuario | texto | |
| 21 | `Comprador/CargoUsuario` | Cargo del usuario | nvarchar | 100 |
| 22 | `DiasCierreLicitacion` | Días para el cierre | entero | |
| 23 | `Informada` | ¿Informada? 1=Sí, 0=No | bit | 1 |
| 24 | `CodigoTipo` | Tipo (1=Pública, 2=Privada) | entero | 4 |
| 25 | `Tipo` | Tipo de licitación (§9.5) | nvarchar | 20 |
| 26 | `TipoConvocatoria` | 1=Abierto, 0=Cerrada | int | 4 |
| 27 | `Moneda` | Moneda (§9.7) | nvarchar | 100 |
| 28 | `Etapas` | Nº de etapas (1 o 2) | int | 4 |
| 29 | `EstadoEtapas` | Aperturas realizadas [1,2] | int | 4 |
| 30 | `TomaRazon` | 1=Con toma de razón, 0=No | int | 4 |
| 31 | `EstadoPublicidadOfertas` | 1=Sí, 0=No | smallint | 2 |
| 32 | `JustificacionPublicidad` | Justificación de publicidad de oferta técnica | nvarchar | -1 |
| 33 | `Contrato` | 1=Requiere subscripción, 2=Formaliza con OC | int | 4 |
| 34 | `Obras` | ¿Es obra? 0=No, 2=Sí | int | 4 |
| 35 | `CantidadReclamos` | Nº de reclamos | entero | |
| 36 | `Fechas/FechaCreacion` | Creación | DateTime | |
| 37 | `Fechas/FechaCierre` | Cierre | DateTime | |
| 38 | `Fechas/FechaInicio` | Inicio del foro | DateTime | |
| 39 | `Fechas/FechaFinal` | Cierre del foro | DateTime | |
| 40 | `Fechas/FechaPubRespuestas` | Publicación de respuestas | DateTime | |
| 41 | `Fechas/FechaActoAperturaTecnica` | Apertura técnica | DateTime | |
| 42 | `Fechas/FechaActoAperturaEconomica` | Apertura económica | DateTime | |
| 43 | `Fechas/FechaPublicacion` | Publicación | DateTime | |
| 44 | `Fechas/FechaAdjudicacion` | Adjudicación | DateTime | |
| 45 | `Fechas/FechaEstimadaAdjudicacion` | Adjudicación estimada | DateTime | |
| 46 | `Fechas/FechaSoporteFisico` | Soporte físico | DateTime | |
| 47 | `Fechas/FechaTiempoEvaluacion` | Evaluación | DateTime | |
| 48 | `Fechas/FechaEstimadaFirma` | Firma estimada | DateTime | |
| 49 | `Fechas/FechasUsuario` | ¿Definió fechas adicionales? | DateTime | |
| 50 | `Fechas/FechaVisitaTerreno` | Visita a terreno | DateTime | |
| 51 | `Fechas/FechaEntregaAntecedentes` | Entrega de antecedentes | DateTime | |
| 52 | `UnidadTiempoEvaluacion` | Unidad de tiempo de evaluación (§9.9) | int | 4 |
| 53 | `DireccionVisita` | Dirección de visita | varchar | 500 |
| 54 | `DireccionEntrega` | Dirección de entrega | varchar | 500 |
| 55 | `Estimacion` | Código de tipo de estimación (§9.8) | | |
| 56 | `FuenteFinanciamiento` | Fuente de financiamiento | int | 4 |
| 57 | `VisibilidadMonto` | 1=Sí, 0=No | bit | 1 |
| 58 | `MontoEstimado` | Monto estimado | float | 53 |
| 59 | `UnidadTiempo` | Unidad de tiempo (duración contrato) | int | 4 |
| 60 | `Modalidad` | Modalidad de pago (§9.10) | int | 4 |
| 61 | `TipoPago` | Tipo de pago | int | 4 |
| 62 | `NombreResponsablePago` | Responsable del pago | nvarchar | 200 |
| 63 | `EmailResponsablePago` | Email responsable del pago | nvarchar | 200 |
| 64 | `NombreResponsableContrato` | Responsable del contrato | nvarchar | 200 |
| 65 | `EmailResponsableContrato` | Email responsable del contrato | nvarchar | 200 |
| 66 | `FonoResponsableContrato` | Teléfono responsable del contrato | nvarchar | 200 |
| 67 | `ProhibicionContratacion` | ¿Se prohíbe la contratación? | nvarchar | 510 |
| 68 | `SubContratacion` | 1=Sí, 0=No | bit | 1 |
| 69 | `UnidadTiempoDuracionContrato` | Unidad de tiempo del contrato (§9.9) | int | 4 |
| 70 | `TiempoDuracionContrato` | Duración del contrato | int | 4 |
| 71 | `TipoDuracionContrato` | Nombre del período | nvarchar | 510 |
| 72 | `JustificacionMontoEstimado` | Justificación del monto estimado | varchar | 255 |
| 73 | `ExtensionPlazo` | 1=Extiende, 0=No extiende | smallint | 2 |
| 74 | `EsBaseTipo` | ¿Creada desde licitación tipo? 1=Sí, 0=No | bit | 1 |
| 75 | `UnidadTiempoContratoLicitacion` | Código de período | int | 4 |
| 76 | `ValorTiempoRenovacion` | Valor de tiempo de renovación | int | 4 |
| 77 | `PeriodoTiempoRenovacion` | Nombre del período de renovación | nvarchar | 510 |
| 78 | `EsRenovable` | 1=Sí, 0=No | bit | 1 |
| 79 | `Adjudicacion/Tipo` | Tipo de acto administrativo (§9.11) | int | 4 |
| 80 | `Adjudicacion/Fecha` | Fecha del acto de adjudicación | datetime | |
| 81 | `Adjudicacion/Numero` | Número del acto administrativo | nvarchar | 100 |
| 82 | `Adjudicacion/NumeroOferentes` | Nº de proveedores adjudicados | entero | |
| 83 | `Adjudicacion/UrlActa` | URL del acta de adjudicación | texto | |
| 84 | `Items/Cantidad` | Nº de productos/servicios | entero | |
| 85 | `Items/Listado/item/CodigoEstadoLicitacion` | Código de estado (por ítem) | entero | 4 |
| 86 | `Items/Listado/item/Correlativo` | Correlativo del ítem | entero | |
| 87 | `Items/Listado/item/CodigoProducto` | **Código de producto UNSPSC v7** (§10) | entero | |
| 88 | `Items/Listado/item/CodigoCategoria` | **Código de categoría UNSPSC v7** (§10) | nvarchar | 100 |
| 89 | `Items/Listado/item/Categoria` | Nombre de la categoría | varchar | 400 |
| 90 | `Items/Listado/item/NombreProducto` | Nombre del producto/servicio | nvarchar | 510 |
| 91 | `Items/Listado/item/Descripcion` | Descripción del producto/servicio | nvarchar | 510 |
| 92 | `Items/Listado/item/UnidadMedida` | Unidad de medida | nvarchar | 510 |
| 93 | `Items/Listado/item/Cantidad` | Cantidad | float | 8 |
| 94 | `Items/Listado/item/Adjudicacion/RutProveedor` | **RUT del proveedor adjudicado** (por línea) | nvarchar | 100 |
| 95 | `Items/Listado/item/Adjudicacion/NombreProveedor` | Nombre del proveedor adjudicado | nvarchar | 500 |
| 96 | `Items/Listado/item/Adjudicacion/CantidadAdjudicada` | Cantidad adjudicada (por línea) | nvarchar | 500 |
| 97 | `Items/Listado/item/Adjudicacion/MontoUnitario` | **Monto unitario adjudicado** (por línea) | float | 8 |

---

## 8. API v2 Compra Ágil (`api2.mercadopublico.cl`)

> Fuente: [`docs/fuentes/guia-api-compra-agil-v3.0.pdf`](./fuentes/guia-api-compra-agil-v3.0.pdf)
> (Guía de Uso API Compra Ágil v2, **Versión 3.0, Mayo 2026** — la más reciente; las v2.0 y v2.x
> están en `docs/fuentes/` solo por auditoría). Es una API **distinta** de la v1 clásica.

### 8.1 Básico
- **Base:** `https://api2.mercadopublico.cl`
- **Auth:** header `ticket: <TICKET>` (sin ticket → 401).
- **Envoltura de respuesta:** `{"success":"OK","trace":null,"payload":{…},"errors":null}`.
  En error: `success:"NOK"`, `payload:null`, `errors:[{codigo,mensaje,detalle}]`.
- **Código de proceso:** formato `1057539-228-COT26`.

### 8.2 Endpoints
| Endpoint | Método | Descripción |
|---|---|---|
| `/v2/compra-agil` | GET | Listado y búsqueda con filtros y paginación |
| `/v2/compra-agil/{codigo}` | GET | Detalle completo (productos, proveedores cotizando, montos) |

### 8.3 Parámetros del listado (`/v2/compra-agil`)
- **Ventana de cambios (usar A *o* B):** `ttl_cambio_ms` (int ms, opción A) **|**
  `cambio_desde` + `cambio_hasta` (ISO-8601, opción B).
- **Fecha de publicación:** `publicado_desde`, `publicado_hasta` (ISO-8601).
- **Estado** (coma-separado): `publicada`, `cerrada`, `desierta`, `cancelada`,
  `proveedor_seleccionado`, `oc_emitida` *(este último definido pero no usado en la práctica →
  ver §8.5)*.
- **Región:** `region` (entero 1–16, repetible; §9.12). ⚠️ **No existe `codigo_organismo`** en
  esta API: para un organismo, filtrar por `region=` y luego por `institucion.rut` en tu sistema.
- **Búsqueda:** `id` (código exacto) **|** `q` (palabras clave URL-encoded) — mutuamente excluyentes.
- **Paginación:** `tamano_pagina` (default 15, máx 50), `numero_pagina` (empieza en 1).
- **Orden:** `ordenar_por` = `FechaUltimaModificacion` (default) | `FechaPublicacion`.

### 8.4 Campos principales
**Listado (`payload.items[]`):** `codigo`, `nombre`, `estado.{id_estado,codigo,glosa}`,
`convocatoria.{estado_convocatoria,descripcion}`, `fechas.{fecha_publicacion,fecha_cierre,
fecha_ultimo_cambio,fecha_cancelacion}`, `montos.{moneda,monto_disponible,monto_disponible_clp}`,
`institucion.{organismo_comprador,rut,unidad_compra,region,nombre_region}`,
`resumen.total_ofertas_recibidas`, `links.detalle`.

**Paginación (`payload.paginacion`):** `total_paginas`, `numero_pagina`, `tamano_pagina`,
`total_resultados`.

**Detalle (`payload`):** todo lo del listado + `descripcion`, `convocatoria.fecha_cierre_
{primer,segundo}_llamado`, `entrega.{direccion_entrega,plazo_entrega_dias}`, `presupuesto.
{tipo_presupuesto,moneda,presupuesto_estimado,monto_disponible,monto_disponible_clp}`, y el
bloque `orden_compra` (ver §8.5).

**Productos solicitados (`payload.productos_solicitados[]`):** `codigo_producto` (UNSPSC),
`nombre`, `descripcion`, `cantidad`, `unidad_medida` (ej. EA=unidad, KG=kilogramo).

**Proveedores cotizando (`payload.proveedores_cotizando[]`):** `rut_proveedor`, `razon_social`,
`es_emt` (Empresa de Menor Tamaño), `valor_neto`, `total_impuesto`, `monto_despacho`,
`monto_total`, y `productos_cotizados[].{codigo_producto,nombre_producto,cantidad,
precio_unitario,monto_total_producto}`. ➜ **Trae las cotizaciones de *todos* los proveedores,
no solo el ganador** — muy rico para el comparador de precios y para concentración.

### 8.5 Relación Compra Ágil ↔ Orden de Compra
- `orden_compra.id_orden_compra` (int|null): **indicador confiable** de que se emitió OC (≠ null).
- `orden_compra.codigo_orden_compra` (ej. `1057532-156-AG26`): ⚠️ en la práctica suele venir
  `null` aunque exista la OC → usar `id_orden_compra`.
- El estado `oc_emitida` no aparece en la práctica; para detectar OC emitidas, listar
  `estado=proveedor_seleccionado` y revisar `id_orden_compra` en el detalle (Ejemplo 8.6 de la guía).

### 8.6 Errores (HTTP)
`400` parámetros inválidos · `401` falta header `ticket` · `403` ticket inexistente/inactivo/
bloqueado · `404` código no existe · `429` cuota diaria agotada (esperar `Retry-After` / próximo
día calendario) · `500` error servidor · `503` servicio no disponible.

---

## 9. Tablas de códigos (validadas)

> Validadas contra los diccionarios oficiales. Donde la copia web (`api-mercadopublico-web-copia.md`)
> y los diccionarios PDF difieren, **manda el diccionario PDF** (se anota la discrepancia).

### 9.1 Estados de Orden de Compra
| Código | Estado | Nomenclatura (query `estado=`) |
|---|---|---|
| 4 | Enviada a Proveedor | `enviadaproveedor` |
| 5 | En proceso | — |
| 6 | Aceptada | `aceptada` |
| 9 | Cancelada | `cancelada` |
| 12 | Recepción Conforme | `recepcionconforme` |
| 13 | Pendiente de Recepcionar | `pendienterecepcion` |
| 14 | Recepcionada Parcialmente | `recepcionaceptadacialmente` *(sic)* |
| 15 | Recepción Conforme Incompleta | `recepecionconformeincompleta` *(sic)* |
| — | Todos | `todos` |

### 9.2 Estados de Licitación
| Código | Estado |
|---|---|
| 5 | Publicada |
| 6 | Cerrada |
| 7 | Desierta |
| 8 | Adjudicada |
| 18 | Revocada |
| 19 | Suspendida |

### 9.3 Tipo de Orden de Compra
| Código | Abrev. | Descripción |
|---|---|---|
| 1 | OC | Automática |
| 2 | D1 | Trato directo — proveedor único |
| 3 | C1 | Trato directo — emergencia/urgencia/imprevisto |
| 4 | F3 | Trato directo — confidencialidad |
| 5 | G1 | Trato directo — naturaleza de la negociación |
| 6 | R1 | Orden de compra menor a 3 UTM |
| 7 | CA | Orden de compra sin resolución |
| 8 | SE | Sin emisión automática |
| 9 | CM | **Convenio Marco** |
| 10 | FG | Trato Directo (Art. 8 letras f y g — Ley 19.886) |
| 11 | TL | Convenio Marco – Tienda de Libros (Obsoleto) |
| 12 | MC | Microcompra |
| 13 | AG | **Compra Ágil** |
| 14 | CC | Compra Coordinada |

### 9.4 Forma de Pago (Orden de Compra)
| Código | Descripción |
|---|---|
| 1 | 15 días contra la recepción de la factura |
| 2 | 30 días contra la recepción de la factura |
| 39 | Otra forma de pago |
| 46 | 50 días contra la recepción de la factura |
| 47 | 60 días contra la recepción de la factura |
| 48 | A 45 días *(solo en copia web; no en el diccionario PDF)* |
| 49 | A más de 30 días *(solo en copia web; no en el diccionario PDF)* |

### 9.5 Tipo de Licitación
| Valor | Descripción |
|---|---|
| L1 | Pública, menor a 100 UTM |
| LE | Pública, ≥100 y <1.000 UTM |
| LP | Pública, ≥1.000 y <2.000 UTM |
| LQ | Pública, ≥2.000 y <5.000 UTM |
| LR | Pública, ≥5.000 UTM |
| LS | Pública, servicios personales especializados |
| E2 | Privada, menor a 100 UTM |
| CO | Privada, ≥100 y <1.000 UTM |
| B2 | Privada, ≥1.000 y <2.000 UTM |
| H2 | Privada, ≥2.000 y <5.000 UTM |
| I2 | Privada, mayor a 5.000 UTM |

> **Nota histórica:** la copia web lista además tipologías antiguas (A1, B1, J1, F1, E1, D1, C2,
> C1, F2, F3, G2, G1, R1, CA, SE…) marcadas como *"tipologías que ya no existen"*. Pueden
> aparecer en **data histórica**; mapearlas como legacy si surgen.

### 9.6 Tipo de Despacho (Orden de Compra)
| Código | Descripción |
|---|---|
| 7 | Despachar a Dirección de envío |
| 9 | Despachar según programa adjuntado |
| 12 | Otra Forma de Despacho, Ver Instrucciones |
| 14 | Retiramos de su bodega |
| 20 | Despacho por courier o encomienda aérea |
| 21 | Despacho por courier o encomienda terrestre |
| 22 | A convenir |

### 9.7 Unidad Monetaria
| Valor | Descripción |
|---|---|
| CLP | Peso Chileno |
| CLF | Unidad de Fomento (UF) |
| USD | Dólar Americano |
| UTM | Unidad Tributaria Mensual |
| EUR | Euro |

### 9.8 Monto Estimado (Licitación)
| Valor | Descripción |
|---|---|
| 1 | Presupuesto Disponible |
| 2 | Precio Referencial |
| 3 | Monto no es posible de estimar |

### 9.9 Unidad de Tiempo (evaluación y duración de contrato)
| Valor | Descripción |
|---|---|
| 1 | Horas |
| 2 | Días |
| 3 | Semanas |
| 4 | Meses |
| 5 | Años |

### 9.10 Modalidad de Pago (Licitación)
| Valor | Descripción |
|---|---|
| 1 | Pago a 30 días |
| 2 | Pago a 30, 60 y 90 días |
| 3 | Pago al día |
| 4 | Pago Anual |
| 5 | Pago Bimensual |
| 6 | Pago Contra Entrega Conforme |
| 7 | Pagos Mensuales |
| 8 | Pago Por Estado de Avance |
| 9 | Pago Trimestral |
| 10 | Pago a 60 días |

> Discrepancia: la copia web ordena distinto algunos valores (p. ej. 5=Pago a 60 días). **Manda
> el diccionario de Licitaciones PDF**, que es el de arriba.

### 9.11 Tipo de Acto Administrativo que adjudica (Licitación)
| Valor | Descripción |
|---|---|
| 1 | Autorización |
| 2 | Resolución |
| 3 | Acuerdo |
| 4 | Decreto |
| 5 | Otros |

> Discrepancia: la copia web mostraba `3=Otros, 5=Acuerdo`. **Manda el diccionario PDF**
> (`3=Acuerdo, 5=Otros`).

### 9.12 Regiones (código → región)
| Cód. | Región | Cód. | Región |
|---|---|---|---|
| 1 | Tarapacá | 9 | Araucanía |
| 2 | Antofagasta | 10 | Los Lagos |
| 3 | Atacama | 11 | Aysén |
| 4 | Coquimbo | 12 | Magallanes y Antártica |
| 5 | Valparaíso | 13 | Metropolitana |
| 6 | O'Higgins | 14 | Los Ríos |
| 7 | Maule | 15 | Arica y Parinacota |
| 8 | Biobío | 16 | Ñuble |

### 9.13 Valores binarios (Licitación) — recordatorio de trampas
La mayoría son `1=Sí / 0=No`, **salvo excepciones** que invierten o cambian la semántica:
- `CodigoTipo`: `1=Pública`, `2=Privada`.
- `Obras`: `2=Sí`, `1=No` **(invertido respecto de lo habitual)**.
- `Contrato` (en OC/licitación): `1=Requiere subscripción`, `2=Formaliza con OC`.
- `ExtensionPlazo`: `1=Extiende`, `0=No extiende`.

---

## 10. Normalización de productos (UNSPSC)

El comparador (viz #1) y la fragmentación (H1) dependen de igualar "el mismo producto".

**Buena noticia (confirmada por los diccionarios):** los ítems traen `CodigoProducto` y
`CodigoCategoria` en el **estándar UNSPSC Versión 7** (codificación ONU de productos y
servicios). Es decir, hay un **ID estándar** para agrupar, no solo texto libre.

Estrategia (de menor a mayor esfuerzo):
1. **MVP — agrupar por `CodigoProducto` UNSPSC** (y/o empezar por **Convenio Marco**, con ID de
   catálogo estándar) → comparación directa y confiable.
2. **Agrupar por `CodigoCategoria`** para vistas más agregadas.
3. **Matching por descripción** (`EspecificacionComprador` / texto libre → fuzzy/embeddings)
   para afinar dentro de un mismo código. Fase 2.

**Reglas de oro:**
- No comparar precio unitario sin igualar **unidad de medida** (`UnidadMedida`) y especificación.
- El precio unitario **ya viene** en `PrecioNeto` (OC) / `MontoUnitario` (adjudicación de
  licitación) / `precio_unitario` (Compra Ágil). Si faltara, derivarlo de monto/cantidad y
  marcar como dudoso.
- UNSPSC agrupa "qué es", no "qué tan igual es": dos ítems con el mismo `CodigoProducto` pueden
  variar en especificación/calidad → usar la descripción para no comparar peras con manzanas.

---

## 11. Límites, validaciones y correcciones conocidas

**Correcciones incorporadas en esta consolidación (vs. el handoff original):**
1. **`PrecioNeto` = precio unitario.** No dividir por cantidad (§6). El total de línea se deriva
   `PrecioNeto × Cantidad`; el campo `Total` del ítem puede venir en `0.0` (dato sucio).
2. **Producto/categoría = UNSPSC v7** (§10): el problema de normalización es más manejable de lo
   que sugería el documento original.
3. **Compra Ágil SÍ es accesible** (§3, §8): vía OC tipo `AG` y vía API v2 dedicada. El caveat de
   H3 aplica **solo** si te limitas a las descargas OCDS.

**Límites de cobertura (decirlos en el dashboard):**
- **Empresas públicas excluidas** de la ley → todo total es "del universo Mercado Público", no
  "todo el gasto del Estado".
- **Compra Ágil ausente de OCDS** (pero recuperable por API).
- **Sin ficha completa en 1 request** (API v1): ingesta en dos pasos; planificar rate limiting y
  reintentos.
- **API v1 rate-limited** (10.000/día): no sirve para barrer histórico → usar descargas masivas.
- **Precio unitario / `Total` inconsistente:** validar, derivar y marcar outliers.
- **Convenio Marco como consolidación existente:** al medir fragmentación (H1), descontar lo ya
  agregado por convenio marco.
- **Binarios con semántica invertida** (§9.13): no asumir 1=Sí siempre.

---

## 12. Arquitectura sugerida

```
[Ingesta]   Python (requests + reintentos/backoff)
              ├─ carga histórica: descargas masivas / OCDS
              ├─ incremental diario v1: API por fecha (ticket en query)
              └─ Compra Ágil: API v2 (ticket en header, paginación)
                     ↓
[Storage]   DuckDB (MVP local) o Postgres (si multiusuario/persistente)
                     ↓
[Transform] dbt o SQL versionado: staging → normalización producto (UNSPSC) → marts
                     ↓
[Viz]       Web interactiva: Evidence/Streamlit (rápido) o Next.js (control fino, drill-down)
```

Notas:
- Guardar el **JSON crudo** de cada request (raw layer) → reproducibilidad y re-parseo sin re-pedir.
- Idempotencia por `codigo` → re-correr sin duplicar.
- Cachear en disco durante desarrollo para no gastar rate limit.
- Cada métrica agregada de la web debe poder "abrirse" hasta las filas que la componen.

---

## 13. Plan por fases

- **Fase 0 — Setup** *(en curso)*: repo, `.env`/`.env.example`/`.gitignore`, scripts que bajan
  1 día de OC y el detalle de una OC, guardando el JSON crudo. Validar el shape. ✅ shape validado.
- **Fase 1 — MVP comparador**: ingesta histórica acotada + comparación de precio por
  `CodigoProducto` UNSPSC (empezando por Convenio Marco) + viz "mismo producto, precio por
  organismo" con drill-down.
- **Fase 2 — Fragmentación (H1) y tipo de proceso (H3)**: procesos separados por rubro/organismo;
  tipo-de-proceso vs. monto; con los caveats de §11 visibles.
- **Fase 3 — Concentración de proveedores (viz #2)**: grafo comprador↔proveedor por RUT; "siempre
  gana"; trato directo vs. licitación.
- **Fase 4 — Silos tecnológicos (H2) + normalización avanzada**: rubros TI (UNSPSC); matching por
  descripción/embeddings.
- **Fase 5 — Pulido web**: filtros por comuna/rubro/fecha, notas de cobertura, export, narrativa.

---

## 14. Decisiones pendientes

- **Alcance temporal:** ¿últimos 12 meses o histórico completo? Impacta volumen/storage.
- **Stack de viz:** ¿rápido (Streamlit/Evidence) o control fino (Next.js)?
- **Storage:** ¿DuckDB local para el MVP o ya Postgres?
- **Alcance geográfico:** ¿nacional o foco en ciertas comunas/regiones para el MVP?
- **Formato entregable:** ¿web sola, o web + informe escrito?

---

## 15. Legal / ético

- Datos de compras públicas: **acceso público**, reutilización legítima (política de datos
  abiertos de ChileCompra). Si se publican sin modificar, **citar como fuente a la Dirección
  ChileCompra**.
- Respetar **términos de uso y rate limits** (10.000/día v1; cuota v2). El ticket es **personal**
  (un ticket por RUT); no compartirlo ni exponerlo.
- Cuidado al cruzar **RUT de personas naturales** con datos personales → Ley 19.628 y su reforma.
  Proveedores empresa: riesgo bajo; personas naturales: minimizar y agregar.
- **Imparcialidad:** el informe reporta lo que la data muestra, con contra-evidencia. No forzar
  una narrativa.

---

## 16. Enlaces y fuentes

**Oficiales:**
- Sitio API: <https://www.chilecompra.cl/api/>
- Documentación y ejemplos: <https://api.mercadopublico.cl/modules/api.aspx>
- Doc. licitación: <https://api.mercadopublico.cl/modules/Licitacion.aspx>
- Doc. orden de compra: <https://api.mercadopublico.cl/modules/OrdenCompra.aspx>
- Datos abiertos (descargas/OCDS): <https://datos-abiertos.chilecompra.cl/>
- Soporte: formulario de sugerencias del sitio (respuesta en ≤3 días hábiles).

**Fuentes conservadas para auditoría** (`docs/fuentes/`, sin modificar):
- `diccionario-datos-ordenes-de-compra.pdf` — diccionario oficial de OC.
- `diccionario-datos-licitaciones.pdf` — diccionario oficial de licitaciones.
- `guia-api-compra-agil-v3.0.pdf` — guía API Compra Ágil v2 (v3.0, la vigente).
- `guia-api-compra-agil-v2.x.pdf`, `guia-api-compra-agil-v2.0.pdf` — versiones previas (auditoría).
- `api-mercadopublico-web-copia.md` — copia de la web de la API (texto pegado por el usuario).
- `contexto-original-handoff.md` — documento de contexto/handoff original del proyecto.
