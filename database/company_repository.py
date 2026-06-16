from typing import List, Optional
from database.db import get_connection
from models.models import Company


class CompanyRepository:

    def get_all(self) -> List[Company]:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM companies ORDER BY id").fetchall()
        conn.close()
        return [Company(id=r["id"], name=r["name"], industry=r["industry"]) for r in rows]

    def get_by_id(self, company_id: int) -> Optional[Company]:
        conn = get_connection()
        row = conn.execute("SELECT * FROM companies WHERE id = ?", (company_id,)).fetchone()
        conn.close()
        if row:
            return Company(id=row["id"], name=row["name"], industry=row["industry"])
        return None

    def search(self, query: str) -> List[Company]:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM companies ORDER BY id").fetchall()
        conn.close()
        query_lower = query.lower()
        result = []
        for r in rows:
            if query_lower in r["name"].lower() or query_lower in r["industry"].lower():
                result.append(Company(id=r["id"], name=r["name"], industry=r["industry"]))
        return result

    def add(self, company: Company) -> int:
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO companies (name, industry) VALUES (?, ?)",
            (company.name, company.industry),
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def update(self, company: Company):
        conn = get_connection()
        conn.execute(
            "UPDATE companies SET name = ?, industry = ? WHERE id = ?",
            (company.name, company.industry, company.id),
        )
        conn.commit()
        conn.close()

    def delete(self, company_id: int):
        conn = get_connection()
        conn.execute("DELETE FROM companies WHERE id = ?", (company_id,))
        conn.commit()
        conn.close()
