# Информационная система прогнозирования доли рынка

Система для хранения данных о предприятиях и товарах, учета продаж, расчета и прогнозирования доли рынка с визуализацией результатов.

## Функциональные возможности

- **Управление предприятиями** — добавление, редактирование, удаление, поиск
- **Управление товарами** — привязка к предприятиям, CRUD-операции
- **Учет продаж** — ввод, изменение, удаление записей, фильтрация по периоду
- **Расчет доли рынка** — вычисление общей емкости рынка и доли каждого предприятия
- **Прогнозирование** — обучение модели линейной регрессии, прогноз на следующий период, расчет MAE/RMSE
- **Визуализация** — графики продаж, долей рынка, прогнозов
- **PDF-отчеты** — формирование отчета со всеми данными и графиками

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <url-репозитория>
cd market-share-forecasting-app
```

### 2. Создание виртуального окружения

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate     # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Заполнение тестовыми данными (опционально)

```bash
python seed_data.py
```

### 5. Запуск приложения

```bash
python main.py
```

## Структура проекта

```
market-share-forecasting-app/
├── main.py                  # Точка входа
├── seed_data.py             # Скрипт заполнения тестовыми данными
├── requirements.txt         # Зависимости
├── database/
│   ├── db.py                # Подключение к БД, инициализация схемы
│   ├── company_repository.py
│   ├── product_repository.py
│   ├── sales_repository.py
│   └── marketshare_repository.py
├── models/
│   └── models.py            # Data-классы сущностей
├── analytics/
│   ├── market_share_service.py   # Расчет доли рынка
│   ├── prediction_service.py     # Обучение и прогнозирование
│   └── metrics_service.py        # MAE, RMSE
├── ui/
│   ├── main_window.py       # Главное окно с вкладками
│   ├── company_widget.py
│   ├── product_widget.py
│   ├── sales_widget.py
│   ├── market_share_widget.py
│   ├── prediction_widget.py
│   ├── analytics_widget.py  # Графики (matplotlib)
│   └── dialogs.py           # Диалоги ввода
└── reports/
    └── report_generator.py  # Формирование PDF-отчета
```

## Используемые технологии

- **Python 3.13** — язык программирования
- **PySide6** — графический интерфейс
- **SQLite** — база данных
- **pandas / numpy** — анализ данных
- **scikit-learn** — машинное обучение (линейная регрессия)
- **matplotlib** — визуализация
- **reportlab** — формирование PDF-отчетов

## База данных

Используется SQLite. Файл БД (`data.db`) создается автоматически в корне проекта при первом запуске.

### Схема БД

- **companies** — предприятия (id, name, industry)
- **products** — товары (id, company_id, name)
- **sales** — продажи (id, product_id, period, sales_volume, price, ad_budget)
- **market_share** — доля рынка (id, company_id, period, market_share)

## Системные требования

- Python 3.13+
- ОС: Windows, macOS, Linux
