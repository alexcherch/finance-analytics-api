import json
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from src.utils import filter_transactions_by_date, glob_load_transactions, load_user_settings

load_dotenv()


def get_greeting(date_time_str: str) -> str:
    """Возвращает приветствие в зависимости от часа переданной даты и времени."""
    try:
        dt = pd.to_datetime(date_time_str)
        hour = dt.hour
        if 6 <= hour < 12:
            return "Доброе утро"
        elif 12 <= hour < 18:
            return "Добрый день"
        elif 18 <= hour < 23:
            return "Добрый вечер"
        else:
            return "Доброй ночи"
    except (ValueError, TypeError):
        return "Добрый день"


def calculate_cards_info(transactions: list[dict]) -> list[dict]:
    """Группирует транзакции по картам, рассчитывает расходы и кэшбэк."""
    cards_data = {}

    for tx in transactions:
        status = str(tx.get("Статус", "")).strip().upper()
        if status not in ["OK", "ОК"]:
            continue

        card_number = tx.get("Номер карты")
        if not card_number or pd.isna(card_number):
            continue

        last_digits = str(card_number).strip()[-4:]

        amount = tx.get("Сумма платежа")
        if amount is None or not isinstance(amount, (int, float)):
            continue

        if amount < 0:
            spent_value = abs(amount)
            if last_digits not in cards_data:
                cards_data[last_digits] = 0.0
            cards_data[last_digits] += spent_value

    result = []
    for card, total_spent in cards_data.items():
        total_spent = round(total_spent, 2)
        cashback = round(total_spent / 100, 2)
        result.append({"last_digits": card, "total_spent": total_spent, "cashback": cashback})

    return result


def get_top_5_transactions(transactions: list[dict]) -> list[dict]:
    """Возвращает ровно 5 транзакций, отсортированных по убыванию суммы платежа (по модулю)."""
    valid_tx = [tx for tx in transactions if tx.get("Сумма платежа") is not None]
    sorted_tx = sorted(valid_tx, key=lambda x: abs(x["Сумма платежа"]), reverse=True)

    top_5 = []
    for tx in sorted_tx[:5]:
        date_raw = tx.get("Дата операции")
        try:
            formatted_date = str(date_raw).strip().split()[0]
        except (IndexError, ValueError, TypeError):
            formatted_date = str(date_raw)

        category = tx.get("Категория")
        if not category or pd.isna(category):
            category = "Остальное"

        top_5.append(
            {
                "date": formatted_date,
                "amount": round(tx["Сумма платежа"], 2),
                "category": category,
                "description": tx.get("Описание", ""),
            }
        )

    return top_5


def get_currency_rates(currencies: list[str]) -> list[dict]:
    """Получает актуальные курсы валют по отношению к рублю (RUB) через ExchangeRate-API."""
    mock_rates = {"USD": 73.21, "EUR": 87.08}
    api_key = os.getenv("EXCHANGE_API_KEY")

    if not api_key:
        return [{"currency": c, "rate": mock_rates.get(c, 75.0)} for c in currencies]

    result = []
    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/RUB"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            rates = response.json().get("conversion_rates", {})
            for currency in currencies:
                rate_to_rub = rates.get(currency)
                if rate_to_rub:
                    rub_price = round(1 / rate_to_rub, 2)
                    result.append({"currency": currency, "rate": float(rub_price)})
    except (requests.exceptions.RequestException, ValueError):
        pass

    if not result:
        return [{"currency": c, "rate": mock_rates.get(c, 75.0)} for c in currencies]
    return result


def get_stock_prices(stocks: list[str]) -> list[dict]:
    """Получает актуальную стоимость акций через API."""
    if not stocks:
        return []

    mock_prices = {"AAPL": 308.30, "AMZN": 180.15, "GOOGL": 152.30, "MSFT": 413.13, "TSLA": 170.80}
    api_key = os.getenv("STOCK_API_KEY")

    if not api_key:
        return [{"stock": s, "price": mock_prices.get(s, 100.0)} for s in stocks]

    result = []
    try:
        for stock in stocks:
            url = f"https://financialmodelingprep.com/stable/search-exchange-variants?symbol={stock}&apikey={api_key}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200 and response.json():
                data = response.json()
                if len(data) > 0:
                    price = data[0].get("price")
                    if price is not None:
                        result.append({"stock": stock, "price": float(round(float(price), 2))})
    except (requests.exceptions.RequestException, ValueError):
        pass

    if not result:
        return [{"stock": s, "price": mock_prices.get(s, 100.0)} for s in stocks]

    return result


