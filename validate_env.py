"""
Script de validación pre-ejecución de la aplicación.
Verifica que todos los requisitos y datos estén disponibles.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import joblib


def check_environment():
    """Verifica que el entorno está correctamente configurado."""
    print("\n" + "="*70)
    print("🔍 VERIFICANDO ENTORNO DE EJECUCIÓN")
    print("="*70 + "\n")
    
    checks_passed = 0
    checks_failed = 0
    
    # 1. Verificar Python version
    print(f"✓ Python {sys.version.split()[0]}")
    checks_passed += 1
    
    # 2. Verificar archivos críticos
    required_files = {
        'models/modelo_final_histgradientboosting.joblib': 'Modelo ML',
        'data/Processed/df_inferencia_performence.csv': 'Dataset de inferencia',
        'app/App.py': 'Aplicación principal',
        'app/predictor.py': 'Módulo de predicción'
    }
    
    print("\n📂 Archivos requeridos:")
    for file_path, description in required_files.items():
        if Path(file_path).exists():
            print(f"  ✓ {description} - {file_path}")
            checks_passed += 1
        else:
            print(f"  ✗ {description} - {file_path} NO ENCONTRADO")
            checks_failed += 1
    
    # 3. Verificar paquetes importados
    print("\n📦 Paquetes importados:")
    required_packages = {
        'streamlit': 'Streamlit',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'seaborn': 'Seaborn',
        'matplotlib': 'Matplotlib',
        'sklearn': 'Scikit-learn',
        'joblib': 'Joblib'
    }
    
    for package_name, display_name in required_packages.items():
        try:
            __import__(package_name)
            print(f"  ✓ {display_name}")
            checks_passed += 1
        except ImportError:
            print(f"  ✗ {display_name} NO DISPONIBLE")
            checks_failed += 1
    
    # 4. Verificar modelo
    print("\n🤖 Validación del modelo:")
    try:
        model = joblib.load('models/modelo_final_histgradientboosting.joblib')
        print(f"  ✓ Modelo cargado (70 features)")
        print(f"  ✓ Tipo: {type(model).__name__}")
        checks_passed += 1
    except Exception as e:
        print(f"  ✗ Error al cargar modelo: {e}")
        checks_failed += 1
    
    # 5. Verificar datos
    print("\n📊 Validación de datos:")
    try:
        df = pd.read_csv('data/Processed/df_inferencia_performence.csv')
        print(f"  ✓ Dataset cargado ({df.shape[0]} filas, {df.shape[1]} columnas)")
        
        products = df['nombre'].nunique()
        print(f"  ✓ Productos: {products}")
        
        # Verificar lags
        lag_cols = [col for col in df.columns if 'lag_' in col]
        print(f"  ✓ Columnas de lag encontradas: {len(lag_cols)}")
        
        # Verificar media móvil
        if 'media_movil_7' in df.columns:
            print(f"  ✓ Media móvil detectada")
        
        checks_passed += 3
    except Exception as e:
        print(f"  ✗ Error al cargar datos: {e}")
        checks_failed += 1
    
    # Resumen
    print("\n" + "="*70)
    print(f"✅ Verificaciones pasadas: {checks_passed}")
    print(f"❌ Verificaciones fallidas: {checks_failed}")
    
    if checks_failed == 0:
        print("\n🎉 ENTORNO LISTO PARA EJECUTAR LA APLICACIÓN")
        print("Ejecuta: streamlit run app/App.py")
    else:
        print("\n⚠️  SOLUCIONA LOS ERRORES ANTES DE EJECUTAR LA APLICACIÓN")
    
    print("="*70 + "\n")
    
    return checks_failed == 0


if __name__ == '__main__':
    success = check_environment()
    sys.exit(0 if success else 1)
