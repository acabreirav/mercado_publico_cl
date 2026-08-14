# Contexto del proyecto — Compras públicas de Chile (Mercado Público / ChileCompra)

> Documento de **contexto/handoff**. Léelo primero para orientarte antes de escribir código.
> No es un `CLAUDE.md`: ese se genera después (`/init`), corto y estable, con comandos y convenciones.
> Este archivo es la fuente de verdad sobre **qué construimos, de dónde sale la data y las trampas conocidas.**

---

## 1. Objetivo

Construir un pipeline de ingesta + un **informe / web interactiva** sobre las compras del Estado chileno,
apuntando a análisis que **hoy casi nadie hace bien**. El foco NO es "cuánto gasta el Estado" (eso ya existe),
sino evidencia navegable que un ciudadano pueda explorar.

**Diferenciador:** ya hay gente publicando *conclusiones* sobre estos problemas (ver §2), pero sin mostrar la data.
Nuestro valor es lo contrario: **cada afirmación respaldada por evidencia con drill-down** hasta las licitaciones
concretas. La web interactiva es el entregable estrella, no un PDF con gráficos estáticos.

Visualizaciones núcleo:

1. **Comparador de precios**: el mismo producto pagado a precios distintos entre organismos/comunas → sobreprecios.
2. **Concentración de proveedores**: quién "siempre gana" en cierta repartición/comuna; grafo comprador↔proveedor.
3. **Fragmentación y tipo de proceso**: cuánto se licita por separado que podría consolidarse; proceso pesado vs. monto.

Prioridad: MVP con #1 y una versión medible de #3 (ver hipótesis abajo).

---

## 2. Hipótesis a validar (derivadas de análisis público existente)

Circulan análisis (LinkedIn, prensa) que afirman que Mercado Público está "roto". Los tratamos como
**hipótesis testeables, no como verdades**. El proyecto las verifica con data y reporta lo que la data muestre,
**incluida la contra-evidencia**. Objetivo: un informe imparcial y reproducible, no un panfleto.

### H1 — Micro-fragmentación
*Tesis:* cientos de escuelas/hospitales/municipios licitan por separado los mismos insumos cotidianos en vez de consolidar demanda.
- **Cómo medirlo:** para una categoría commodity (útiles, agua, carpas, etc.), contar procesos distintos por N organismos en una ventana; % de procesos bajo cierto umbral de monto; mapa de "cuántas unidades compran el mismo rubro por separado".
- **Contra-evidencia a chequear:** parte de esa demanda **ya está consolidada vía Convenio Marco** → hay que descontar lo agregado antes de gritar fragmentación.

### H2 — Silos tecnológicos
*Tesis:* servidores, parches de software y sitios web se licitan pieza por pieza, ignorando infraestructura centralizada.
- **Cómo medirlo:** filtrar rubros TI (códigos de categoría de tecnología); contar contratos pequeños/aislados; dispersión de proveedores y montos por organismo.
- **Contra-evidencia a chequear:** parte puede estar bajo convenios marco de tecnología; distinguir compra genuinamente aislada de la que sigue un estándar central.

### H3 — Proceso pesado para compras triviales
*Tesis:* se usa el proceso de licitación completo (largo, formal) para comprar cosas de bajo monto.
- **Cómo medirlo:** cruzar **tipo de proceso** (licitación L1/LE/LP vs. trato directo vs. convenio marco vs. compra ágil) contra **monto**; destacar licitaciones completas de montos bajos.
- **CAVEAT CRÍTICO:** **Compra Ágil** —el mecanismo liviano diseñado justo para montos bajos— **no está en el dataset OCDS** (ver §6). Su ausencia puede hacer que la data **sobreestime** este problema. Hay que decirlo explícito en el informe.
- **Ojo con supuestos:** "horas-hombre desperdiciadas" NO está en la data; es una estimación con supuestos. Si se muestra, etiquetar como *modelo*, no como *dato*.

**Regla editorial:** toda conclusión fuerte va acompañada del dato que la sostiene y del que la matiza. El drill-down es la prueba.

---

## 3. Fuentes de datos — dos caminos, se usan ambos

### 3.1 API REST en tiempo real — `api.mercadopublico.cl`
Buena para: datos frescos, un proceso puntual, el día actual.
Mala para: histórico masivo (rate-limited, orientada a consultas por día/código).

- **Base:** `https://api.mercadopublico.cl/servicios/v1/publico/`
- **Formatos:** `.json`, `.jsonp`, `.xml`
- **Auth:** parámetro `&ticket=<TICKET>` en cada request.
- **Formato de fecha:** `ddmmaaaa` sin separadores (ej. `02022014`)
- **Soporte:** `API@chilecompra.cl`

