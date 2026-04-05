"""
Script para ejecutar todos los tests con reporte profesional.
"""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Ejecuta todos los tests con pytest."""
    
    test_dir = Path(__file__).parent / 'tests'
    
    print("\n" + "="*70)
    print("🧪 EJECUTANDO SUITE DE TESTS PROFESIONAL")
    print("="*70 + "\n")
    
    cmd = [
        sys.executable, '-m', 'pytest',
        str(test_dir),
        '-v',
        '--tb=short',
        '--color=yes',
        '-ra',
        '--cov=app',
        '--cov-report=term-missing'
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    print("\n" + "="*70)
    if result.returncode == 0:
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
    print("="*70 + "\n")
    
    return result.returncode


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
