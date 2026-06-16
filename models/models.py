from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class Company:
    id: Optional[int] = None
    name: str = ""
    industry: str = ""


@dataclass
class Product:
    id: Optional[int] = None
    company_id: int = 0
    name: str = ""


@dataclass
class Sale:
    id: Optional[int] = None
    product_id: int = 0
    period: date = date.today()
    sales_volume: float = 0.0
    price: float = 0.0
    ad_budget: float = 0.0


@dataclass
class MarketShare:
    id: Optional[int] = None
    company_id: int = 0
    period: date = date.today()
    market_share: float = 0.0
