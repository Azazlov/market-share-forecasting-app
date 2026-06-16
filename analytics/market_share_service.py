from typing import List, Dict
from datetime import date
import pandas as pd
from database.sales_repository import SalesRepository
from database.marketshare_repository import MarketShareRepository
from database.product_repository import ProductRepository
from models.models import MarketShare


class MarketShareService:

    def __init__(self):
        self.sales_repo = SalesRepository()
        self.marketshare_repo = MarketShareRepository()
        self.product_repo = ProductRepository()

    def calculate(self, period: date) -> List[MarketShare]:
        products = self.product_repo.get_all()
        sales = self.sales_repo.get_by_period(period, period)

        if not sales:
            return []

        df_sales = pd.DataFrame([{
            "product_id": s.product_id,
            "sales_volume": s.sales_volume,
        } for s in sales])

        df_products = pd.DataFrame([{
            "id": p.id,
            "company_id": p.company_id,
        } for p in products])

        merged = df_sales.merge(df_products, left_on="product_id", right_on="id")
        total_volume = merged["sales_volume"].sum()

        if total_volume == 0:
            return []

        company_volumes = merged.groupby("company_id")["sales_volume"].sum()

        self.marketshare_repo.clear_period(period)

        results = []
        for company_id, volume in company_volumes.items():
            share = volume / total_volume
            ms = MarketShare(company_id=company_id, period=period, market_share=share)
            ms.id = self.marketshare_repo.add(ms)
            results.append(ms)

        return results

    def get_all(self) -> List[Dict]:
        records = self.marketshare_repo.get_all()
        result = []
        for r in records:
            result.append({
                "id": r.id,
                "company_id": r.company_id,
                "period": r.period,
                "market_share": r.market_share,
            })
        return result
