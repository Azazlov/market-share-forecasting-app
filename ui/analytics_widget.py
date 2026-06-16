from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QPushButton, QFileDialog,
    QHBoxLayout,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use("Qt5Agg")
from database.sales_repository import SalesRepository
from database.marketshare_repository import MarketShareRepository
from database.company_repository import CompanyRepository
from database.product_repository import ProductRepository
import pandas as pd
import numpy as np


class PlotWidget(QWidget):
    def __init__(self, title: str):
        super().__init__()
        self.title = title
        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        btn_layout = QHBoxLayout()
        self.btn_export = QPushButton("Экспорт графика")
        self.btn_export.clicked.connect(self._export)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_export)
        layout.addLayout(btn_layout)

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить график", "", "PNG (*.png);;PDF (*.pdf)"
        )
        if path:
            self.figure.savefig(path, dpi=150, bbox_inches="tight")

    def clear(self):
        self.figure.clear()
        self.canvas.draw()


class SalesPlotWidget(PlotWidget):
    def __init__(self):
        super().__init__("Продажи компаний")
        self.sales_repo = SalesRepository()
        self.product_repo = ProductRepository()
        self.company_repo = CompanyRepository()

    def refresh(self):
        self.clear()
        sales = self.sales_repo.get_all()
        if not sales:
            return
        products = {p.id: p.company_id for p in self.product_repo.get_all()}
        companies = {c.id: c.name for c in self.company_repo.get_all()}

        df = pd.DataFrame([{
            "period": s.period,
            "company_id": products.get(s.product_id),
            "volume": s.sales_volume,
        } for s in sales if s.product_id in products])

        if df.empty:
            return

        grouped = df.groupby(["period", "company_id"])["volume"].sum().reset_index()
        ax = self.figure.add_subplot(111)
        for cid in grouped["company_id"].unique():
            data = grouped[grouped["company_id"] == cid]
            ax.plot(data["period"], data["volume"], marker="o", label=companies.get(cid, str(cid)))
        ax.set_title("Продажи компаний")
        ax.set_xlabel("Период")
        ax.set_ylabel("Объем продаж")
        ax.legend()
        ax.tick_params(axis="x", rotation=45)
        self.figure.tight_layout()
        self.canvas.draw()


class MarketSharePlotWidget(PlotWidget):
    def __init__(self):
        super().__init__("Доля рынка")
        self.marketshare_repo = MarketShareRepository()
        self.company_repo = CompanyRepository()

    def refresh(self):
        self.clear()
        records = self.marketshare_repo.get_all()
        if not records:
            return
        companies = {c.id: c.name for c in self.company_repo.get_all()}
        df = pd.DataFrame([{
            "period": r.period,
            "company_id": r.company_id,
            "share": r.market_share,
        } for r in records])

        ax = self.figure.add_subplot(111)
        for cid in df["company_id"].unique():
            data = df[df["company_id"] == cid]
            ax.plot(data["period"], data["share"] * 100, marker="s", label=companies.get(cid, str(cid)))
        ax.set_title("Доля рынка")
        ax.set_xlabel("Период")
        ax.set_ylabel("Доля (%)")
        ax.legend()
        ax.tick_params(axis="x", rotation=45)
        self.figure.tight_layout()
        self.canvas.draw()


class PredictionPlotWidget(PlotWidget):
    def __init__(self):
        super().__init__("Прогноз доли рынка")
        self._data = None

    def set_data(self, result, company_name):
        self._data = (result, company_name)
        self.refresh()

    def refresh(self):
        self.clear()
        if not self._data:
            return
        result, company_name = self._data
        ax = self.figure.add_subplot(111)

        train = result["train"]
        test = result["test"]
        fc = result["forecast"]

        train_periods = [pd.Timestamp(p) for p in train["periods"]]
        test_periods = [pd.Timestamp(p) for p in test["periods"]]
        fc_period = pd.Timestamp(fc["next_period"])

        ax.plot(train_periods, np.array(train["actual"]) * 100, "bo-",
                label="Факт (обучение)", markersize=5)
        ax.plot(train_periods, np.array(train["predicted"]) * 100, "bx--",
                label="Прогноз (обучение)", markersize=4, alpha=0.7)

        if test["periods"]:
            ax.plot(test_periods, np.array(test["actual"]) * 100, "go-",
                    label="Факт (тест)", markersize=6)
            ax.plot(test_periods, np.array(test["predicted"]) * 100, "ro-",
                    label="Прогноз (тест)", markersize=6)

        fc_val = fc["predicted_share"] * 100
        ci_l = fc["ci_lower"] * 100
        ci_u = fc["ci_upper"] * 100

        ax.plot([fc_period], [fc_val], "D", color="purple",
                markersize=8, label="Прогноз", zorder=5)
        ax.vlines(fc_period, ci_l, ci_u, color="purple", linewidth=3,
                  alpha=0.5, label="95% дов. интервал")

        y_min = min(
            np.min(train["actual"]) * 100,
            np.min(test["actual"]) * 100 if test["periods"] else 100,
            ci_l,
        ) - 2
        y_max = max(
            np.max(train["actual"]) * 100,
            np.max(test["actual"]) * 100 if test["periods"] else 0,
            ci_u,
        ) + 2
        ax.set_ylim(y_min, y_max)

        ax.set_title(f"Прогноз доли рынка: {company_name}")
        ax.set_xlabel("Период")
        ax.set_ylabel("Доля рынка (%)")
        ax.legend(fontsize=8)
        ax.tick_params(axis="x", rotation=45)
        self.figure.tight_layout()
        self.canvas.draw()


class AnalyticsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        self.sales_plot = SalesPlotWidget()
        self.share_plot = MarketSharePlotWidget()
        self.prediction_plot = PredictionPlotWidget()

        self.tabs.addTab(self.sales_plot, "Продажи")
        self.tabs.addTab(self.share_plot, "Доля рынка")
        self.tabs.addTab(self.prediction_plot, "Прогноз")

        layout.addWidget(self.tabs)

        self.btn_refresh = QPushButton("Обновить графики")
        self.btn_refresh.clicked.connect(self.refresh)
        layout.addWidget(self.btn_refresh)

    def refresh(self):
        self.sales_plot.refresh()
        self.share_plot.refresh()
        self.prediction_plot.refresh()
