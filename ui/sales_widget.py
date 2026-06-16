from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QLabel, QDateEdit,
    QComboBox,
)
from PySide6.QtCore import QDate
from database.sales_repository import SalesRepository
from database.product_repository import ProductRepository
from models.models import Sale
from ui.dialogs import SaleDialog
from datetime import date


class SalesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = SalesRepository()
        self.product_repo = ProductRepository()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("С:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addYears(-1))
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("По:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date)

        self.btn_filter = QPushButton("Фильтр")
        self.btn_filter.clicked.connect(self._load_data)
        self.btn_reset = QPushButton("Сброс")
        self.btn_reset.clicked.connect(self._reset_filter)
        filter_layout.addWidget(self.btn_filter)
        filter_layout.addWidget(self.btn_reset)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.product_combo = QComboBox()
        self.product_combo.addItem("Все товары", 0)
        layout.addWidget(self.product_combo)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "ID товара", "Период", "Объем продаж", "Цена", "Рекламный бюджет"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.setColumnHidden(1, True)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Изменить")
        self.btn_delete = QPushButton("Удалить")
        self.btn_add.clicked.connect(self._on_add)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_delete.clicked.connect(self._on_delete)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def refresh(self):
        self._load_products()
        self._load_data()

    def _load_products(self):
        products = self.product_repo.get_all()
        self.product_combo.clear()
        self.product_combo.addItem("Все товары", 0)
        for p in products:
            self.product_combo.addItem(f"{p.id} - {p.name}", p.id)

    def _load_data(self):
        start = self.start_date.date().toPython()
        end = self.end_date.date().toPython()

        if self.product_combo.currentData():
            sales = [s for s in self.repo.get_by_period(start, end)
                     if s.product_id == self.product_combo.currentData()]
        else:
            sales = self.repo.get_by_period(start, end)

        self.table.setRowCount(len(sales))
        for i, s in enumerate(sales):
            self.table.setItem(i, 0, QTableWidgetItem(str(s.id)))
            self.table.setItem(i, 1, QTableWidgetItem(str(s.product_id)))
            self.table.setItem(i, 2, QTableWidgetItem(s.period.isoformat()))
            self.table.setItem(i, 3, QTableWidgetItem(f"{s.sales_volume:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{s.price:.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{s.ad_budget:.2f}"))

    def _reset_filter(self):
        self.start_date.setDate(QDate.currentDate().addYears(-1))
        self.end_date.setDate(QDate.currentDate())
        self.product_combo.setCurrentIndex(0)
        self._load_data()

    def _get_selected_sale(self):
        rows = self.table.selectedItems()
        if not rows:
            QMessageBox.warning(self, "Внимание", "Выберите продажу")
            return None
        row = rows[0].row()
        sale_id = int(self.table.item(row, 0).text())
        return self.repo.get_by_id(sale_id)

    def _on_add(self):
        products = self.product_repo.get_all()
        if not products:
            QMessageBox.warning(self, "Ошибка", "Сначала добавьте товары")
            return
        dialog = SaleDialog(self, products=products)
        if dialog.exec():
            self.repo.add(dialog.get_sale())
            self._load_data()

    def _on_edit(self):
        sale = self._get_selected_sale()
        if not sale:
            return
        products = self.product_repo.get_all()
        dialog = SaleDialog(self, sale, products)
        if dialog.exec():
            self.repo.update(dialog.get_sale())
            self._load_data()

    def _on_delete(self):
        sale = self._get_selected_sale()
        if not sale:
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить продажу от {sale.period}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.repo.delete(sale.id)
            self._load_data()
