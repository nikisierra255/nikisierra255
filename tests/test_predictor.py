"""
Tests unitarios para la lógica de predicción recursiva.
Valida que los lags se actualicen correctamente día a día.
"""

import pytest
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import sys
sys.path.insert(0, '/ProjForestCastDataScience')

from app.predictor import RecursivePredictor, compare_scenarios


class TestRecursivePredictor:
    """Suite de tests para la clase RecursivePredictor."""
    
    @pytest.fixture(scope="class")
    def setup_data(self):
        """Carga modelo y datos para todos los tests."""
        model = joblib.load('models/modelo_final_histgradientboosting.joblib')
        df = pd.read_csv('data/Processed/df_inferencia_performence.csv')
        
        yield {
            'model': model,
            'df': df,
            'feature_names': model.feature_names_in_
        }
    
    def test_predictor_initialization(self, setup_data):
        """Test que el predictor se inicializa correctamente."""
        predictor = RecursivePredictor(
            setup_data['model'],
            setup_data['df'],
            setup_data['feature_names']
        )
        
        assert predictor.model is not None
        assert len(predictor.model_feature_names) == 70
        assert predictor.base_df is not None
    
    def test_predict_november_returns_dataframe(self, setup_data):
        """Test que predict_november retorna un dataframe válido."""
        predictor = RecursivePredictor(
            setup_data['model'],
            setup_data['df'],
            setup_data['feature_names']
        )
        
        product = setup_data['df']['nombre'].unique()[0]
        df_result, summary = predictor.predict_november(product)
        
        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 30
        assert 'unidades_vendidas_predichas' in df_result.columns
        assert 'ingresos_predichos' in df_result.columns
    
    def test_predict_november_returns_summary(self, setup_data):
        """Test que el resumen contiene las claves correctas."""
        predictor = RecursivePredictor(
            setup_data['model'],
            setup_data['df'],
            setup_data['feature_names']
        )
        
        product = setup_data['df']['nombre'].unique()[0]
        _, summary = predictor.predict_november(product)
        
        assert 'total_units' in summary
        assert 'total_revenue' in summary
        assert 'avg_price' in summary
        assert 'avg_discount' in summary
        assert 'max_sales_day' in summary
        assert 'max_sales_units' in summary
    
    def test_predictions_are_positive(self, setup_data):
        """Test que todas las predicciones son positivas (no negativas)."""
        predictor = RecursivePredictor(
            setup_data['model'],
            setup_data['df'],
            setup_data['feature_names']
        )
        
        product = setup_data['df']['nombre'].unique()[0]
        df_result, _ = predictor.predict_november(product)
        
        assert (df_result['unidades_vendidas_predichas'] >= 0).all()
    
    def test_ingresos_calculation(self, setup_data):
        """Test que ingresos se calculan correctamente."""
        predictor = RecursivePredictor(
            setup_data['model'],
            setup_data['df'],
            setup_data['feature_names']
        )
        
        product = setup_data['df']['nombre'].unique()[0]
        df_result, _ = predictor.predict_november(product)
        
        # Verificar que ingresos = unidades * precio_venta
        for idx, row in df_result.iterrows():
            expected_ingresos = row['unidades_vendidas_predichas'] * row['precio_venta']
            assert abs(row['ingresos_predichos'] - expected_ingresos) < 0.01
    
    def test_discount_applied(self, setup_data):
        """Test que el descuento se aplica correctamente."""
        predictor = RecursivePredictor(
            setup_data['model'],
            setup_data['df'],
            setup_data['feature_names']
        )
        
        product = setup_data['df']['nombre'].unique()[0]
        discount_pct = 10
        
        df_result, _ = predictor.predict_november(product, discount_pct=discount_pct)
        
        # El precio_venta debe ser menor que precio_base en el 10%
        assert (df_result['precio_venta'] < df_result['precio_base']).all()
    
    def test_no_discount(self, setup_data):
        """Test que sin descuento, precio_venta = precio_base."""
        predictor = RecursivePredictor(
            setup_data['model'],
            setup_data['df'],
            setup_data['feature_names']
        )
        
        product = setup_data['df']['nombre'].unique()[0]
        df_result, _ = predictor.predict_november(product, discount_pct=0)
        
        # Con descuento 0, precio_venta debe ser igual a precio_base
        for idx, row in df_result.iterrows():
            assert abs(row['precio_venta'] - row['precio_base']) < 0.01
    
    def test_update_lags_shifts_correctly(self, setup_data):
        """Test que los lags se desplazan correctamente."""
        predictor = RecursivePredictor(
            setup_data['model'],
            setup_data['df'],
            setup_data['feature_names']
        )
        
        current_lags = {
            'lag_1': 10.0,
            'lag_2': 20.0,
            'lag_3': 30.0,
            'lag_4': 40.0,
            'lag_5': 50.0,
            'lag_6': 60.0,
            'lag_7': 70.0,
        }
        
        new_prediction = 5.0
        updated_lags = predictor._update_lags(current_lags, new_prediction)
        
        assert updated_lags['lag_1'] == new_prediction
        assert updated_lags['lag_2'] == current_lags['lag_1']
        assert updated_lags['lag_3'] == current_lags['lag_2']
        assert updated_lags['lag_4'] == current_lags['lag_3']
        assert updated_lags['lag_5'] == current_lags['lag_4']
        assert updated_lags['lag_6'] == current_lags['lag_5']
        assert updated_lags['lag_7'] == current_lags['lag_6']
    
    def test_invalid_product_raises_error(self, setup_data):
        """Test que un producto inválido raise ValueError."""
        predictor = RecursivePredictor(
            setup_data['model'],
            setup_data['df'],
            setup_data['feature_names']
        )
        
        with pytest.raises(ValueError):
            predictor.predict_november("Producto Inexistente")
    
    def test_competition_scenario_minus5(self, setup_data):
        """Test que escenario competitive_minus5 reduce precio competencia."""
        predictor = RecursivePredictor(
            setup_data['model'],
            setup_data['df'],
            setup_data['feature_names']
        )
        
        product = setup_data['df']['nombre'].unique()[0]
        
        df_actual, _ = predictor.predict_november(product, competition_scenario='actual')
        df_minus5, _ = predictor.predict_november(product, competition_scenario='competitive_minus5')
        
        # Precio de competencia debe ser 5% menor en el escenario minus5
        price_comp_actual = df_actual['precio_competencia'].iloc[0]
        price_comp_minus5 = df_minus5['precio_competencia'].iloc[0]
        
        assert price_comp_minus5 < price_comp_actual
        assert abs(price_comp_minus5 / price_comp_actual - 0.95) < 0.01
    
    def test_competition_scenario_plus5(self, setup_data):
        """Test que escenario competitive_plus5 aumenta precio competencia."""
        predictor = RecursivePredictor(
            setup_data['model'],
            setup_data['df'],
            setup_data['feature_names']
        )
        
        product = setup_data['df']['nombre'].unique()[0]
        
        df_actual, _ = predictor.predict_november(product, competition_scenario='actual')
        df_plus5, _ = predictor.predict_november(product, competition_scenario='competitive_plus5')
        
        # Precio de competencia debe ser 5% mayor en el escenario plus5
        price_comp_actual = df_actual['precio_competencia'].iloc[0]
        price_comp_plus5 = df_plus5['precio_competencia'].iloc[0]
        
        assert price_comp_plus5 > price_comp_actual
        assert abs(price_comp_plus5 / price_comp_actual - 1.05) < 0.01
    
    def test_total_revenue_equals_sum_of_daily_ingresos(self, setup_data):
        """Test que revenue total = suma de ingresos diarios."""
        predictor = RecursivePredictor(
            setup_data['model'],
            setup_data['df'],
            setup_data['feature_names']
        )
        
        product = setup_data['df']['nombre'].unique()[0]
        df_result, summary = predictor.predict_november(product)
        
        expected_revenue = df_result['ingresos_predichos'].sum()
        assert abs(summary['total_revenue'] - expected_revenue) < 0.01
    
    def test_total_units_equals_sum_of_daily_unidades(self, setup_data):
        """Test que unidades total = suma de unidades diarias."""
        predictor = RecursivePredictor(
            setup_data['model'],
            setup_data['df'],
            setup_data['feature_names']
        )
        
        product = setup_data['df']['nombre'].unique()[0]
        df_result, summary = predictor.predict_november(product)
        
        expected_units = int(df_result['unidades_vendidas_predichas'].sum())
        assert summary['total_units'] == expected_units
    
    def test_max_sales_day_is_correct(self, setup_data):
        """Test que el día de máximas ventas es correcto."""
        predictor = RecursivePredictor(
            setup_data['model'],
            setup_data['df'],
            setup_data['feature_names']
        )
        
        product = setup_data['df']['nombre'].unique()[0]
        df_result, summary = predictor.predict_november(product)
        
        max_units = df_result['unidades_vendidas_predichas'].max()
        max_day = df_result[df_result['unidades_vendidas_predichas'] == max_units].iloc[0]['dia']
        
        assert summary['max_sales_day'] == int(max_day)


