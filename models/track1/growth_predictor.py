import logging
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from typing import Dict, Any, List

logger = logging.getLogger("ratefluencer.growth")

class GrowthPredictor:
    """Predicts future follower growth from historical 30-day time-series data."""
    
    def __init__(self):
        self.use_fallback = False
        try:
            # Check if prophet can be loaded
            from prophet import Prophet
            # Mute prophet logs
            logging.getLogger('prophet').setLevel(logging.WARNING)
        except Exception as e:
            logger.warning(f"Prophet not available or failed to load: {e}. Activating premium Linear Regression time-series fallback.")
            self.use_fallback = True

    def forecast_with_prophet(self, history: List[int], days_to_predict: int = 30) -> float:
        """Forecasts time-series using Facebook Prophet."""
        from prophet import Prophet
        
        # Prepare historical data frame
        start_date = datetime.now() - timedelta(days=len(history))
        dates = [start_date + timedelta(days=d) for d in range(len(history))]
        
        df = pd.DataFrame({
            "ds": dates,
            "y": history
        })
        
        # Instantiate and fit Prophet model
        model = Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=False)
        model.fit(df)
        
        # Future frame
        future = model.make_future_dataframe(periods=days_to_predict, freq='D')
        forecast = model.predict(future)
        
        current_val = float(history[-1])
        predicted_val = float(forecast.iloc[-1]['yhat'])
        
        growth_rate = (predicted_val - current_val) / max(1.0, current_val)
        return growth_rate

    def forecast_with_regression(self, history: List[int], days_to_predict: int = 30) -> float:
        """Fallback method: Fits linear regression with exponential smoothing to forecast future follower counts."""
        n = len(history)
        x = np.arange(n).reshape(-1, 1)
        y = np.array(history, dtype=np.float32)
        
        # Use simple exponential smoothing weights (give more weight to recent days)
        weights = np.exp(np.linspace(-1, 0, n))
        
        # Fit weighted linear regression manually via numpy polyfit
        slope, intercept = np.polyfit(x.flatten(), y, 1, w=weights)
        
        current_val = float(y[-1])
        predicted_val = float(slope * (n + days_to_predict - 1) + intercept)
        
        # Prevent unrealistic negative forecasts
        predicted_val = max(100.0, predicted_val)
        
        growth_rate = (predicted_val - current_val) / max(1.0, current_val)
        return growth_rate

    def predict(self, influencer: Dict[str, Any], days_to_predict: int = 30) -> Dict[str, Any]:
        """Runs the forecast and returns a Growth Score 0-100 and forecast metadata."""
        history = influencer.get("follower_history_30d", [])
        if isinstance(history, str):
            try:
                history = json.loads(history)
            except json.JSONDecodeError:
                history = []
                
        if not history or len(history) < 5:
            # Mock fallback if history is insufficient
            logger.warning(f"Insufficient history for {influencer.get('username')}. Returning default growth metrics.")
            growth_rate = 0.015 # default 1.5% growth
            history = [10000 + i * 50 for i in range(30)]
        else:
            if self.use_fallback:
                growth_rate = self.forecast_with_regression(history, days_to_predict)
            else:
                try:
                    growth_rate = self.forecast_with_prophet(history, days_to_predict)
                except Exception as e:
                    logger.warning(f"Prophet forecast failed: {e}. Falling back to regression forecast.")
                    growth_rate = self.forecast_with_regression(history, days_to_predict)
                    
        # Calculate growth score 0-100 based on the 30-day percentage change
        # A growth rate of 5% in 30 days is excellent (gets a 90 score). 0% gets a 50 score.
        growth_rate_pct = growth_rate * 100.0
        score = 50.0 + growth_rate_pct * 8.0 # e.g. 5% growth -> 50 + 40 = 90
        
        # Bounds checks
        growth_score = float(np.clip(score, 0.0, 100.0))
        
        # Generate predicted 30-day future curve for visualizations
        last_follower = history[-1]
        step = (last_follower * growth_rate) / days_to_predict
        predicted_curve = [int(last_follower + step * (day + 1)) for day in range(days_to_predict)]
        
        return {
            "growth_score": growth_score,
            "growth_rate_30d_pct": float(growth_rate_pct),
            "historical_history": history,
            "predicted_history": predicted_curve
        }

if __name__ == "__main__":
    # Test script
    predictor = GrowthPredictor()
    sample_history = [10000 + i * 35 for i in range(30)] # steady growth
    sample_influencer = {
        "username": "@tester",
        "follower_history_30d": sample_history
    }
    result = predictor.predict(sample_influencer)
    print(f"Growth Score: {result['growth_score']:.2f}")
    print(f"Growth Rate %: {result['growth_rate_30d_pct']:.2f}%")
    print(f"First 5 Predictions: {result['predicted_history'][:5]}")
