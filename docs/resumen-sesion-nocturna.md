# Resumen de la sesión nocturna — para leer en la mañana

> Trabajé de forma autónoma según tus instrucciones: eficientar la API, hacer que el HTML
> entregue valor (no solo números), seguir anotando discrepancias, avanzar fases y dejarte
> este resumen. Todo está commiteado y pusheado a la rama `claude/compras-publicas-setup-pq1s4l`.
> **No necesitas correr nada para revisar** — solo abrir el visual y leer.

---

## 1. TL;DR (lo esencial en 5 puntos)

1. **Visual interactivo listo y publicado** → el comparador de precios ahora abre con
   **"Lo que más llama la atención"**, ordena por **lo que más vale investigar** (dispersión ×
   confiabilidad), muestra chips de confiabilidad e interpreta en palabras. Link abajo (§3).
2. **La API ya es eficiente**: ritmo adaptativo (AIMD) que se auto-ajusta al límite de ráfaga +
   contador de cuota diaria persistente. Las próximas descargas serán menos lentas y no gastarás
   la cuota a ciegas.
3. **Descubrimiento clave sobre el rate limit**: lo que te frenaba **no** era el tope de 10.000/día,
   sino un **límite de ráfaga** de la API. Para volumen histórico real, el camino correcto es
   **descargas masivas OCDS**, no la API detalle-a-detalle.
4. **Avancé Fase 2**: medí la fragmentación (H1) — 291 productos comprados por 5+ organismos por
   separado — y el cruce tipo-de-proceso × monto (H3 parcial). Con caveats. Ver `docs/hallazgos-fase2.md`.
5. **16 discrepancias anotadas** (agregué D13–D16 esta noche). Ver `docs/discrepancias-fuentes.md`.

---

## 2. Qué hice, punto por punto (tus 5 encargos)

### ✅ Eficientar las llamadas a la API
- **`quota.py`**: contador de cuota diaria (10.000/día) que **persiste en disco**. El descargador
  respeta el tope entre corridas y sesiones; si se agota, corta y avisa "sigue mañana" (es idempotente).
- **Ritmo adaptativo AIMD** en `download_lote_detalles`: la pausa entre llamadas **sube cuando hay
  429** y **baja cuando va limpio**, convergiendo al ritmo más rápido que la API tolera. Antes usabas
  una pausa fija (lenta o agresiva); ahora se auto-tunea.
- **`api_client`** ahora honra `Retry-After` y reporta los 429 para alimentar el AIMD.
- **Por qué NO concurrencia**: el límite es del servidor (ráfaga), no de latencia del cliente →
  paralelizar solo causaría más 429. Documentado.
- **La respuesta de fondo a la eficiencia**: para el histórico masivo, usar **descargas OCDS**
  (`datos-abiertos.chilecompra.cl`), no barrer la API. Está señalado como el próximo gran paso.

### ✅ HTML que entregue valor de entrada (no solo números)
- Sección **"Lo que más llama la atención"**: los 3 productos de alta confiabilidad con mayor brecha.
- **Orden por defecto = "más vale investigar"**: combina dispersión de precio **y** confiabilidad
  (nº de organismos y de compras). Justo lo que pediste.
- **Chips de confiabilidad** (alta/media/baja) por producto.
- **Interpretación en palabras**: "11 organismos lo compraron. La mitad pagó entre $370 y $1.990 —
  una brecha de 5,4× por lo mismo."
- **Credibilidad**: los titulares usan comparación **robusta** (p25–p75), no el máx/mín que estaba
  inflado por outliers de unidad de medida. Antes decía "27.675×" (falso); ahora dice la brecha real.
- Filtro "solo confiabilidad alta/media", buscador, y clic en un hallazgo te lleva a su drill-down.

### ✅ Seguir anotando discrepancias
- Agregué **D13** (Convenio Marco no trae CodigoProducto → 98% en 0), **D14** (el listado por día
  abarca OC de 2019–2024), **D15** (precio bajo se correlaciona con cantidades grandes = descuento
  por volumen), **D16** (el límite que muerde es la ráfaga, no el tope diario).

### ✅ Avanzar las fases que alcancé
- **Fase 2 (H1 y H3 parcial)**: `analisis_fragmentacion.py` + `docs/hallazgos-fase2.md`.

### ✅ Este resumen.

---

## 3. El visual (ábrelo primero)

**Link:** https://claude.ai/code/artifact/08339fd7-013c-417a-944a-535c8ac8c10c

También está en el repo: `docs/visual/comparador-precios.html` (autocontenido, se abre con doble clic).

**Qué verás:** 50 productos comparados, ordenados por lo que más vale investigar. Arriba, los 3
hallazgos más llamativos. Cada fila: nombre, chip de confiabilidad, una frase que explica la
brecha, una franja con los precios de cada organismo (escala log), y la mediana + dispersión.
**Clic en cualquier fila** abre el detalle hasta la orden de compra concreta (organismo, comuna,
precio, cantidad, tipo, fecha, código de OC, proveedor). Tiene tema claro/oscuro.

