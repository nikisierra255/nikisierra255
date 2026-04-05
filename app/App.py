"""
Aplicación Streamlit para simulación y predicción de ventas de noviembre 2025.
Interfaz moderna y funcional con dashboard interactivo.
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
from app.predictor import RecursivePredictor, compare_scenarios

warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="🚀 Sales Forecast Nov 2025",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 2.5em;
        color: #667eea;
        margin-bottom: 0.5em;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5em;
        border-radius: 0.5em;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        margin: 0.3em 0;
    }
    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    .section-divider {
        border-top: 2px solid #667eea;
        margin: 2em 0 1.5em 0;
    }
    .black-friday {
        background-color: #FFE5E5;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model_and_data():
    """Carga el modelo y datos (caché para evitar recargar)."""
    try:
        model = joblib.load('models/modelo_final_histgradientboosting.joblib')
        df = pd.read_csv('data/Processed/df_inferencia_performence.csv')
        return model, df
    except Exception as e:
        st.error(f"❌ Error cargando modelo o datos: {e}")
        st.stop()


def main():
    """Función principal de la aplicación."""
    model, df = load_model_and_data()
    
    # SIDEBAR - CONTROLES DE SIMULACIÓN
    with st.sidebar:
        st.markdown("### 🎮 Controles de Simulación")
        st.markdown("---")
        
        # Selector de producto
        products = sorted(df['nombre'].unique().tolist())
        selected_product = st.selectbox(
            "📦 Selecciona un producto:",
            products,
            help="Elige el producto para simular ventas"
        )
        
        # Slider de descuento
        discount = st.slider(
            "💰 Ajuste de descuento:",
            min_value=-50,
            max_value=50,
            value=0,
            step=5,
            format="%d%%",
            help="Rango de -50% a +50% sobre precio base"
        )
        
        # Selector de escenario de competencia
        st.markdown("**🏆 Escenario de Competencia:**")
        scenario_map = {
            "Actual (0%)": "actual",
            "Competencia -5%": "competitive_minus5",
            "Competencia +5%": "competitive_plus5"
        }
        scenario = st.radio(
            "Elige escenario:",
            list(scenario_map.keys()),
            label_visibility="collapsed",
            help="Cómo afecta la competencia al precio"
        )
        
        st.markdown("---")
        
        # Botón de simulación
        simulate_button = st.button(
            "🚀 Simular Ventas",
            use_container_width=True,
            type="primary"
        )
    
    # ZONA PRINCIPAL - DASHBOARD
    st.markdown(
        f"<div class='main-title'>📈 Simulación de Ventas - Noviembre 2025</div>",
        unsafe_allow_html=True
    )
    
    product_info = df[df['nombre'] == selected_product].iloc[0]
    st.markdown(
        f"<div style='text-align:center; font-size:1.2em; color:#666; margin-bottom:1em;'>"
        f"<strong>{selected_product}</strong> | {product_info['categoria']} → {product_info['subcategoria']}"
        f"</div>",
        unsafe_allow_html=True
    )
    
    if simulate_button:
        with st.spinner("⏳ Realizando predicciones recursivas..."):
            try:
                predictor = RecursivePredictor(
                    model, df, model.feature_names_in_
                )
                df_predictions, summary = predictor.predict_november(
                    selected_product,
                    discount,
                    scenario_map[scenario]
                )
                
                # KPIs DESTACADOS
                st.markdown(
                    "<div class='section-divider'></div>",
                    unsafe_allow_html=True
                )
                st.markdown("### 📊 KPIs Proyectados")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "📦 Unidades Totales",
                        f"{summary['total_units']:,}",
                        delta=f"Máximo: {summary['max_sales_units']} (día {summary['max_sales_day']})"
                    )
                
                with col2:
                    st.metric(
                        "💵 Ingresos Proyectados",
                        f"${summary['total_revenue']:,.0f}",
                        delta=None
                    )
                
                with col3:
                    st.metric(
                        "🏷️ Precio Promedio",
                        f"${summary['avg_price']:.2f}",
                        delta=None
                    )
                
                with col4:
                    st.metric(
                        "📉 Descuento Promedio",
                        f"{summary['avg_discount']:.1f}%",
                        delta=None
                    )
                
                # GRÁFICO DE PREDICCIÓN
                st.markdown(
                    "<div class='section-divider'></div>",
                    unsafe_allow_html=True
                )
                st.markdown("### 📈 Predicción de Ventas Diarias")
                
                fig, ax = plt.subplots(figsize=(14, 5))
                
                # Línea principal de predicción
                ax.plot(
                    df_predictions['dia'],
                    df_predictions['unidades_vendidas_predichas'],
                    linewidth=2.5,
                    color='#667eea',
                    marker='o',
                    markersize=4,
                    label='Unidades Predichas'
                )
                
                # Marcar Black Friday (día 28)
                black_friday_day = df_predictions[df_predictions['dia_mes'] == 28]
                if not black_friday_day.empty:
                    bf_day = black_friday_day.iloc[0]
                    bf_idx = int(bf_day['dia']) - 1
                    ax.axvline(
                        x=bf_idx + 1,
                        color='#E74C3C',
                        linestyle='--',
                        alpha=0.7,
                        linewidth=2
                    )
                    ax.scatter(
                        bf_idx + 1,
                        bf_day['unidades_vendidas_predichas'],
                        color='#E74C3C',
                        s=200,
                        zorder=5,
                        edgecolor='darkred',
                        linewidth=2
                    )
                    ax.annotate(
                        '🎁 Black Friday',
                        xy=(bf_idx + 1, bf_day['unidades_vendidas_predichas']),
                        xytext=(bf_idx + 1, bf_day['unidades_vendidas_predichas'] * 1.15),
                        fontsize=10,
                        fontweight='bold',
                        ha='center',
                        color='#E74C3C',
                        arrowprops=dict(arrowstyle='->', color='#E74C3C', lw=1.5)
                    )
                
                # Configuración del gráfico
                ax.set_xlabel('Día de Noviembre', fontsize=11, fontweight='bold')
                ax.set_ylabel('Unidades Vendidas', fontsize=11, fontweight='bold')
                ax.set_title(
                    'Proyección de Ventas Diarias - Noviembre 2025',
                    fontsize=13,
                    fontweight='bold',
                    pad=20
                )
                ax.grid(True, alpha=0.2, linestyle='--')
                ax.set_xticks(range(1, 31, 2))
                
                sns.despine(left=False, bottom=False)
                plt.tight_layout()
                st.pyplot(fig)
                
                # TABLA DETALLADA
                st.markdown(
                    "<div class='section-divider'></div>",
                    unsafe_allow_html=True
                )
                st.markdown("### 📋 Detalle por Día")
                
                # Preparar tabla para mostrar
                df_display = df_predictions[[
                    'dia', 'dia_semana', 'precio_venta', 'precio_competencia',
                    'descuento_porcentaje', 'unidades_vendidas_predichas', 'ingresos_predichos'
                ]].copy()
                
                df_display.columns = [
                    'Día', 'Semana', 'Precio Venta', 'Precio Comp.',
                    'Descuento', 'Unidades', 'Ingresos'
                ]
                
                # Formatear columnas
                df_display['Precio Venta'] = df_display['Precio Venta'].apply(lambda x: f"${x:.2f}")
                df_display['Precio Comp.'] = df_display['Precio Comp.'].apply(lambda x: f"${x:.2f}")
                df_display['Descuento'] = df_display['Descuento'].apply(lambda x: f"{x*100:.1f}%")
                df_display['Unidades'] = df_display['Unidades'].apply(lambda x: f"{int(x)}")
                df_display['Ingresos'] = df_display['Ingresos'].apply(lambda x: f"${x:,.0f}")
                
                # Marcar Black Friday en la tabla
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    height=400,
                    hide_index=True
                )
                
                # COMPARATIVA DE ESCENARIOS
                st.markdown(
                    "<div class='section-divider'></div>",
                    unsafe_allow_html=True
                )
                st.markdown("### 🔄 Comparativa de Escenarios de Competencia")
                st.markdown(
                    "*Manteniendo el descuento de {:.0f}% fijo y variando solo el precio de competencia*".format(discount)
                )
                
                scenarios_comparison = compare_scenarios(
                    selected_product,
                    discount,
                    model,
                    df,
                    model.feature_names_in_
                )
                
                scenario_cols = st.columns(3)
                scenario_colors = ['#667eea', '#764ba2', '#f093fb']
                
                for idx, (scenario_name, scenario_data) in enumerate(scenarios_comparison.items()):
                    with scenario_cols[idx]:
                        if 'error' not in scenario_data:
                            st.metric(
                                f"{scenario_name}",
                                f"{scenario_data['total_units']:,} unidades",
                                delta=f"${scenario_data['total_revenue']:,.0f} en ingresos"
                            )
                        else:
                            st.error(f"Error en {scenario_name}: {scenario_data['error']}")
                
                # Footer con información
                st.markdown(
                    "<div class='section-divider'></div>",
                    unsafe_allow_html=True
                )
                st.markdown("""
                    <div style='text-align:center; color:#999; font-size:0.85em; margin-top:2em;'>
                    📊 Dashboard actualizó exitosamente<br>
                    Modelo: HistGradientBoosting | Predicciones: Recursivas con actualización de lags<br>
                    Datos: Noviembre 2025
                    </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error en la simulación: {str(e)}")
                st.info("💡 Verifica que el producto esté en los datos y reinten ta")
    else:
        st.info(
            "👈 Configura los parámetros en el panel lateral y haz clic en "
            "'🚀 Simular Ventas' para ver las predicciones."
        )


if __name__ == "__main__":
    main()
