"""
Quick start script - Inicia la aplicación en un solo comando.
"""

import subprocess
import sys
import os

def main():
    print("\n" + "="*70)
    print(" "*15 + "SALES FORECAST APP - QUICK START")
    print("="*70 + "\n")
    
    # Verificar que Streamlit está instalado
    try:
        import streamlit
        print("[OK] Streamlit detectado")
    except ImportError:
        print("[!!] Streamlit no está instalado")
        print("    Ejecuta: pip install streamlit")
        return
    
    # Cambiar a directorio app
    app_path = os.path.join(os.path.dirname(__file__), 'app', 'App.py')
    
    if not os.path.exists(app_path):
        print(f"[ERROR] No encontrado: {app_path}")
        return
    
    print("[OK] Aplicación encontrada")
    print("\nIniciando Streamlit...\n")
    print("="*70)
    print("La aplicación se abrirá en: http://localhost:8501")
    print("Presiona CTRL+C para detener")
    print("="*70 + "\n")
    
    # Iniciar Streamlit
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', app_path])


if __name__ == '__main__':
    main()
