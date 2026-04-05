"""
Script de demostración de la aplicación.
Muestra un ejemplo de predicción y valida que todo funciona.
"""

import pandas as pd
import joblib
import sys
sys.path.insert(0, '.')

from app.predictor import RecursivePredictor, compare_scenarios


def demo():
    """Ejecuta una demostración de la aplicación."""
    
    print("\n" + "="*70)
    print("DEMO: SIMULADOR DE PREDICCIÓN DE VENTAS - NOVIEMBRE 2025")
    print("="*70 + "\n")
    
    # Cargar datos y modelo
    print("[1] Cargando modelo y datos...")
    model = joblib.load('models/modelo_final_histgradientboosting.joblib')
    df = pd.read_csv('data/Processed/df_inferencia_performence.csv')
    print(f"    [OK] Modelo cargado (70 features)")
    print(f"    [OK] Dataset cargado (720 filas, 24 productos)")
    
    # Seleccionar un producto
    product = df['nombre'].unique()[0]
    print(f"\n[2] Producto seleccionado: {product}")
    
    # Crear predictor
    print("\n[3] Creando predictor recursivo...")
    predictor = RecursivePredictor(model, df, model.feature_names_in_)
    print("    [OK] Predictor inicializado")
    
    # Hacer predicción
    print("\n[4] Realizando predicción recursiva (30 días)...")
    print("    (Actualizando lags día a día...)")
    
    df_pred, summary = predictor.predict_november(
        product,
        discount_pct=10,  # 10% descuento
        competition_scenario='actual'
    )
    
    print("    [OK] Predicción completada\n")
    
    # Mostrar resumen
    print("RESULTADOS DE LA PREDICCIÓN:")
    print("-" * 70)
    print(f"Producto:                {product}")
    print(f"Unidades proyectadas:    {summary['total_units']:,} unidades")
    print(f"Ingresos proyectados:    ${summary['total_revenue']:,.2f}")
    print(f"Precio promedio venta:   ${summary['avg_price']:.2f}")
    print(f"Descuento promedio:      {summary['avg_discount']:.1f}%")
    print(f"Día de máximas ventas:   Día {summary['max_sales_day']} ({summary['max_sales_units']} unidades)")
    print("-" * 70)
    
    # Mostrar primeros 5 días
    print("\nPRIMEROS 5 DÍAS DE NOVIEMBRE:")
    print("-" * 70)
    cols_display = ['dia', 'dia_semana', 'precio_venta', 'unidades_vendidas_predichas', 'ingresos_predichos']
    print(df_pred[cols_display].head().to_string(index=False))
    
    # Black Friday
    print("\nBLACK FRIDAY (DÍA 28):")
    print("-" * 70)
    bf_row = df_pred[df_pred['dia'] == 28].iloc[0]
    print(f"Día:                     28 (Viernes)")
    print(f"Unidades predichas:      {int(bf_row['unidades_vendidas_predichas'])} unidades")
    print(f"Precio venta:            ${bf_row['precio_venta']:.2f}")
    print(f"Ingresos:                ${bf_row['ingresos_predichos']:,.2f}")
    
    # Comparativa de escenarios
    print("\n" + "="*70)
    print("COMPARATIVA DE ESCENARIOS (Descuento 10% fijo):")
    print("="*70)
    
    scenarios = compare_scenarios(product, 10, model, df, model.feature_names_in_)
    
    for scenario_name, scenario_data in scenarios.items():
        print(f"\n{scenario_name}:")
        print(f"  Unidades: {scenario_data['total_units']:,}")
        print(f"  Ingresos: ${scenario_data['total_revenue']:,.2f}")
    
    print("\n" + "="*70)
    print("[OK] DEMO COMPLETADA EXITOSAMENTE")
    print("="*70 + "\n")
    
    print("Para ejecutar la aplicación interactiva:")
    print("  streamlit run app/App.py")
    print()


if __name__ == '__main__':
    try:
        demo()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