def main_page_view(date_time_str: str) -> str:
    """Главная функция для генерации JSON-ответа для страницы 'Главная'."""
    greeting = get_greeting(date_time_str)

    base_dir = Path(__file__).resolve().parents[1]
    excel_path = base_dir / "data" / "operations.xlsx"

    settings = load_user_settings(str(base_dir / "user_settings.json"))
    currencies = settings.get("user_currencies", ["USD", "EUR"])
    stocks = settings.get("user_stocks", ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])

    all_transactions = glob_load_transactions(str(excel_path))
    filtered_transactions = filter_transactions_by_date(all_transactions, date_time_str)

    cards_info = calculate_cards_info(filtered_transactions)
    top_transactions = get_top_5_transactions(filtered_transactions)

    currency_rates = get_currency_rates(currencies)
    stock_prices = get_stock_prices(stocks)

    response_data = {
        "greeting": greeting,
        "cards": cards_info,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return json.dumps(response_data, ensure_ascii=False, indent=2)


def events_page_view(date_time_str: str, date_range: str = "M") -> str:
    """Главная функция для генерации JSON-ответа для страницы 'События'.

    :param date_time_str: Дата и время в формате YYYY-MM-DD HH:MM:SS или DD.MM.YYYY HH:MM:SS
    :param date_range: Диапазон данных: W (неделя), M (месяц), Y (год), ALL (все данные до даты)
    """
    base_dir = Path(__file__).resolve().parents[1]
    excel_path = base_dir / "data" / "operations.xlsx"
    settings = load_user_settings(str(base_dir / "user_settings.json"))

    currencies = settings.get("user_currencies", ["USD", "EUR"])
    stocks = settings.get("user_stocks", ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])

    all_transactions = glob_load_transactions(str(excel_path))

    # 1. Определяем границы периода
    try:
        end_date = pd.to_datetime(date_time_str)
    except (ValueError, TypeError):
        return json.dumps({"error": "Неверный формат даты"}, ensure_ascii=False)

    if date_range == "W":
        start_date = end_date - pd.Timedelta(days=7)
    elif date_range == "Y":
        start_date = end_date - pd.DateOffset(years=1)
    elif date_range == "ALL":
        start_date = pd.to_datetime("1900-01-01")  # Условно "все данные"
    else:  # По умолчанию "M"
        start_date = end_date.replace(day=1)

    # 2. Фильтруем данные
    df = pd.DataFrame(all_transactions)
    if df.empty:
        return json.dumps({"error": "Нет данных"}, ensure_ascii=False)

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True, errors="coerce")
    filtered_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)].copy()

    # 3. Считаем Расходы и Поступления
    expenses_df = filtered_df[filtered_df["Сумма платежа"] < 0].copy()
    income_df = filtered_df[filtered_df["Сумма платежа"] > 0].copy()

    expenses_df["Сумма платежа"] = expenses_df["Сумма платежа"].abs()

    # --- Логика для РАСХОДОВ ---
    total_expenses = int(expenses_df["Сумма платежа"].sum())

    # Разделяем на "Переводы и наличные" и "Основные"
    transfer_cats = ["Переводы", "Наличные"]
    main_expenses_df = expenses_df[~expenses_df["Категория"].isin(transfer_cats)]
    transfer_expenses_df = expenses_df[expenses_df["Категория"].isin(transfer_cats)]

    # Группируем основные расходы
    main_grouped = main_expenses_df.groupby("Категория")["Сумма платежа"].sum().reset_index()
    main_grouped = main_grouped.sort_values(by="Сумма платежа", ascending=False)

    # Топ-7 и "Остальное"
    main_list = []
    if len(main_grouped) > 7:
        top_7 = main_grouped.head(7)
        other_sum = main_grouped.iloc[7:]["Сумма платежа"].sum()
        for _, row in top_7.iterrows():
            main_list.append({"category": row["Категория"], "amount": int(round(row["Сумма платежа"]))})
        main_list.append({"category": "Остальное", "amount": int(round(other_sum))})
    else:
        for _, row in main_grouped.iterrows():
            main_list.append({"category": row["Категория"], "amount": int(round(row["Сумма платежа"]))})

    # Группируем переводы
    transfer_grouped = transfer_expenses_df.groupby("Категория")["Сумма платежа"].sum().reset_index()
    transfer_grouped = transfer_grouped.sort_values(by="Сумма платежа", ascending=False)
    transfer_list = []
    for _, row in transfer_grouped.iterrows():
        transfer_list.append({"category": row["Категория"], "amount": int(round(row["Сумма платежа"]))})

    # --- Логика для ПОСТУПЛЕНИЙ ---
    total_income = int(income_df["Сумма платежа"].sum())
    income_grouped = income_df.groupby("Категория")["Сумма платежа"].sum().reset_index()
    income_grouped = income_grouped.sort_values(by="Сумма платежа", ascending=False)
    income_list = []
    for _, row in income_grouped.iterrows():
        income_list.append({"category": row["Категория"], "amount": int(round(row["Сумма платежа"]))})

    # 4. Собираем ответ
    response_data = {
        "expenses": {"total_amount": total_expenses, "main": main_list, "transfers_and_cash": transfer_list},
        "income": {"total_amount": total_income, "main": income_list},
        "currency_rates": get_currency_rates(currencies),
        "stock_prices": get_stock_prices(stocks),
    }

    return json.dumps(response_data, ensure_ascii=False, indent=2)