#### Manejo del ticket (SECRETO — leer)
El ticket es una credencial de solo lectura sobre datos públicos, pero se trata como secreto:
- Va en un archivo **`.env`** en la raíz del repo, con una entrada tipo `MERCADO_PUBLICO_TICKET=...`
- **`.env` va en `.gitignore`.** Nunca commitear el ticket. Nunca hardcodearlo en el código.
- El código lo lee del entorno (`os.environ` / `python-dotenv`), no de este documento.
- Dejar un `.env.example` (sin el valor real) para documentar qué variables se necesitan.
- Ticket de **prueba** público (solo pruebas, no para producción): `F8537A18-6766-4DEF-9E59-426B4FEE2844`

**Endpoints clave (ejemplos reales):**

```
# Licitaciones del día actual (todos los estados)
GET /servicios/v1/publico/licitaciones.json?ticket=<TICKET>

# Licitaciones de una fecha específica
GET /servicios/v1/publico/licitaciones.json?fecha=02022014&ticket=<TICKET>

# Licitación por código
GET /servicios/v1/publico/licitaciones.json?codigo=1509-5-L114&ticket=<TICKET>

# Órdenes de compra de una fecha
GET /servicios/v1/publico/ordenesdecompra.json?fecha=02022014&ticket=<TICKET>

# Orden de compra por código
GET /servicios/v1/publico/ordenesdecompra.json?codigo=2097-241-SE14&ticket=<TICKET>

# Órdenes de compra por estado (día actual)
GET /servicios/v1/publico/ordenesdecompra.json?estado=todos&ticket=<TICKET>

# Buscar proveedor por RUT (con puntos, guión y DV)
GET /servicios/v1/publico/Publico/Empresas/BuscarProveedor?rutempresaproveedor=70.017.820-k&ticket=<TICKET>
```

**Patrón típico:** la consulta "por día" devuelve un listado con códigos; el detalle se pide por `codigo`.
**No existe un método que devuelva la ficha completa de una licitación en una sola llamada** → ingesta en dos pasos
(listar por día → iterar detalles). Documentación: `https://api.mercadopublico.cl/modules/api.aspx`

### 3.2 Descargas masivas + OCDS — `datos-abiertos.chilecompra.cl`
Buena para: **histórico y masivo** (el 90% del proyecto). Es el camino correcto para poblar la base la primera vez.

- **Procesos OCDS:** `https://datos-abiertos.chilecompra.cl/descargas/procesos-ocds`
- **Descargas masivas OC y licitaciones:** `https://datos-abiertos.chilecompra.cl/descargas/ordenes-y-licitaciones`

**Estrategia:** cargar histórico desde descargas masivas/OCDS → mantener al día con la API por incrementales.
No reconstruir el histórico llamando la API día por día.

---

## 4. Modelo de datos (entidades clave)

```
Organismo comprador ──< Licitación ──< Adjudicación ──< Orden de Compra ──< Ítem (línea)
                                                              │                    │
                                                         Proveedor (RUT)      Producto/Rubro
```

- **Licitación:** tipo por monto — `L1` (<100 UTM), `LE` (100–1000 UTM), `LP` (>1000 UTM). Estados: publicada, cerrada, desierta, adjudicada, revocada, suspendida.
- **Orden de Compra:** el gasto efectivo. Código tipo `2097-241-SE14`.
- **Ítem / línea:** `producto`, `cantidad`, `precio unitario`, `código de categoría`. **Corazón del comparador de precios.**
- **Proveedor:** identificado por **RUT** → grafos de concentración (limpio y confiable).
- **Organismo comprador:** repartición/comuna → comparación de precios entre entidades y análisis de fragmentación.

Codificaciones a mapear: unidad monetaria (CLP/USD/UTM), modalidad de pago, monto estimado (1=presupuesto, 2=referencial), binarios 1/0.

---

## 5. El problema difícil: normalización de productos

