# 📊 Aplicación de Predicción de Ventas - Noviembre 2025

Simulador y visualizador interactivo de predicciones de ventas utilizando un modelo de Machine Learning (HistGradientBoosting) con predicciones recursivas que actualizan lags día a día.

## 🎯 Características

✅ **Dashboard interactivo** con Streamlit
✅ **Predicciones recursivas** que actualizan lags automáticamente
✅ **Controles en sidebar** para personalización
✅ **Visualizaciones profesionales** con Seaborn
✅ **Comparativa de escenarios** de competencia
✅ **Tabla detallada** con proyecciones diarias
✅ **Marcado de Black Friday** con anotaciones visuales
✅ **Testing completo** (26 tests de validación, tests unitarios del predictor)

## 📋 Requisitos

- Python 3.8+
- Virtualenv configurado en `.venv/`
- Modelo entrenado: `models/modelo_final_histgradientboosting.joblib`
- Dataset preparado: `data/Processed/df_inferencia_performence.csv`

## 🚀 Instalación

### 1. Clonar el proyecto
```bash
cd c:\ProjForestCastDataScience
```

### 2. Activar el ambiente virtual
```bash
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

## ▶️ Ejecución

### Validar entorno (opcional)
```bash
python validate_env.py
```

### Ejecutar la aplicación
```bash
streamlit run app/App.py
```

La aplicación se abrirá en `http://localhost:8501`

## 🧪 Testing

### Ejecutar todos los tests
```bash
python -m pytest tests/ -v
```

### Ejecutar solo tests de validación de datos
```bash
python -m pytest tests/test_data_validation.py -v
```

### Ejecutar solo tests del predictor
```bash
python -m pytest tests/test_predictor.py -v
```

### Generar reporte de cobertura
```bash
python -m pytest tests/ --cov=app --cov-report=html
```

## 📁 Estructura del Proyecto

```
ProjForestCastDataScience/
├── app/
│   ├── App.py                          # Aplicación principal Streamlit
│   ├── predictor.py                    # Lógica de predicciones recursivas
│   └── __init__.py
├── tests/
│   ├── test_data_validation.py        # Tests de validación de datos (26 tests)
│   ├── test_predictor.py              # Tests del predictor recursivo
│   └── __init__.py
├── data/
│   └── Processed/
│       └── df_inferencia_performence.csv  # Dataset noviembre 2025
├── models/
│   └── modelo_final_histgradientboosting.joblib  # Modelo ML
├── notebooks/
│   ├── Entrenamineto.ipynb
│   └── forecasting.ipynb
├── requirements.txt                    # Dependencias
├── validate_env.py                     # Validador de entorno
├── run_tests.py                        # Runner de tests
└── README.md                           # Este archivo
```

## 🎮 Controles de la Aplicación

### Sidebar - Controles de Simulación

1. **Selector de Producto** (dropdown)
   - Elige entre 24 productos disponibles
   
2. **Slider de Descuento** (-50% a +50%)
   - Ajusta el descuento sobre el precio base
   - Pasos de 5%
   
3. **Escenario de Competencia** (radio buttons)
   - **Actual (0%)**: Precios de competencia actuales
   - **Competencia -5%**: Competencia reduce precio un 5%
   - **Competencia +5%**: Competencia aumenta precio un 5%
   
4. **Botón "Simular Ventas"**
   - Ejecuta predicciones recursivas para los 30 días

### Dashboard Principal

**KPIs Destacados:**
- 📦 Unidades Totales Proyectadas
- 💵 Ingresos Proyectados
- 🏷️ Precio Promedio de Venta
- 📉 Descuento Promedio

**Gráfico de Predicción:**
- Línea de predicción diaria (1-30 de noviembre)
- Marcado especial de Black Friday (día 28)
- Punto rojo destacado y anotación

**Tabla Detallada:**
- Fecha y día de la semana
- Precio de venta y precio competencia
- Descuento aplicado
- Unidades predichas
- Ingresos proyectados por día
- Destaque visual del Black Friday

**Comparativa de Escenarios:**
- Tarjetas con comparación de 3 escenarios
- Mantiene el descuento del usuario, solo varía competencia

