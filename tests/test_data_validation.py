"""
Tests de validación de datos y columnas.
Asegura que el dataframe tiene todas las columnas necesarias.
"""

import pytest
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import sys

sys.path.insert(0, '/ProjForestCastDataScience')


class TestDataValidation:
    """Tests para validar la integridad del dataframe."""
    
    @pytest.fixture(scope="class")
    def df(self):
        """Carga el dataframe una sola vez."""
        return pd.read_csv('data/Processed/df_inferencia_performence.csv')
    
    @pytest.fixture(scope="class")
    def model(self):
        """Carga el modelo una sola vez."""
        return joblib.load('models/modelo_final_histgradientboosting.joblib')
    
    def test_csv_load_successful(self, df):
        """Test que el CSV se carga sin errores."""
        assert df is not None
        assert len(df) > 0
    
    def test_dataframe_has_30_days_per_product(self, df):
        """Test que hay 30 registros por cada producto."""
        product_counts = df['nombre'].value_counts()
        
        for product, count in product_counts.items():
            assert count == 30, f"Producto {product} tiene {count} registros, se esperan 30"
    
    def test_dataframe_has_24_products(self, df):
        """Test que hay 24 productos únicos."""
        products = df['nombre'].unique()
        assert len(products) == 24
    
    def test_all_dates_are_november_2025(self, df):
        """Test que todas las fechas son de noviembre 2025."""
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        assert df['fecha'].min().year == 2025
        assert df['fecha'].max().year == 2025
        assert df['fecha'].min().month == 11
        assert df['fecha'].max().month == 11
        assert df['fecha'].min().day == 1
        assert df['fecha'].max().day == 30
    
    def test_lag_columns_exist(self, df):
        """Test que existen todas las columnas de lag (lag_1 a lag_7)."""
        for i in range(1, 8):
            lag_col = f'lag_{i}'
            assert lag_col in df.columns, f"Falta columna {lag_col}"
    
    def test_media_movil_column_exists(self, df):
        """Test que existe la columna media_movil_7."""
        assert 'media_movil_7' in df.columns
    
    def test_precio_columns_exist(self, df):
        """Test que existen las columnas de precio."""
        required_price_cols = [
            'precio_base', 'precio_venta', 'precio_competencia',
            'descuento_porcentaje', 'ratio_precio'
        ]
        
        for col in required_price_cols:
            assert col in df.columns, f"Falta columna {col}"
    
    def test_target_column_exists(self, df):
        """Test que existe la columna de target (unidades_vendidas)."""
        assert 'unidades_vendidas' in df.columns
    
    def test_temporal_columns_exist(self, df):
        """Test que existen todas las columnas temporales."""
        temporal_cols = [
            'fecha', 'año', 'mes', 'dia_mes', 'dia_semana',
            'dia_semana_num', 'fin_semana', 'dia_festivo',
            'dia_blackfriday', 'dia_cyber_monday', 'trimestre',
            'semana_año', 'dia_año', 'es_bisiesto'
        ]
        
        for col in temporal_cols:
            assert col in df.columns, f"Falta columna temporal {col}"
    
    def test_ohe_columns_exist(self, df):
        """Test que existen columnas de One-Hot Encoding."""
        ohe_pattern = [
            # Nombres (al menos algunos)
            'nombre_OHE_Nike Air Zoom Pegasus 40',
            'nombre_OHE_Adidas Ultraboost 23',
            # Categorías
            'categoria_OHE_Fitness',
            'categoria_OHE_Running',
            # Subcategorías (al menos algunas)
            'subcategoria_OHE_Zapatillas Running',
            'subcategoria_OHE_Esterilla Yoga'
        ]
        
        for col in ohe_pattern:
            assert col in df.columns, f"Falta columna OHE {col}"
    
    def test_lags_numeric_values(self, df):
        """Test que todos los lags contienen valores numéricos."""
        for i in range(1, 8):
            lag_col = f'lag_{i}'
            assert pd.api.types.is_numeric_dtype(df[lag_col]), \
                f"Columna {lag_col} no es numérica"
    
    def test_no_null_in_critical_columns(self, df):
        """Test que no hay nulos en columnas críticas."""
        critical_cols = [
            'fecha', 'nombre', 'precio_base', 'precio_venta',
            'lag_1', 'lag_2', 'lag_3', 'lag_4', 'lag_5', 'lag_6', 'lag_7',
            'media_movil_7'
        ]
        
        for col in critical_cols:
            null_count = df[col].isna().sum()
            assert null_count == 0, f"Columna {col} tiene {null_count} nulos"
    
    def test_prices_are_positive(self, df):
        """Test que todos los precios son positivos."""
        price_cols = ['precio_base', 'precio_venta', 'precio_competencia']
        
        for col in price_cols:
            assert (df[col] > 0).all(), f"Columna {col} tiene valores no positivos"
    
    def test_lags_are_non_negative(self, df):
        """Test que todos los lags son no-negativos (pueden ser 0)."""
        for i in range(1, 8):
            lag_col = f'lag_{i}'
            assert (df[lag_col] >= 0).all(), f"Columna {lag_col} tiene valores negativos"
    
    def test_media_movil_is_non_negative(self, df):
        """Test que media_movil_7 es no-negativa."""
        assert (df['media_movil_7'] >= 0).all()
    
    def test_descuento_is_numeric(self, df):
        """Test que descuento es numérico (puede ser negativo o positivo)."""
        assert pd.api.types.is_numeric_dtype(df['descuento_porcentaje'])
        # Descuento puede ser negativo (aumento de precio) o positivo (descuento)
        assert df['descuento_porcentaje'].min() >= -20  # Límite razonable
        assert df['descuento_porcentaje'].max() <= 20   # Límite razonable
    
    def test_black_friday_is_on_day_28(self, df):
        """Test que Black Friday está marcado en día 28."""
        bf_rows = df[df['dia_blackfriday'] == 1]
        
        for _, row in bf_rows.iterrows():
            assert row['dia_mes'] == 28, "Black Friday debe estar en día 28"
    
    def test_model_feature_consistency(self, df, model):
        """Test que el modelo espera columnas que existen."""
        model_features = set(model.feature_names_in_)
        df_columns = set(df.columns)
        
        missing_features = model_features - df_columns
        assert len(missing_features) == 0, \
            f"Faltan columnas para el modelo: {missing_features}"
    
    def test_ohe_columns_are_binary(self, df):
        """Test que columnas OHE solo tienen valores 0 o 1."""
        ohe_cols = [col for col in df.columns if col.startswith('nombre_OHE_') or
                    col.startswith('categoria_OHE_') or 
                    col.startswith('subcategoria_OHE_')]
        
        for col in ohe_cols:
            unique_vals = df[col].unique()
            assert set(unique_vals).issubset({0, 1}), \
                f"Columna OHE {col} tiene valores no binarios"
    
    def test_one_ohe_per_product(self, df):
        """Test que cada producto tiene exactamente una columna OHE = 1."""
        nombre_ohe_cols = [col for col in df.columns if col.startswith('nombre_OHE_')]
        
        for idx, row in df.iterrows():
            ohe_sum = sum(row[col] for col in nombre_ohe_cols)
            assert ohe_sum == 1, \
                f"Fila {idx} no tiene exactamente una columna nombre_OHE=1"
    
    def test_ratio_precio_consistency(self, df):
        """Test que ratio_precio = precio_venta / precio_competencia."""
        df_sample = df.sample(min(100, len(df)))  # Verificar 100 filas aleatorias
        
        for idx, row in df_sample.iterrows():
            expected_ratio = row['precio_venta'] / (row['precio_competencia'] + 0.01)
            assert abs(row['ratio_precio'] - expected_ratio) < 0.01, \
                f"Fila {idx} tiene ratio_precio inconsistente"
    
    def test_ingresos_calculation(self, df):
        """Test que ingresos = unidades_vendidas * precio_venta."""
        df_sample = df.sample(min(100, len(df)))  # Verificar 100 filas aleatorias
        
        for idx, row in df_sample.iterrows():
            expected_ingresos = row['unidades_vendidas'] * row['precio_venta']
            assert abs(row['ingresos'] - expected_ingresos) < 0.01, \
                f"Fila {idx} tiene ingresos inconsistente"


