from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QDateEdit, QDoubleSpinBox, QComboBox, QDialogButtonBox,
)
from PySide6.QtCore import QDate
from models.models import Company, Product, Sale


class CompanyDialog(QDialog):
    def __init__(self, parent=None, company: Company = None):
        super().__init__(parent)
        self.company = company
        self.setWindowTitle("Предприятие")
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.industry_input = QLineEdit()
        form.addRow("Название:", self.name_input)
        form.addRow("Отрасль:", self.industry_input)
        layout.addLayout(form)

        if company:
            self.name_input.setText(company.name)
            self.industry_input.setText(company.industry)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate(self):
        if not self.name_input.text().strip():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым")
            return
        if not self.industry_input.text().strip():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Отрасль не может быть пустой")
            return
        self.accept()

    def get_company(self) -> Company:
        return Company(
            id=self.company.id if self.company else None,
            name=self.name_input.text().strip(),
            industry=self.industry_input.text().strip(),
        )


class ProductDialog(QDialog):
    def __init__(self, parent=None, product: Product = None, companies=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Товар")
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.company_combo = QComboBox()
        if companies:
            for c in companies:
                self.company_combo.addItem(c.name, c.id)
        self.name_input = QLineEdit()
        form.addRow("Предприятие:", self.company_combo)
        form.addRow("Название:", self.name_input)
        layout.addLayout(form)

        if product:
            idx = self.company_combo.findData(product.company_id)
            if idx >= 0:
                self.company_combo.setCurrentIndex(idx)
            self.name_input.setText(product.name)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate(self):
        if not self.name_input.text().strip():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым")
            return
        self.accept()

    def get_product(self) -> Product:
        return Product(
            id=self.product.id if self.product else None,
            company_id=self.company_combo.currentData(),
            name=self.name_input.text().strip(),
        )


class SaleDialog(QDialog):
    def __init__(self, parent=None, sale: Sale = None, products=None):
        super().__init__(parent)
        self.sale = sale
        self.setWindowTitle("Продажа")
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.product_combo = QComboBox()
        if products:
            for p in products:
                self.product_combo.addItem(f"{p.id} - {p.name}", p.id)
        self.period_input = QDateEdit()
        self.period_input.setCalendarPopup(True)
        self.period_input.setDate(QDate.currentDate())
        self.volume_input = QDoubleSpinBox()
        self.volume_input.setRange(0, 1e9)
        self.volume_input.setDecimals(2)
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1e9)
        self.price_input.setDecimals(2)
        self.ad_input = QDoubleSpinBox()
        self.ad_input.setRange(0, 1e9)
        self.ad_input.setDecimals(2)

        form.addRow("Товар:", self.product_combo)
        form.addRow("Период:", self.period_input)
        form.addRow("Объем продаж:", self.volume_input)
        form.addRow("Цена:", self.price_input)
        form.addRow("Рекламный бюджет:", self.ad_input)
        layout.addLayout(form)

        if sale:
            idx = self.product_combo.findData(sale.product_id)
            if idx >= 0:
                self.product_combo.setCurrentIndex(idx)
            self.period_input.setDate(QDate(sale.period.year, sale.period.month, sale.period.day))
            self.volume_input.setValue(sale.sales_volume)
            self.price_input.setValue(sale.price)
            self.ad_input.setValue(sale.ad_budget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate(self):
        if self.volume_input.value() <= 0:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Объем продаж должен быть больше 0")
            return
        self.accept()

    def get_sale(self) -> Sale:
        qd = self.period_input.date()
        return Sale(
            id=self.sale.id if self.sale else None,
            product_id=self.product_combo.currentData(),
            period=qd.toPython(),
            sales_volume=self.volume_input.value(),
            price=self.price_input.value(),
            ad_budget=self.ad_input.value(),
        )
