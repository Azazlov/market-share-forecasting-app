from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMenuBar, QMenu, QMessageBox, QFileDialog,
)
from PySide6.QtGui import QAction
from ui.company_widget import CompanyWidget
from ui.product_widget import ProductWidget
from ui.sales_widget import SalesWidget
from ui.market_share_widget import MarketShareWidget
from ui.prediction_widget import PredictionWidget
from ui.analytics_widget import AnalyticsWidget
from reports.report_generator import ReportGenerator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Прогнозирование доли рынка")
        self.resize(1024, 720)

        self.tabs = QTabWidget()
        self.company_widget = CompanyWidget()
        self.product_widget = ProductWidget()
        self.sales_widget = SalesWidget()
        self.market_share_widget = MarketShareWidget()
        self.prediction_widget = PredictionWidget()
        self.analytics_widget = AnalyticsWidget()

        self.tabs.addTab(self.company_widget, "Предприятия")
        self.tabs.addTab(self.product_widget, "Товары")
        self.tabs.addTab(self.sales_widget, "Продажи")
        self.tabs.addTab(self.market_share_widget, "Доля рынка")
        self.tabs.addTab(self.prediction_widget, "Прогнозирование")
        self.tabs.addTab(self.analytics_widget, "Аналитика")
        self.tabs.currentChanged.connect(self._on_tab_changed)

        self.prediction_widget.training_completed.connect(self._on_training_completed)

        self.setCentralWidget(self.tabs)
        self._create_menu()

    def _create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")
        report_action = QAction("Сформировать PDF-отчет", self)
        report_action.triggered.connect(self._generate_report)
        file_menu.addAction(report_action)
        file_menu.addSeparator()
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("Справка")
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _on_tab_changed(self, index):
        widget = self.tabs.widget(index)
        if hasattr(widget, "refresh"):
            widget.refresh()

    def _generate_report(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить отчет", "report.pdf", "PDF (*.pdf)"
        )
        if path:
            try:
                generator = ReportGenerator()
                generator.generate(path)
                QMessageBox.information(self, "Успех", f"Отчет сохранен: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сформировать отчет: {e}")

    def _on_training_completed(self, result, company_name):
        self.analytics_widget.prediction_plot.set_data(result, company_name)

    def _show_about(self):
        QMessageBox.about(
            self, "О программе",
            "Информационная система прогнозирования доли рынка\n\n"
            "Версия 1.0\n"
            "Разработано с использованием PySide6, scikit-learn, matplotlib"
        )