class TestModelValidation:
    """Tests para validar que el modelo está correctamente guardado."""
    
    def test_model_load_successful(self):
        """Test que el modelo se carga sin errores."""
        model = joblib.load('models/modelo_final_histgradientboosting.joblib')
        assert model is not None
    
    def test_model_has_feature_names(self):
        """Test que el modelo tiene nombres de features."""
        model = joblib.load('models/modelo_final_histgradientboosting.joblib')
        assert hasattr(model, 'feature_names_in_')
        assert len(model.feature_names_in_) > 0
    
    def test_model_has_70_features(self):
        """Test que el modelo tiene exactamente 70 features."""
        model = joblib.load('models/modelo_final_histgradientboosting.joblib')
        assert len(model.feature_names_in_) == 70
    
    def test_model_can_predict(self):
        """Test que el modelo puede hacer predicciones."""
        model = joblib.load('models/modelo_final_histgradientboosting.joblib')
        df = pd.read_csv('data/Processed/df_inferencia_performence.csv')
        
        # Preparar un input de muestra
        sample_row = df.iloc[0]
        X_sample = np.zeros(len(model.feature_names_in_))
        
        for i, feat in enumerate(model.feature_names_in_):
            if feat in sample_row.index:
                try:
                    X_sample[i] = float(sample_row[feat])
                except:
                    X_sample[i] = 0
        
        prediction = model.predict(X_sample.reshape(1, -1))
        assert isinstance(prediction, np.ndarray)
        assert len(prediction) == 1
        assert prediction[0] >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