---

## 4. Hallazgos con la data real (4 días ≈ 18.711 ítems, 296 organismos)

**Comparador (commodities con mayor brecha, alta confiabilidad):**
- **Artículos de papelería** — 11 organismos, la mitad pagó entre $370 y $1.990 (5,4×).
- **Toallas de papel** — 18 organismos, 4,8×.
- **Computadores de escritorio** — 14 organismos, 5,1×.
- **Pilas alcalinas, extintores, vendas de gasa** — todos con dispersión alta y varios compradores.

**Fragmentación (H1):** 291 productos comprados por 5+ organismos por separado. Los más
fragmentados: servicios de limpieza (39 organismos), exámenes médicos (34), vigilancia (31),
verduras frescas (24, en 522 líneas).

**Tipo de proceso (H3 parcial):** Compra Ágil tiene la mediana de monto más baja ($116k), coherente
con su diseño para montos chicos.

**⚠️ Todo esto es "señal para investigar", con caveats reales** (ver §5): falta la unidad de medida,
hay descuento por volumen mezclado, y falta descontar Convenio Marco.

---

## 5. Los caveats que hay que tener presentes (no ignorar)

1. **Sin unidad de medida** (D11): la API de OC no la informa → parte de la dispersión es envase/lote.
2. **Descuento por volumen** (D15): quien compra 1.000 unidades paga menos por unidad. No es
   necesariamente sobreprecio.
3. **Convenio Marco no trae código de producto** (D13): por eso el comparador se basa en el universo
   general (SE/AG), no en CM. Y al medir fragmentación falta restar lo ya consolidado por CM.
4. **Rango temporal 2019–2024** (D14): mayoría 2024, pero hay inflación mezclada en la cola.
5. **Cobertura parcial**: es una muestra, no todo el gasto del Estado; empresas públicas excluidas.

---

## 6. Estado del repositorio (rama `claude/compras-publicas-setup-pq1s4l`)

```
docs/
  mercado-publico-referencia.md     ← referencia única (APIs, diccionarios, códigos)
  discrepancias-fuentes.md          ← 16 discrepancias con estado y checklist
  hallazgos-fase2.md                ← fragmentación H1 + tipo/monto H3 (nuevo)
  resumen-sesion-nocturna.md        ← este archivo
  visual/comparador-precios.html    ← el visual (deliverable)
  visual/_plantilla.html            ← plantilla del visual
  fuentes/                          ← PDFs oficiales (auditoría)
src/mercadopublico/
  config, api_client, quota         ← infra (entorno, HTTP+AIMD, cuota)
  download_ordenes_dia / _detalle_oc / _lote_detalles   ← ingesta
  parse_items, comparador, scoring, preparar_viz        ← Fase 1
  analisis_fragmentacion            ← Fase 2
bajar_*.py / parsear_items.py / comparar_precios.py / construir_visual.py   ← atajos
data/ (raw|interim|processed)       ← datos (algunos versionados a la fuerza)
```

---

## 7. Lo que puedes hacer cuando quieras (opcional, no urgente)

**Nada es bloqueante.** Si quieres más volumen/robustez, cuando tengas la máquina:

```
git pull origin claude/compras-publicas-setup-pq1s4l
py bajar_lote.py --fecha 2024-03-11 --limit 1500   # otro día; el AIMD lo hace más fluido
py parsear_items.py
py -m mercadopublico.preparar_viz
py construir_visual.py                              # reconstruye el HTML
```
El descargador ahora respeta la cuota y se auto-ritma. Igual, para histórico grande, lo eficiente
de verdad es bajar los **archivos masivos OCDS** — lo dejamos como próximo paso.

---

## 8. Decisiones abiertas para conversar (cuando estés)

1. **¿Clasificar por rubro** (aseo / alimentos / TI / insumos médicos) para comparaciones más
   precisas? Dijiste que sí más adelante — sería el siguiente salto de calidad del comparador.
2. **¿Incorporar la cantidad** al comparador para separar descuento por volumen de sobreprecio (D15)?
3. **¿Traer licitaciones** (API/OCDS) para el H3 real (proceso pesado vs monto)?
4. **¿Ir por descargas OCDS masivas** para tener histórico de verdad en vez de muestras por día?
5. **Stack de la web final**: el prototipo actual es HTML autocontenido; si crece, evaluar
   Streamlit/Evidence o Next.js (§ del maestro).

Mi recomendación para el próximo bloque: **(2) + (1)** — meter cantidad y una clasificación por
rubro hace el comparador mucho más creíble y navegable, sin depender de más descargas.

---

*Todo pusheado. Que descanses — mañana seguimos con lo que prefieras de la §8.*
