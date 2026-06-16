from typing import List, Optional
from database.db import get_connection
from models.models import Product


class ProductRepository:

    def get_by_company(self, company_id: int) -> List[Product]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM products WHERE company_id = ? ORDER BY id", (company_id,)
        ).fetchall()
        conn.close()
        return [Product(id=r["id"], company_id=r["company_id"], name=r["name"]) for r in rows]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        conn = get_connection()
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        conn.close()
        if row:
            return Product(id=row["id"], company_id=row["company_id"], name=row["name"])
        return None

    def get_all(self) -> List[Product]:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
        conn.close()
        return [Product(id=r["id"], company_id=r["company_id"], name=r["name"]) for r in rows]

    def add(self, product: Product) -> int:
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO products (company_id, name) VALUES (?, ?)",
            (product.company_id, product.name),
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def update(self, product: Product):
        conn = get_connection()
        conn.execute(
            "UPDATE products SET company_id = ?, name = ? WHERE id = ?",
            (product.company_id, product.name, product.id),
        )
        conn.commit()
        conn.close()

    def delete(self, product_id: int):
        conn = get_connection()
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
