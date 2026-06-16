from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QMessageBox, QHeaderView, QLabel,
)
from database.company_repository import CompanyRepository
from models.models import Company
from ui.dialogs import CompanyDialog


class CompanyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = CompanyRepository()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Название или отрасль...")
        self.search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Отрасль"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
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

    def _load_data(self, query: str = ""):
        if query:
            companies = self.repo.search(query)
        else:
            companies = self.repo.get_all()
        self.table.setRowCount(len(companies))
        for i, c in enumerate(companies):
            self.table.setItem(i, 0, QTableWidgetItem(str(c.id)))
            self.table.setItem(i, 1, QTableWidgetItem(c.name))
            self.table.setItem(i, 2, QTableWidgetItem(c.industry))

    def _on_search(self):
        self._load_data(self.search_input.text().strip())

    def _get_selected_company(self):
        rows = self.table.selectedItems()
        if not rows:
            QMessageBox.warning(self, "Внимание", "Выберите предприятие")
            return None
        row = rows[0].row()
        company_id = int(self.table.item(row, 0).text())
        return self.repo.get_by_id(company_id)

    def _on_add(self):
        dialog = CompanyDialog(self)
        if dialog.exec():
            self.repo.add(dialog.get_company())
            self._load_data(self.search_input.text().strip())

    def _on_edit(self):
        company = self._get_selected_company()
        if not company:
            return
        dialog = CompanyDialog(self, company)
        if dialog.exec():
            self.repo.update(dialog.get_company())
            self._load_data(self.search_input.text().strip())

    def _on_delete(self):
        company = self._get_selected_company()
        if not company:
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить предприятие '{company.name}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.repo.delete(company.id)
            self._load_data(self.search_input.text().strip())
