import json
import os
from datetime import datetime
import pandas as pd


def glob_load_transactions(file_path: str) -> list[dict]:
    """ Читает Excel-файл с финансовыми транзакциями
        и возвращает список словарей
    """
    if not os.path.exists(file_path):
        # Здесь будет: logger.error(f"Файл не найден: {file_path}")
        return []

    try:
        df = pd.read_excel(file_path)

        # Заменяем NaN на None для корректной последующей конвертации в JSON
        df = df.astype(object).where(pd.notnull(df), None)

        return df.to_dict(orient="records")

    except Exception:
        # Здесь будет: logger.exception("Ошибка при чтении Excel-файла")
        return []


def load_user_settings(settings_path: str = "user_settings.json") -> dict:
    """ Читает пользовательские настройки из JSON-файла.
        Возвращает словарь с валютами и акциями
    """
    if not os.path.exists(settings_path):
        return {"user_currencies": [], "user_stocks": []}

    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"user_currencies": [], "user_stocks": []}


def filter_transactions_by_date(transactions: list[dict], date_str: str) -> list[dict]:
    """ Фильтрует транзакции в диапазоне от 1-го числа месяца переданной даты
        до самой переданной даты включительно.
    """
    filtered = []

    # Определяем формат входящей даты и превращаем ее в объект datetime
    try:
        # Если пришла строка вида "2021-12-21 15:30:00", берем только первую часть "2021-12-21"
        clean_date_str = date_str.split()[0]

        if "." in clean_date_str:
            target_date = datetime.strptime(clean_date_str, "%d.%m.%Y")
        else:
            target_date = datetime.strptime(clean_date_str, "%Y-%m-%d")
    except ValueError:
        return []

    # Определяем начало месяца для переданной даты
    start_of_month = datetime(target_date.year, target_date.month, 1)

    for tx in transactions:
        tx_date_raw = tx.get("Дата операции")
        if not tx_date_raw:
            continue

        # В Excel даты могут быть строками или уже объектами даты. Обрабатываем оба случая:
        try:
            if isinstance(tx_date_raw, str):
                # Пробуем стандартный формат даты в выгрузках (например, '25.12.2021 13:50:58')
                tx_date = datetime.strptime(tx_date_raw.split()[0], "%d.%m.%Y")
            else:
                # Если pandas уже превратил ячейку в Timestamp/datetime
                tx_date = pd.to_datetime(tx_date_raw).to_pydatetime()
        except Exception:
            continue

        # Проверяем, попадает ли транзакция в диапазон [Начало месяца; Целевая дата]
        if start_of_month <= tx_date <= target_date:
            filtered.append(tx)

    return filtered