class TestCompareScenarios:
    """Tests para la función de comparación de escenarios."""
    
    @pytest.fixture(scope="class")
    def setup_data(self):
        """Carga modelo y datos."""
        model = joblib.load('models/modelo_final_histgradientboosting.joblib')
        df = pd.read_csv('data/Processed/df_inferencia_performence.csv')
        
        yield {
            'model': model,
            'df': df,
            'feature_names': model.feature_names_in_
        }
    
    def test_compare_scenarios_returns_dict(self, setup_data):
        """Test que compare_scenarios retorna diccionario."""
        product = setup_data['df']['nombre'].unique()[0]
        result = compare_scenarios(
            product, 0, setup_data['model'], setup_data['df'],
            setup_data['feature_names']
        )
        
        assert isinstance(result, dict)
        assert len(result) == 3
    
    def test_compare_scenarios_has_three_scenarios(self, setup_data):
        """Test que tenga los tres escenarios."""
        product = setup_data['df']['nombre'].unique()[0]
        result = compare_scenarios(
            product, 0, setup_data['model'], setup_data['df'],
            setup_data['feature_names']
        )
        
        assert 'Actual (0%)' in result
        assert 'Competencia -5%' in result
        assert 'Competencia +5%' in result
    
    def test_compare_scenarios_contains_summaries(self, setup_data):
        """Test que cada escenario tenga datos válidos."""
        product = setup_data['df']['nombre'].unique()[0]
        result = compare_scenarios(
            product, 0, setup_data['model'], setup_data['df'],
            setup_data['feature_names']
        )
        
        for scenario_name, scenario_data in result.items():
            assert 'total_units' in scenario_data
            assert 'total_revenue' in scenario_data


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
