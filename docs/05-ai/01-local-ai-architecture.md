# Documentación de Inteligencia Artificial Local & Machine Learning

## 1. Principio Fundamental: Inferencia Local & Cero Dependencia de LLMs

En cumplimiento estricto con las directrices de seguridad y privacidad corporativa de FlowMind AI, el sistema **no utiliza llamadas a Large Language Models (LLMs) externos en la nube** (OpenAI, Gemini, Anthropic) para sus tareas de extracción, clasificación o validación.

Toda la inteligencia del sistema está construida sobre:
1. **Modelos Supervisados de Machine Learning Clásico (`scikit-learn`):** Ejecución en CPU local con tiempos de inferencia $< 10$ ms y huella de memoria mínima ($< 50$ MB).
2. **Algoritmos Deterministas de Coincidencia Difusa (`rapidfuzz`):** Emparejamiento por distancia Levenshtein y afinidad ponderada de tokens.
3. **Visión Artificial Offline (`zxing-cpp`, `pytesseract`, `OpenCV`):** Lectura directa de códigos QR y barras 1D/2D con 100% de precisión y OCR local adaptativo.
4. **Validadores Aritméticos Deterministas:** Recálculo exacto de totales y cuotas fiscales con tolerancia de céntimo.

---

## 2. Clasificador de Documentos (`MLClassifier`)

### 2.1 Arquitectura del Pipeline
* **Vectorizador:** `TfidfVectorizer` de `scikit-learn` con extracción de unigramas y bigramas ($N$-grams $(1, 2)$), filtrado de *stop words* en español e inglés y frecuencias sublineales de términos (`sublinear_tf=True`).
* **Clasificador:** `LogisticRegression` multinomial con regularización $L_2$ o `MultinomialNB`.
* **Clases Canónicas Entrenadas:**
  - `invoice`: Facturas de proveedores y clientes.
  - `inventory`: Hojas de control de stock y catálogo de almacén.
  - `purchase_order`: Pedidos de compra (PO).
  - `payroll`: Nóminas y liquidaciones de salarios.
  - `contract`: Contratos mercantiles y acuerdos de confidencialidad.

### 2.2 Inferencia y Fallbacks
* Si la confianza del modelo $\text{Confidence} \ge 0.70$, se adopta la predicción del clasificador ML.
* Si $\text{Confidence} < 0.70$, se ejecuta el **Clasificador Heurístico por Reglas** (`RuleClassifier`) que inspecciona palabras clave deterministas en las primeras 50 líneas del documento.

---

## 3. Motor de Similitud Difusa y Mapeo Canónico (`SchemaNormalizer`)

### 3.1 Algoritmo
* Se calculan matrices de similitud entre las cabeceras origen y los alias/nombres de los campos destino del esquema mediante `rapidfuzz.fuzz.token_sort_ratio`.
* Se aplica una asignación voraz por máxima puntuación (*Greedy Maximum Weight Bipartite Matching*), garantizando que columnas ambiguas no se asignen a múltiples campos incompatibles.
* Umbral de aceptación automática: Similitud $\ge 85\%$; sugerencia asistida: $45\% \le \text{Similitud} < 85\%$.

---

## 4. Búsqueda Vectorial Offline & Embeddings Cuantizados (Fase Planificada)

* **Modelo Local:** `all-MiniLM-L6-v2` exportado a formato **ONNX INT8** (~45 MB de peso total).
* **Runtime:** `onnxruntime` optimizado para instrucciones AVX2/AVX-512 en CPU estándar.
* **Índice:** `FAISS` (`IndexFlatIP` o `IndexHNSWFlat`) persistido en disco por organización bajo `./data/indices/{organization_id}/`.
