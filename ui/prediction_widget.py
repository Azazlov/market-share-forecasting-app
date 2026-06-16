from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QLabel, QComboBox,
    QGroupBox, QFormLayout, QTabWidget,
)
from PySide6.QtCore import Signal
from database.company_repository import CompanyRepository
from analytics.prediction_service import PredictionService


class PredictionWidget(QWidget):
    training_completed = Signal(dict, str)

    def __init__(self):
        super().__init__()
        self.company_repo = CompanyRepository()
        self.service = PredictionService()
        self._last_result = None
        self._setup_ui()
        self._load_companies()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Предприятие:"))
        self.company_combo = QComboBox()
        select_layout.addWidget(self.company_combo)
        select_layout.addStretch()
        layout.addLayout(select_layout)

        btn_layout = QHBoxLayout()
        self.btn_train = QPushButton("Обучить модель")
        self.btn_predict = QPushButton("Прогноз на следующий период")
        self.btn_predict.setEnabled(False)
        self.btn_train.clicked.connect(self._on_train)
        self.btn_predict.clicked.connect(self._on_predict)
        btn_layout.addWidget(self.btn_train)
        btn_layout.addWidget(self.btn_predict)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        metrics_group = QGroupBox("Метрики модели")
        metrics_form = QFormLayout()
        self.lbl_train_mae = QLabel("—")
        self.lbl_train_rmse = QLabel("—")
        self.lbl_test_mae = QLabel("—")
        self.lbl_test_rmse = QLabel("—")
        metrics_form.addRow("Train MAE:", self.lbl_train_mae)
        metrics_form.addRow("Train RMSE:", self.lbl_train_rmse)
        metrics_form.addRow("Test MAE:", self.lbl_test_mae)
        metrics_form.addRow("Test RMSE:", self.lbl_test_rmse)
        metrics_group.setLayout(metrics_form)
        layout.addWidget(metrics_group)

        forecast_group = QGroupBox("Прогноз на следующий период")
        forecast_form = QFormLayout()
        self.lbl_next_period = QLabel("—")
        self.lbl_predicted_share = QLabel("—")
        self.lbl_ci = QLabel("—")
        forecast_form.addRow("Период:", self.lbl_next_period)
        forecast_form.addRow("Прогноз доли:", self.lbl_predicted_share)
        forecast_form.addRow("95% дов. интервал:", self.lbl_ci)
        forecast_group.setLayout(forecast_form)
        layout.addWidget(forecast_group)

        table_tabs = QTabWidget()
        self.train_table = QTableWidget()
        self.train_table.setColumnCount(3)
        self.train_table.setHorizontalHeaderLabels(["Период", "Факт", "Прогноз (обучение)"])
        self.train_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.train_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.test_table = QTableWidget()
        self.test_table.setColumnCount(3)
        self.test_table.setHorizontalHeaderLabels(["Период", "Факт", "Прогноз (тест)"])
        self.test_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.test_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        table_tabs.addTab(self.train_table, "Обучающая выборка")
        table_tabs.addTab(self.test_table, "Тестовая выборка")
        layout.addWidget(table_tabs)

    def _load_companies(self):
        companies = self.company_repo.get_all()
        self.company_combo.clear()
        for c in companies:
            self.company_combo.addItem(c.name, c.id)

    def refresh(self):
        self._load_companies()

    def _fill_table(self, table, periods, actual, predicted):
        table.setRowCount(len(periods))
        for i in range(len(periods)):
            table.setItem(i, 0, QTableWidgetItem(periods[i]))
            table.setItem(i, 1, QTableWidgetItem(f"{actual[i] * 100:.2f}%"))
            table.setItem(i, 2, QTableWidgetItem(f"{predicted[i] * 100:.2f}%"))

    def _on_train(self):
        company_id = self.company_combo.currentData()
        if not company_id:
            QMessageBox.warning(self, "Ошибка", "Выберите предприятие")
            return

        try:
            result = self.service.train(company_id)
            self._last_result = result

            train = result["train"]
            test = result["test"]

            self.lbl_train_mae.setText(f"{result['train_mae']:.6f}")
            self.lbl_train_rmse.setText(f"{result['train_rmse']:.6f}")
            self.lbl_test_mae.setText(f"{result['test_mae']:.6f}")
            self.lbl_test_rmse.setText(f"{result['test_rmse']:.6f}")

            self._fill_table(self.train_table, train["periods"], train["actual"], train["predicted"])
            self._fill_table(self.test_table, test["periods"], test["actual"], test["predicted"])

            fc = result["forecast"]
            self.lbl_next_period.setText(fc["next_period"])
            self.lbl_predicted_share.setText(f"{fc['predicted_share'] * 100:.2f}%")
            self.lbl_ci.setText(
                f"{fc['ci_lower'] * 100:.2f}% — {fc['ci_upper'] * 100:.2f}%"
            )
            self.btn_predict.setEnabled(True)

            company_name = self.company_combo.currentText()
            self.training_completed.emit(result, company_name)

            QMessageBox.information(self, "Успех", "Модель обучена")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обучить модель: {e}")

    def _on_predict(self):
        company_id = self.company_combo.currentData()
        if not company_id:
            QMessageBox.warning(self, "Ошибка", "Выберите предприятие")
            return

        try:
            result = self.service.predict_next(company_id)
            self.lbl_next_period.setText(result.get("next_period", "—"))
            self.lbl_predicted_share.setText(f"{result['predicted_share'] * 100:.2f}%")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
