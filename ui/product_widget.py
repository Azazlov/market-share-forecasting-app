from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QLabel, QComboBox,
)
from database.product_repository import ProductRepository
from database.company_repository import CompanyRepository
from models.models import Product
from ui.dialogs import ProductDialog


class ProductWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = ProductRepository()
        self.company_repo = CompanyRepository()
        self._setup_ui()
        self._load_companies()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Предприятие:"))
        self.company_combo = QComboBox()
        self.company_combo.currentIndexChanged.connect(self._on_company_changed)
        filter_layout.addWidget(self.company_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "ID предприятия", "Название"])
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

    def _load_companies(self):
        companies = self.company_repo.get_all()
        self.company_combo.clear()
        self.company_combo.addItem("Все предприятия", 0)
        for c in companies:
            self.company_combo.addItem(c.name, c.id)

    def _on_company_changed(self):
        self._load_data()

    def refresh(self):
        self._load_companies()
        self._load_data()

    def _load_data(self):
        company_id = self.company_combo.currentData()
        if company_id:
            products = self.repo.get_by_company(company_id)
        else:
            products = self.repo.get_all()

        self.table.setRowCount(len(products))
        for i, p in enumerate(products):
            self.table.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(i, 1, QTableWidgetItem(str(p.company_id)))
            self.table.setItem(i, 2, QTableWidgetItem(p.name))

    def _get_selected_product(self):
        rows = self.table.selectedItems()
        if not rows:
            QMessageBox.warning(self, "Внимание", "Выберите товар")
            return None
        row = rows[0].row()
        product_id = int(self.table.item(row, 0).text())
        return self.repo.get_by_id(product_id)

    def _on_add(self):
        companies = self.company_repo.get_all()
        if not companies:
            QMessageBox.warning(self, "Ошибка", "Сначала добавьте предприятия")
            return
        dialog = ProductDialog(self, companies=companies)
        if dialog.exec():
            self.repo.add(dialog.get_product())
            self._load_data()

    def _on_edit(self):
        product = self._get_selected_product()
        if not product:
            return
        companies = self.company_repo.get_all()
        dialog = ProductDialog(self, product, companies)
        if dialog.exec():
            self.repo.update(dialog.get_product())
            self._load_data()

    def _on_delete(self):
        product = self._get_selected_product()
        if not product:
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить товар '{product.name}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.repo.delete(product.id)
            self._load_data()