## 🔧 Lógica de Predicción Recursiva

### Día 1 (1 de noviembre)
- Usa lags iniciales que ya están en el CSV (calculados desde octubre)
- Realiza la primera predicción

### Días 2-30
- Actualiza `lag_1` ← predicción del día anterior
- Desplaza lags: `lag_2 ← lag_1_anterior`, `lag_3 ← lag_2_anterior`, etc.
- Actualiza `media_movil_7` con promedio de últimas 7 predicciones
- Predice el día con los lags actualizados

### Ajustes de Usuario
- **Descuento**: Recalcula `precio_venta = precio_base * (1 - descuento%)`
- **Competencia**: Ajusta `precio_competencia` según escenario
- **Ratio de precio**: Recalcula `precio_venta / precio_competencia`

## 🧪 Suite de Tests

### Tests de Validación de Datos (26 tests)

Valida que el dataset tiene:
- ✓ 720 filas (24 productos × 30 días)
- ✓ 81 columnas correctas
- ✓ Fechas de noviembre 2025
- ✓ Lags (lag_1 a lag_7)
- ✓ Media móvil (media_movil_7)
- ✓ Columnas de precio
- ✓ One-hot encoding correcto
- ✓ Black Friday marcado en día 28
- ✓ Sin nulos en columnas críticas
- ✓ Precios positivos
- ✓ Consistencia de cálculos

### Tests del Predictor Recursivo

Valida que:
- ✓ Predictor se inicializa correctamente
- ✓ Retorna dataframe válido con 30 días
- ✓ Todas las predicciones son positivas
- ✓ Ingresos = unidades × precio_venta
- ✓ Descuentos se aplican correctamente
- ✓ Lags se desplazan correctamente
- ✓ Escenarios de competencia funcionan
- ✓ Totales calculados correctamente

## 📊 Ejemplo de Uso

1. **Abrir la aplicación**
   ```bash
   streamlit run app/App.py
   ```

2. **Configurar parámetros en sidebar:**
   - Seleccionar: "Nike Air Zoom Pegasus 40"
   - Descuento: 10%
   - Escenario: "Actual (0%)"

3. **Hacer clic en "Simular Ventas"**

4. **Ver resultados:**
   - KPIs con proyecciones
   - Gráfico de tendencia diaria
   - Tabla detallada
   - Comparativa de escenarios

## 🛠️ Troubleshooting

### Error: "Modelo no encontrado"
```
Verifica que existe: models/modelo_final_histgradientboosting.joblib
```

### Error: "Dataset no encontrado"
```
Verifica que existe: data/Processed/df_inferencia_performence.csv
```

### Error: "Streamlit no está instalado"
```bash
pip install streamlit
```

### La app se congela durante predicción
```
Esto es normal para productos con muchas variaciones.
Las predicciones recursivas pueden tardar 5-10 segundos.
```

## 📝 Notas Técnicas

- **Columnas de lag**: `lag_1`, `lag_2`, ..., `lag_7` (sin prefijo "unidades_vendidas_")
- **Media móvil**: `media_movil_7` (no `unidades_vendidas_ma7`)
- **Target**: El modelo predice unidades_vendidas
- **Features**: 70 features incluyendo OHE para nombre, categoría y subcategoría
- **Validación**: Todos los tests pasan (26/26 validación + predictor tests)

## 🎨 Diseño Visual

- **Paleta de colores**: Morado/Azul (#667eea, #764ba2, #f093fb)
- **Framework**: Streamlit con CSS personalizado
- **Gráficos**: Seaborn sobre Matplotlib
- **Layout**: Responsivo, optimizado para desktop y tablets

## 📞 Soporte

Para reportar errores o sugerencias, revisa:
1. Los logs de la aplicación en la terminal
2. Los resultados de `python validate_env.py`
3. Los tests con `python -m pytest tests/ -v`

## 📄 Licencia

Proyecto de predicción de ventas con ML - 2025

---

**Última actualización**: Noviembre 2025
**Versión**: 1.0.0
**Status**: ✅ Producción
