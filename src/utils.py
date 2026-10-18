import json
import os
from typing import cast

import pandas as pd


def glob_load_transactions(file_path: str) -> list[dict]:
    """Читает Excel-файл с финансовыми транзакциями
    и возвращает список словарей
    """
    if not os.path.exists(file_path):
        return []

    try:
        df = pd.read_excel(file_path)

        df = df.astype(object).fillna(pd.NA).replace({pd.NA: None})

        return df.to_dict(orient="records")

    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return []


def load_user_settings(settings_path: str = "user_settings.json") -> dict:
    """Читает пользовательские настройки из JSON-файла.
    Возвращает словарь с валютами и акциями
    """
    if not os.path.exists(settings_path):
        return {"user_currencies": [], "user_stocks": []}

    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            return cast(dict, json.load(f))
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return {"user_currencies": [], "user_stocks": []}


def filter_transactions_by_date(transactions: list[dict], date_str: str) -> list[dict]:
    """Фильтрует список транзакций по диапазону дат:
    от 1-го числа месяца переданной даты до самой даты включительно.
    """
    if not transactions:
        return []

    try:
        target_date = pd.to_datetime(date_str).date()
        start_date = target_date.replace(day=1)
    except (ValueError, TypeError):
        return []

    filtered = []
    for tx in transactions:
        tx_date_raw = tx.get("Дата операции")
        if not tx_date_raw or pd.isna(tx_date_raw):
            continue

        try:
            tx_date = pd.to_datetime(tx_date_raw).date()
            if start_date <= tx_date <= target_date:
                filtered.append(tx)
        except (ValueError, TypeError):
            continue

    return filtered
