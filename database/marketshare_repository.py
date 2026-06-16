from typing import List, Optional
from datetime import date
from database.db import get_connection
from models.models import MarketShare


class MarketShareRepository:

    def get_by_company(self, company_id: int) -> List[MarketShare]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM market_share WHERE company_id = ? ORDER BY period", (company_id,)
        ).fetchall()
        conn.close()
        return [MarketShare(id=r["id"], company_id=r["company_id"],
                            period=date.fromisoformat(r["period"]),
                            market_share=r["market_share"]) for r in rows]

    def get_by_period(self, period: date) -> List[MarketShare]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM market_share WHERE period = ?", (period.isoformat(),)
        ).fetchall()
        conn.close()
        return [MarketShare(id=r["id"], company_id=r["company_id"],
                            period=date.fromisoformat(r["period"]),
                            market_share=r["market_share"]) for r in rows]

    def get_all_periods(self) -> List[date]:
        conn = get_connection()
        rows = conn.execute("SELECT DISTINCT period FROM market_share ORDER BY period").fetchall()
        conn.close()
        return [date.fromisoformat(r["period"]) for r in rows]

    def get_all(self) -> List[MarketShare]:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM market_share ORDER BY period").fetchall()
        conn.close()
        return [MarketShare(id=r["id"], company_id=r["company_id"],
                            period=date.fromisoformat(r["period"]),
                            market_share=r["market_share"]) for r in rows]

    def add(self, ms: MarketShare) -> int:
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO market_share (company_id, period, market_share) VALUES (?, ?, ?)",
            (ms.company_id, ms.period.isoformat(), ms.market_share),
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def clear_period(self, period: date):
        conn = get_connection()
        conn.execute("DELETE FROM market_share WHERE period = ?", (period.isoformat(),))
        conn.commit()
        conn.close()

    def delete(self, ms_id: int):
        conn = get_connection()
        conn.execute("DELETE FROM market_share WHERE id = ?", (ms_id,))
        conn.commit()
        conn.close()
