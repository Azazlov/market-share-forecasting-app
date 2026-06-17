"""Заполнение БД тестовыми данными."""

from database.db import init_db, get_connection
from database.company_repository import CompanyRepository
from database.product_repository import ProductRepository
from database.sales_repository import SalesRepository
from models.models import Company, Product, Sale
from datetime import date
import random
import math


def seed():
    init_db()

    company_repo = CompanyRepository()
    product_repo = ProductRepository()
    sales_repo = SalesRepository()

    conn = get_connection()
    conn.execute("DELETE FROM sales")
    conn.execute("DELETE FROM market_share")
    conn.execute("DELETE FROM products")
    conn.execute("DELETE FROM companies")
    conn.commit()
    conn.close()

    companies_data = [
        ("ООО ТехноПром", "Электроника"),
        ("АО АгроХолдинг", "Сельское хозяйство"),
        ("ЗАО СтройИнвест", "Строительство"),
        ("ООО МедТех", "Медицина"),
        ("ИП ПищеПром", "Пищевая промышленность"),
    ]
    company_ids = []
    for name, industry in companies_data:
        cid = company_repo.add(Company(name=name, industry=industry))
        company_ids.append(cid)

    products_per_company = [
        ["Смартфон X1", "Ноутбук Pro", "Планшет Lite"],
        ["Удобрение Универсал", "Семена Элит", "Трактор М"],
        ["Цемент М500", "Кирпич", "Арматура"],
        ["Тонометр", "Стетоскоп", "Анализатор"],
        ["Мука высший сорт", "Сахар", "Масло подсолнечное"],
    ]
    product_ids = []
    product_company_map = {}
    for ci, products in enumerate(products_per_company):
        for pname in products:
            pid = product_repo.add(Product(company_id=company_ids[ci], name=pname))
            product_ids.append(pid)
            product_company_map[pid] = company_ids[ci]

    random.seed(42)

    profile_templates = [
        {"base_volume": 500, "trend": 8, "seasonal_amplitude": 0.15,
         "base_price": 300, "price_elasticity": -0.5},
        {"base_volume": 350, "trend": 3, "seasonal_amplitude": 0.30,
         "base_price": 80, "price_elasticity": -0.3},
        {"base_volume": 450, "trend": -2, "seasonal_amplitude": 0.10,
         "base_price": 120, "price_elasticity": -0.4},
        {"base_volume": 300, "trend": 5, "seasonal_amplitude": 0.05,
         "base_price": 250, "price_elasticity": -0.2},
        {"base_volume": 400, "trend": 2, "seasonal_amplitude": 0.08,
         "base_price": 50, "price_elasticity": -0.6},
    ]
    company_profiles = dict(zip(company_ids, profile_templates))

    product_weights = {}
    for pid, cid in product_company_map.items():
        product_weights[pid] = random.uniform(0.7, 1.3)

    base_date = date(2024, 7, 1)
    months = 18

    for i in range(months):
        m = (base_date.month + i - 1) % 12 + 1
        y = base_date.year + (base_date.month + i - 1) // 12
        period = date(y, m, 1)

        month_frac = i / months

        for pid in product_ids:
            cid = product_company_map[pid]
            profile = company_profiles[cid]
            weight = product_weights[pid]

            trend = profile["trend"] * month_frac
            seasonal = profile["seasonal_amplitude"] * math.sin(2 * math.pi * (m - 1) / 12)
            noise = random.gauss(0, 0.08)
            volume_factor = 1.0 + trend + seasonal + noise
            volume = profile["base_volume"] * weight * max(0.3, volume_factor)

            ad_base = profile["base_volume"] * weight * 3
            ad_seasonal = 0.3 * math.sin(2 * math.pi * (m - 3) / 12 + 1)
            ad_noise = random.gauss(0, 0.1)
            ad_budget = ad_base * max(0.5, 1.0 + ad_seasonal + ad_noise)

            ad_effect = 0.15 * math.log(ad_budget / (profile["base_volume"] * weight * 3) + 1)
            price_seasonal = 0.05 * math.sin(2 * math.pi * (m - 6) / 12)
            price = profile["base_price"] * (1.0 + price_seasonal + random.gauss(0, 0.03))
            effective_volume = volume * (1 + ad_effect) * (price / profile["base_price"]) ** profile["price_elasticity"]

            sales_repo.add(Sale(
                product_id=pid,
                period=period,
                sales_volume=round(max(1, effective_volume), 2),
                price=round(max(1, price), 2),
                ad_budget=round(max(1, ad_budget), 2),
            ))

    print("Тестовые данные успешно добавлены:")
    print(f"  - Предприятий: {len(company_ids)}")
    print(f"  - Товаров: {len(product_ids)}")
    print(f"  - Продаж: {len(product_ids) * months}")
    print(f"  - Периодов: {months} месяцев (с 2024-07 по 2025-12)")


if __name__ == "__main__":
    seed()
