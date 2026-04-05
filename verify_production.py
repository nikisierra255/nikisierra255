"""
Análisis pre-producción y checklist de verificación.
Valida que el proyecto cumple con todos los requisitos.
"""

import pandas as pd
import joblib
import sys
import subprocess

sys.path.insert(0, '.')
from app.predictor import RecursivePredictor


def verify_requirements():
    """Verifica todos los requisitos del proyecto."""
    
    checklist = {
        'Datos': {},
        'Modelo': {},
        'Codigo': {},
        'Tests': {},
        'Funcionalidad': {}
    }
    
    print("\n" + "="*70)
    print("CHECKLIST DE VERIFICACIÓN PRE-PRODUCCIÓN")
    print("="*70 + "\n")
    
    # ========== DATOS ==========
    print("[DATOS] Validando dataset...")
    try:
        df = pd.read_csv('data/Processed/df_inferencia_performence.csv')
        
        # 24 productos
        num_products = df['nombre'].nunique()
        checklist['Datos']['24 productos'] = num_products == 24
        
        # 30 días por producto
        product_counts = df['nombre'].value_counts()
        all_30_days = (product_counts == 30).all()
        checklist['Datos']['30 días por producto'] = all_30_days
        
        # Tres columnas de precio
        has_prices = all(col in df.columns for col in 
                        ['precio_base', 'precio_venta', 'precio_competencia'])
        checklist['Datos']['Columnas de precio'] = has_prices
        
        # Lags 1-7
        has_lags = all(f'lag_{i}' in df.columns for i in range(1, 8))
        checklist['Datos']['Lags (1-7)'] = has_lags
        
        # Media móvil
        has_ma = 'media_movil_7' in df.columns
        checklist['Datos']['Media móvil 7'] = has_ma
        
        # Noviembre 2025
        df['fecha'] = pd.to_datetime(df['fecha'])
        is_nov_2025 = (df['fecha'].dt.year == 2025).all() and (df['fecha'].dt.month == 11).all()
        checklist['Datos']['Noviembre 2025'] = is_nov_2025
        
        # No hay nulos en críticos
        critical = ['fecha', 'nombre', 'precio_base', 'lag_1', 'media_movil_7']
        no_nulls = df[critical].isna().sum().sum() == 0
        checklist['Datos']['Sin nulos en columnas críticas'] = no_nulls
        
        print("  [OK] Dataset validado\n")
    except Exception as e:
        print(f"  [FAIL] {e}\n")
        checklist['Datos']['Dataset'] = False
    
    # ========== MODELO ==========
    print("[MODELO] Validando modelo ML...")
    try:
        model = joblib.load('models/modelo_final_histgradientboosting.joblib')
        
        # 70 features
        num_features = len(model.feature_names_in_)
        checklist['Modelo']['70 features'] = num_features == 70
        
        # Puede predecir
        import numpy as np
        X_test = np.zeros(70)
        pred = model.predict(X_test.reshape(1, -1))
        checklist['Modelo']['Puede predecir'] = len(pred) == 1 and pred[0] >= 0
        
        print("  [OK] Modelo validado\n")
    except Exception as e:
        print(f"  [FAIL] {e}\n")
    
    # ========== CÓDIGO ==========
    print("[CODIGO] Validando estructura del código...")
    try:
        # Importar módulos
        from app.predictor import RecursivePredictor, compare_scenarios
        
        checklist['Codigo']['Módulo predictor'] = True
        
        # Archivos existen
        import os
        files = [
            'app/App.py',
            'app/predictor.py',
            'tests/test_predictor.py',
            'tests/test_data_validation.py'
        ]
        checklist['Codigo']['Archivos principales'] = all(os.path.exists(f) for f in files)
        
        print("  [OK] Estructura validada\n")
    except Exception as e:
        print(f"  [FAIL] {e}\n")
    
    # ========== TESTS ==========
    print("[TESTS] Ejecutando suite de tests...")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/test_data_validation.py', '-q'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        data_tests_ok = result.returncode == 0
        checklist['Tests']['Tests de validación'] = data_tests_ok
        
        # Contar tests pasados
        if 'passed' in result.stdout:
            import re
            match = re.search(r'(\d+) passed', result.stdout)
            if match:
                num_passed = int(match.group(1))
                print(f"  [OK] {num_passed} tests de validación pasaron\n")
    except Exception as e:
        print(f"  [FAIL] {e}\n")
    
    # ========== FUNCIONALIDAD ==========
    print("[FUNCIONALIDAD] Probando predicciones recursivas...")
    try:
        model = joblib.load('models/modelo_final_histgradientboosting.joblib')
        df = pd.read_csv('data/Processed/df_inferencia_performence.csv')
        
        predictor = RecursivePredictor(model, df, model.feature_names_in_)
        
        product = df['nombre'].unique()[0]
        df_pred, summary = predictor.predict_november(product, discount_pct=10)
        
        # Valida estructura de predicción
        checklist['Funcionalidad']['30 días predichos'] = len(df_pred) == 30
        checklist['Funcionalidad']['Resumen contiene total_units'] = 'total_units' in summary
        checklist['Funcionalidad']['Total units positivo'] = summary['total_units'] > 0
        checklist['Funcionalidad']['Total revenue positivo'] = summary['total_revenue'] > 0
        
        # Comparativa funciona
        scenarios = compare_scenarios(product, 10, model, df, model.feature_names_in_)
        checklist['Funcionalidad']['3 escenarios comparados'] = len(scenarios) == 3
        
        print("  [OK] Predicciones recursivas funcionando\n")
    except Exception as e:
        print(f"  [FAIL] {e}\n")
        checklist['Funcionalidad']['Predicciones'] = False
    
    # ========== RESUMEN ==========
    print("="*70)
    print("RESUMEN DEL CHECKLIST")
    print("="*70 + "\n")
    
    total_checks = 0
    total_passed = 0
    
    for category, items in checklist.items():
        passed = sum(1 for v in items.values() if v)
        total = len(items)
        total_checked = passed + total
        total_passed_overall = total_passed + passed
        total_checks += total
        
        status = "OK" if passed == total else "PARCIAL"
        symbol = "OK" if passed == total else "!!"
        
        print(f"[{symbol}] {category}: {passed}/{total}")
        for item, result in items.items():
            sym = "OK" if result else "FAIL"
            print(f"    [{sym}] {item}")
    
    print("\n" + "="*70)
    total_passed += total_passed_overall
    overall_percentage = (total_passed / total_checks * 100) if total_checks > 0 else 0
    
    if total_passed == total_checks:
        print(f"[OK] TODOS LOS REQUISITOS CUMPLIDOS ({total_passed}/{total_checks})")
        print("\n Aplicacion lista para produccion")
        return True
    else:
        failed = total_checks - total_passed
        print(f"[!!] {failed}/{total_checks} VERIFICACIONES FALLIDAS ({overall_percentage:.0f}%)")
        return False
    
    print("="*70 + "\n")


if __name__ == '__main__':
    success = verify_requirements()
    sys.exit(0 if success else 1)
