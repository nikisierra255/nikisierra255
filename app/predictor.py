"""
Módulo de predicción recursiva para el modelo de ventas.
Contiene la lógica para realizar predicciones día a día actualizando lags.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List
import warnings

warnings.filterwarnings('ignore')


class RecursivePredictor:
    """
    Predictor que actualiza lags recursivamente para predicciones consistentes.
    """
    
    def __init__(self, model, base_df: pd.DataFrame, model_feature_names: List[str]):
        """
        Inicializa el predictor.
        
        Args:
            model: Modelo entrenado con método predict()
            base_df: DataFrame con datos de noviembre (ya con lags iniciales)
            model_feature_names: Lista de nombres de features que espera el modelo
        """
        self.model = model
        self.model_feature_names = np.array(model_feature_names)
        self.base_df = base_df.copy()
        
    def predict_november(
        self,
        product_name: str,
        discount_pct: float = 0.0,
        competition_scenario: str = "actual"
    ) -> Tuple[pd.DataFrame, dict]:
        """
        Realiza predicciones recursivas para noviembre.
        
        Args:
            product_name: Nombre del producto
            discount_pct: Porcentaje de descuento (-50 a 50)
            competition_scenario: "actual", "competitive_minus5", "competitive_plus5"
            
        Returns:
            Tuple con (dataframe con predicciones, diccionario de resumen)
        """
        # Filtrar datos del producto
        df_product = self.base_df[self.base_df['nombre'] == product_name].copy()
        
        if len(df_product) == 0:
            raise ValueError(f"Producto '{product_name}' no encontrado")
        
        if len(df_product) != 30:
            raise ValueError(f"Se esperan 30 días, se encontraron {len(df_product)}")
        
        # Resetear índice para acceso más fácil
        df_product = df_product.reset_index(drop=True)
        df_product['fecha'] = pd.to_datetime(df_product['fecha'])
        
        # Aplicar ajustes según controles del usuario
        df_product = self._apply_user_adjustments(
            df_product, discount_pct, competition_scenario
        )
        
        # Predicciones recursivas
        predictions = []
        lags = {
            'lag_1': float(df_product.loc[0, 'lag_1']),
            'lag_2': float(df_product.loc[0, 'lag_2']),
            'lag_3': float(df_product.loc[0, 'lag_3']),
            'lag_4': float(df_product.loc[0, 'lag_4']),
            'lag_5': float(df_product.loc[0, 'lag_5']),
            'lag_6': float(df_product.loc[0, 'lag_6']),
            'lag_7': float(df_product.loc[0, 'lag_7']),
        }
        ma7_values = []  # Para calcular media móvil de 7 días
        
        for day in range(30):
            # Actualizar lags (excepto el primer día)
            if day > 0:
                lags = self._update_lags(lags, predictions[-1])
                df_product.loc[day, 'lag_1'] = lags['lag_1']
                df_product.loc[day, 'lag_2'] = lags['lag_2']
                df_product.loc[day, 'lag_3'] = lags['lag_3']
                df_product.loc[day, 'lag_4'] = lags['lag_4']
                df_product.loc[day, 'lag_5'] = lags['lag_5']
                df_product.loc[day, 'lag_6'] = lags['lag_6']
                df_product.loc[day, 'lag_7'] = lags['lag_7']
                
                # Actualizar media móvil
                ma7_values.append(predictions[-1])
                if len(ma7_values) > 7:
                    ma7_values.pop(0)
                df_product.loc[day, 'media_movil_7'] = np.mean(ma7_values)
            
            # Preparar features para el modelo
            X = self._prepare_features(df_product.loc[day])
            
            # Realizar predicción
            prediction = self.model.predict(X.reshape(1, -1))[0]
            prediction = max(0, prediction)  # No negativos
            
            predictions.append(prediction)
            df_product.loc[day, 'unidades_vendidas_predichas'] = prediction
            df_product.loc[day, 'ingresos_predichos'] = (
                prediction * df_product.loc[day, 'precio_venta']
            )
        
        # Agregar columna de día del mes para visualización
        df_product['dia'] = range(1, 31)
        
        # Calcular resumen
        summary = self._calculate_summary(df_product)
        
        return df_product, summary
    
    def _apply_user_adjustments(
        self,
        df: pd.DataFrame,
        discount_pct: float,
        competition_scenario: str
    ) -> pd.DataFrame:
        """Aplica ajustes de descuento y competencia."""
        df = df.copy()
        
        # Ajustar precio_venta según descuento
        df['precio_venta'] = df['precio_base'] * (1 - discount_pct / 100)
        
        # Ajustar precio_competencia según escenario
        if competition_scenario == "competitive_minus5":
            df['precio_competencia'] = df['precio_competencia'] * 0.95
        elif competition_scenario == "competitive_plus5":
            df['precio_competencia'] = df['precio_competencia'] * 1.05
        
        # Recalcular descuento_porcentaje
        df['descuento_porcentaje'] = discount_pct / 100
        
        # Recalcular ratio_precio
        df['ratio_precio'] = df['precio_venta'] / (df['precio_competencia'] + 0.01)
        
        return df
    
    def _update_lags(self, current_lags: dict, newest_prediction: float) -> dict:
        """
        Desplaza los lags: lag_1 become newest_prediction, lag_2 becomes lag_1, etc.
        """
        new_lags = {
            'lag_1': newest_prediction,
            'lag_2': current_lags['lag_1'],
            'lag_3': current_lags['lag_2'],
            'lag_4': current_lags['lag_3'],
            'lag_5': current_lags['lag_4'],
            'lag_6': current_lags['lag_5'],
            'lag_7': current_lags['lag_6'],
        }
        return new_lags
    
    def _prepare_features(self, row: pd.Series) -> np.ndarray:
        """
        Prepara los features exactamente en el orden que espera el modelo.
        """
        features = []
        
        for feature_name in self.model_feature_names:
            if feature_name in row.index:
                value = row[feature_name]
                # Convertir a número
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    value = 0
                features.append(value)
            else:
                features.append(0)
        
        return np.array(features, dtype=np.float32)
    
    def _calculate_summary(self, df: pd.DataFrame) -> dict:
        """Calcula estadísticas resumidas."""
        total_units = df['unidades_vendidas_predichas'].sum()
        total_revenue = df['ingresos_predichos'].sum()
        avg_price = df['precio_venta'].mean()
        avg_discount = df['descuento_porcentaje'].mean() * 100
        
        # Día con mayores ventas
        max_sales_day = df.loc[df['unidades_vendidas_predichas'].idxmax()]
        
        return {
            'total_units': int(total_units),
            'total_revenue': float(total_revenue),
            'avg_price': float(avg_price),
            'avg_discount': float(avg_discount),
            'max_sales_day': int(max_sales_day['dia']),
            'max_sales_units': int(max_sales_day['unidades_vendidas_predichas']),
        }


def compare_scenarios(
    product_name: str,
    discount_pct: float,
    model,
    base_df: pd.DataFrame,
    model_feature_names: List[str]
) -> dict:
    """
    Compara los tres escenarios de competencia.
    
    Returns:
        Dict con resumen para cada escenario
    """
    predictor = RecursivePredictor(model, base_df, model_feature_names)
    
    scenarios = {
        'Actual (0%)': 'actual',
        'Competencia -5%': 'competitive_minus5',
        'Competencia +5%': 'competitive_plus5'
    }
    
    results = {}
    for scenario_name, scenario_code in scenarios.items():
        try:
            _, summary = predictor.predict_november(
                product_name, discount_pct, scenario_code
            )
            results[scenario_name] = summary
        except Exception as e:
            results[scenario_name] = {'error': str(e)}
    
    return results
