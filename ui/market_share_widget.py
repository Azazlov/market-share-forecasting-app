from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QDateEdit, QMessageBox,
)
from PySide6.QtCore import QDate
from analytics.market_share_service import MarketShareService
from database.company_repository import CompanyRepository
from datetime import date


class MarketShareWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.service = MarketShareService()
        self.company_repo = CompanyRepository()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        calc_layout = QHBoxLayout()
        calc_layout.addWidget(QLabel("С:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-3))
        calc_layout.addWidget(self.start_date)

        calc_layout.addWidget(QLabel("По:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        calc_layout.addWidget(self.end_date)

        self.btn_calculate = QPushButton("Рассчитать долю рынка")
        self.btn_calculate.clicked.connect(self._on_calculate)
        calc_layout.addWidget(self.btn_calculate)
        calc_layout.addStretch()
        layout.addLayout(calc_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Предприятие", "Период", "Доля рынка"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self._refresh)
        layout.addWidget(self.btn_refresh)

    def _on_calculate(self):
        start = self.start_date.date().toPython()
        end = self.end_date.date().toPython()
        try:
            total = 0
            year = start.year
            month = start.month
            while date(year, month, 1) <= end:
                period = date(year, month, 1)
                results = self.service.calculate(period)
                total += len(results)
                month += 1
                if month > 12:
                    month = 1
                    year += 1
            if total == 0:
                QMessageBox.information(self, "Результат", "Нет данных о продажах за выбранный период")
            self._display_results()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _display_results(self):
        records = self.service.get_all()
        companies = {c.id: c.name for c in self.company_repo.get_all()}

        self.table.setRowCount(len(records))
        for i, r in enumerate(records):
            self.table.setItem(i, 0, QTableWidgetItem(str(r["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(companies.get(r["company_id"], "?")))
            self.table.setItem(i, 2, QTableWidgetItem(r["period"].isoformat()))
            self.table.setItem(i, 3, QTableWidgetItem(f"{r['market_share'] * 100:.2f}%"))

    def _refresh(self):
        self._display_results()

    def refresh(self):
        self._refresh()
