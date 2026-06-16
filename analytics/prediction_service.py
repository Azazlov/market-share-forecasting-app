from typing import Optional, Dict
from datetime import date, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
from database.marketshare_repository import MarketShareRepository
from database.company_repository import CompanyRepository
from database.product_repository import ProductRepository
from database.sales_repository import SalesRepository
from analytics.metrics_service import MetricsService


class PredictionService:

    def __init__(self):
        self.marketshare_repo = MarketShareRepository()
        self.company_repo = CompanyRepository()
        self.product_repo = ProductRepository()
        self.sales_repo = SalesRepository()
        self.metrics = MetricsService()
        self._model: Optional[LinearRegression] = None

    def _features_for_company(self, company_id: int):
        products = self.product_repo.get_by_company(company_id)
        product_ids = [p.id for p in products]
        if not product_ids:
            return [], [], []

        all_sales = self.sales_repo.get_all()
        company_sales = [s for s in all_sales if s.product_id in product_ids]

        periods_data = {}
        for s in company_sales:
            pd_ = periods_data.setdefault(s.period, {
                "volume": 0.0, "price_weighted": 0.0, "ad_budget": 0.0
            })
            pd_["volume"] += s.sales_volume
            pd_["price_weighted"] += s.price * s.sales_volume
            pd_["ad_budget"] += s.ad_budget

        ms_records = self.marketshare_repo.get_by_company(company_id)
        ms_map = {r.period: r.market_share for r in ms_records}

        X, y, periods = [], [], []
        for period in sorted(periods_data):
            if period not in ms_map:
                continue
            pd_ = periods_data[period]
            avg_price = pd_["price_weighted"] / pd_["volume"] if pd_["volume"] > 0 else 0.0

            month = period.month
            month_sin = np.sin(2 * np.pi * month / 12)
            month_cos = np.cos(2 * np.pi * month / 12)

            X.append([
                month_sin,
                month_cos,
                pd_["volume"],
                avg_price,
                pd_["ad_budget"],
            ])
            y.append(ms_map[period])
            periods.append(period)

        return np.array(X) if X else np.array([]), np.array(y) if y else np.array([]), periods

    def train(self, company_id: int) -> Dict:
        X, y, periods = self._features_for_company(company_id)
        if len(X) < 4:
            raise ValueError(
                "Недостаточно данных для обучения (нужно минимум 4 периода "
                "с рассчитанной долей рынка)"
            )

        split = max(2, len(X) - 2)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        periods_train, periods_test = periods[:split], periods[split:]

        self._model = LinearRegression()
        self._model.fit(X_train, y_train)

        y_train_pred = self._model.predict(X_train)
        y_test_pred = self._model.predict(X_test)

        train_mae = self.metrics.mae(y_train, y_train_pred)
        train_rmse = self.metrics.rmse(y_train, y_train_pred)
        test_mae = self.metrics.mae(y_test, y_test_pred) if len(y_test) > 0 else 0.0
        test_rmse = self.metrics.rmse(y_test, y_test_pred) if len(y_test) > 0 else 0.0

        residuals = y_train - y_train_pred
        residual_std = np.std(residuals)
        t_value = 2.0 if len(y_train) > 10 else 2.57

        next_period, next_features = self._build_next_features(periods, X)
        next_pred = float(self._model.predict(next_features.reshape(1, -1))[0])
        ci_half = float(t_value * residual_std * np.sqrt(1 + 1 / len(X_train)))

        return {
            "train": {
                "periods": [p.isoformat() for p in periods_train],
                "actual": y_train.tolist(),
                "predicted": y_train_pred.tolist(),
            },
            "test": {
                "periods": [p.isoformat() for p in periods_test],
                "actual": y_test.tolist() if len(y_test) > 0 else [],
                "predicted": y_test_pred.tolist() if len(y_test_pred) > 0 else [],
            },
            "forecast": {
                "next_period": next_period.isoformat(),
                "predicted_share": float(next_pred),
                "ci_lower": float(next_pred - ci_half),
                "ci_upper": float(next_pred + ci_half),
            },
            "test_mae": float(test_mae),
            "test_rmse": float(test_rmse),
            "train_mae": float(train_mae),
            "train_rmse": float(train_rmse),
            "feature_names": [
                "month_sin", "month_cos", "sales_volume",
                "avg_price", "ad_budget",
            ],
            "coefficients": self._model.coef_.tolist(),
            "intercept": float(self._model.intercept_),
        }

    def _build_next_features(self, periods, X):
        last_period = periods[-1]
        if last_period.month == 12:
            next_period = date(last_period.year + 1, 1, 1)
        else:
            next_period = date(last_period.year, last_period.month + 1, 1)

        month = next_period.month
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)

        lookback = min(3, len(X))
        recent = X[-lookback:]
        avg_volume = float(np.mean(recent[:, 2]))
        avg_price = float(np.mean(recent[:, 3]))
        avg_ad = float(np.mean(recent[:, 4]))

        features = np.array([month_sin, month_cos, avg_volume, avg_price, avg_ad])
        return next_period, features

    def predict_next(self, company_id: int) -> Dict:
        if self._model is None:
            result = self.train(company_id)
            return result["forecast"]

        X, y, periods = self._features_for_company(company_id)
        if len(periods) == 0:
            raise ValueError("Нет данных для прогнозирования")

        next_period, next_features = self._build_next_features(periods, X)
        prediction = float(self._model.predict(next_features.reshape(1, -1))[0])

        return {
            "predicted_share": prediction,
            "next_period": next_period.isoformat(),
        }

    def is_trained(self) -> bool:
        return self._model is not None
