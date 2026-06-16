import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
)
from database.company_repository import CompanyRepository
from database.product_repository import ProductRepository
from database.sales_repository import SalesRepository
from database.marketshare_repository import MarketShareRepository
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date


class ReportGenerator:

    def __init__(self):
        self.company_repo = CompanyRepository()
        self.product_repo = ProductRepository()
        self.sales_repo = SalesRepository()
        self.marketshare_repo = MarketShareRepository()
        self.styles = getSampleStyleSheet()

    def generate(self, path: str):
        doc = SimpleDocTemplate(path, pagesize=A4)
        elements = []

        elements.append(Paragraph("Отчет по доле рынка", self.styles["Title"]))
        elements.append(Spacer(1, 12))

        # Companies
        elements.append(Paragraph("Предприятия", self.styles["Heading2"]))
        companies = self.company_repo.get_all()
        data = [["ID", "Название", "Отрасль"]]
        for c in companies:
            data.append([str(c.id), c.name, c.industry])
        t = Table(data)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

        # Sales
        elements.append(Paragraph("Продажи", self.styles["Heading2"]))
        sales = self.sales_repo.get_all()
        if sales:
            data = [["ID", "ID товара", "Период", "Объем", "Цена", "Рекл. бюджет"]]
            for s in sales[:20]:
                data.append([
                    str(s.id), str(s.product_id), str(s.period),
                    f"{s.sales_volume:.2f}", f"{s.price:.2f}", f"{s.ad_budget:.2f}",
                ])
            if len(sales) > 20:
                data.append(["...", "...", "...", "...", "...", "..."])
            t = Table(data)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]))
            elements.append(t)
        else:
            elements.append(Paragraph("Нет данных о продажах", self.styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Market Share
        elements.append(Paragraph("Доля рынка", self.styles["Heading2"]))
        shares = self.marketshare_repo.get_all()
        if shares:
            companies_map = {c.id: c.name for c in self.company_repo.get_all()}
            data = [["ID", "Предприятие", "Период", "Доля"]]
            for ms in shares:
                data.append([
                    str(ms.id),
                    companies_map.get(ms.company_id, "?"),
                    str(ms.period),
                    f"{ms.market_share * 100:.2f}%",
                ])
            t = Table(data)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(t)
        else:
            elements.append(Paragraph("Доля рынка еще не рассчитана", self.styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Build chart images
        img_buf = self._build_sales_chart()
        if img_buf:
            elements.append(Paragraph("График продаж", self.styles["Heading2"]))
            elements.append(Image(img_buf, width=400, height=200))
            elements.append(Spacer(1, 12))

        img_buf2 = self._build_share_chart()
        if img_buf2:
            elements.append(Paragraph("График доли рынка", self.styles["Heading2"]))
            elements.append(Image(img_buf2, width=400, height=200))

        doc.build(elements)

    def _build_sales_chart(self):
        sales = self.sales_repo.get_all()
        products = self.product_repo.get_all()
        companies = self.company_repo.get_all()
        if not sales or not products:
            return None

        products_map = {p.id: p.company_id for p in products}
        companies_map = {c.id: c.name for c in companies}

        df = pd.DataFrame([{
            "period": s.period,
            "company_id": products_map.get(s.product_id),
            "volume": s.sales_volume,
        } for s in sales if s.product_id in products_map])

        if df.empty:
            return None

        grouped = df.groupby(["period", "company_id"])["volume"].sum().reset_index()
        fig, ax = plt.subplots(figsize=(8, 4))
        for cid in grouped["company_id"].unique():
            data = grouped[grouped["company_id"] == cid]
            ax.plot(data["period"], data["volume"], marker="o", label=companies_map.get(cid, str(cid)))
        ax.set_title("Продажи компаний")
        ax.set_xlabel("Период")
        ax.set_ylabel("Объем продаж")
        ax.legend()
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=100)
        plt.close(fig)
        buf.seek(0)
        return buf

    def _build_share_chart(self):
        records = self.marketshare_repo.get_all()
        companies = self.company_repo.get_all()
        if not records:
            return None

        companies_map = {c.id: c.name for c in companies}

        df = pd.DataFrame([{
            "period": r.period,
            "company_id": r.company_id,
            "share": r.market_share,
        } for r in records])

        fig, ax = plt.subplots(figsize=(8, 4))
        for cid in df["company_id"].unique():
            data = df[df["company_id"] == cid]
            ax.plot(data["period"], data["share"] * 100, marker="s", label=companies_map.get(cid, str(cid)))
        ax.set_title("Доля рынка")
        ax.set_xlabel("Период")
        ax.set_ylabel("Доля (%)")
        ax.legend()
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=100)
        plt.close(fig)
        buf.seek(0)
        return buf
