from typing import List, Optional
from datetime import date
from database.db import get_connection
from models.models import Sale


class SalesRepository:

    def get_by_product(self, product_id: int) -> List[Sale]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM sales WHERE product_id = ? ORDER BY period", (product_id,)
        ).fetchall()
        conn.close()
        return [Sale(id=r["id"], product_id=r["product_id"],
                     period=date.fromisoformat(r["period"]),
                     sales_volume=r["sales_volume"], price=r["price"],
                     ad_budget=r["ad_budget"]) for r in rows]

    def get_by_period(self, start: date, end: date) -> List[Sale]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM sales WHERE period BETWEEN ? AND ? ORDER BY period",
            (start.isoformat(), end.isoformat()),
        ).fetchall()
        conn.close()
        return [Sale(id=r["id"], product_id=r["product_id"],
                     period=date.fromisoformat(r["period"]),
                     sales_volume=r["sales_volume"], price=r["price"],
                     ad_budget=r["ad_budget"]) for r in rows]

    def get_all(self) -> List[Sale]:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM sales ORDER BY period").fetchall()
        conn.close()
        return [Sale(id=r["id"], product_id=r["product_id"],
                     period=date.fromisoformat(r["period"]),
                     sales_volume=r["sales_volume"], price=r["price"],
                     ad_budget=r["ad_budget"]) for r in rows]

    def get_by_id(self, sale_id: int) -> Optional[Sale]:
        conn = get_connection()
        row = conn.execute("SELECT * FROM sales WHERE id = ?", (sale_id,)).fetchone()
        conn.close()
        if row:
            return Sale(id=row["id"], product_id=row["product_id"],
                        period=date.fromisoformat(row["period"]),
                        sales_volume=row["sales_volume"], price=row["price"],
                        ad_budget=row["ad_budget"])
        return None

    def add(self, sale: Sale) -> int:
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO sales (product_id, period, sales_volume, price, ad_budget) "
            "VALUES (?, ?, ?, ?, ?)",
            (sale.product_id, sale.period.isoformat(),
             sale.sales_volume, sale.price, sale.ad_budget),
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def update(self, sale: Sale):
        conn = get_connection()
        conn.execute(
            "UPDATE sales SET product_id=?, period=?, sales_volume=?, price=?, ad_budget=? WHERE id=?",
            (sale.product_id, sale.period.isoformat(),
             sale.sales_volume, sale.price, sale.ad_budget, sale.id),
        )
        conn.commit()
        conn.close()

    def delete(self, sale_id: int):
        conn = get_connection()
        conn.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
        conn.commit()
        conn.close()