El comparador (viz #1) y la fragmentación (H1) dependen de esto. **"El mismo producto" no viene con ID limpio:**
descripciones en **texto libre** que varían entre organismos ("Resma papel A4 75gr" vs "PAPEL FOTOCOPIA CARTA").

Estrategia (de menor a mayor esfuerzo):
1. **MVP — empezar por Convenio Marco:** ítems con ID de catálogo estándar → comparación directa y confiable. Vía más rápida a una viz creíble.
2. **Agrupar por código de categoría/rubro** antes de comparar.
3. **Matching por descripción** (normalización de texto → fuzzy/embeddings). Fase 2.

**Regla de oro:** no comparar precio unitario sin igualar unidad de medida y especificación. Si el precio unitario no viene, derivarlo de monto/cantidad y marcar dudosos.

---

## 6. Límites y validaciones conocidas (LEER antes de prometer una viz o conclusión)

- **Cobertura no total:** las **empresas públicas están excluidas** de la ley, y **"Compra Ágil" no se publica en la API OCDS**. Todo total es "del universo Mercado Público OCDS", no "todo el gasto del Estado". Decirlo en el dashboard.
- **Compra Ágil ausente sesga H3** (proceso pesado para compras chicas): el mecanismo liviano no aparece → cuidado con sobre-concluir.
- **Sin ficha completa en 1 request:** ingesta en dos pasos; planificar rate limiting y reintentos.
- **API rate-limited:** no es para barrer histórico → usar descargas masivas/OCDS.
- **Normalización de producto = principal riesgo de proyecto** (§5).
- **Precio unitario inconsistente:** validar/derivar y marcar outliers.
- **Convenio Marco como consolidación existente:** al medir fragmentación (H1), descontar lo ya agregado por convenio marco.

---

## 7. Arquitectura sugerida (decisión abierta — ver §9)

```
[Ingesta]   Python (httpx/requests + tenacity para reintentos)
              ├─ carga histórica: descargas masivas / OCDS
              └─ incremental diario: API por fecha (ticket desde .env)
                     ↓
[Storage]   DuckDB (MVP local) o Postgres (si multiusuario/persistente)
                     ↓
[Transform] dbt o SQL versionado: staging → normalización producto → marts (precio, concentración, fragmentación)
                     ↓
[Viz]       Web interactiva. Opciones: Evidence/Streamlit (rápido) o Next.js + lib de charts (más control y mejor para drill-down)
```

Notas:
- Guardar el **JSON crudo** de cada request (raw layer) → reproducibilidad y re-parseo sin re-pedir.
- Idempotencia por `codigo` → re-correr sin duplicar.
- Cachear en disco durante desarrollo para no gastar rate limit.
- Para el drill-down de la web, cada métrica agregada debe poder "abrirse" hasta las filas de licitación que la componen.

---

## 8. Plan por fases

- **Fase 0 — Setup:** repo, `.env` con ticket real (+ `.env.example`), `.gitignore`. Script que baje 1 día de OC y lo guarde crudo. Validar shape del JSON.
- **Fase 1 — MVP comparador (Convenio Marco):** ingesta histórica acotada + comparación de precio de ítems con ID de catálogo + viz "mismo producto, precio por organismo" con drill-down.
- **Fase 2 — Fragmentación (H1) y tipo de proceso (H3):** métricas de procesos separados por rubro/organismo; cruce tipo-de-proceso vs. monto; con los caveats de §6 visibles.
- **Fase 3 — Concentración de proveedores (viz #2):** grafo comprador↔proveedor por RUT; ranking de "siempre gana"; trato directo vs. licitación.
- **Fase 4 — Silos tecnológicos (H2) + normalización avanzada:** rubros TI; matching por descripción/embeddings.
- **Fase 5 — Pulido web:** filtros por comuna/rubro/fecha, notas de cobertura, export, narrativa del informe.

---

## 9. Decisiones pendientes (definir antes de codear en firme)

- **Alcance temporal:** ¿últimos 12 meses o histórico completo? Impacta volumen y storage.
- **Stack de viz:** ¿rápido (Streamlit/Evidence) o con control fino y buen drill-down (Next.js)?
- **Storage:** ¿DuckDB local para el MVP o ya Postgres?
- **Alcance geográfico:** ¿nacional o foco en ciertas comunas/regiones para el MVP?
- **Formato entregable:** ¿web interactiva sola, o web + informe escrito que la acompañe?

---

## 10. Legal / ético (breve)

- Datos de compras públicas: **acceso público**, reutilización legítima (política de datos abiertos de ChileCompra).
- Respetar **términos de uso y rate limits** de la API.
- Cuidado al cruzar **RUT de personas naturales** con datos personales → Ley 19.628 y su reforma. Proveedores empresa: riesgo bajo; personas naturales: minimizar y agregar.
- **Imparcialidad:** el informe reporta lo que la data muestra, con contra-evidencia. No forzar una narrativa.

---

## 11. Enlaces de referencia

- Sitio API: https://www.chilecompra.cl/api/
- Documentación y ejemplos: https://api.mercadopublico.cl/modules/api.aspx
- Datos abiertos (descargas/OCDS): https://datos-abiertos.chilecompra.cl/
- Soporte: API@chilecompra.cl
