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
        just_date_str = str(date_str).strip().split()[0]

        if "." in just_date_str:
            target_date = pd.to_datetime(just_date_str, format="%d.%m.%Y").date()
        else:
            target_date = pd.to_datetime(just_date_str, format="%Y-%m-%d").date()

        start_date = target_date.replace(day=1)
    except (ValueError, TypeError, IndexError):
        return []

    filtered = []
    for tx in transactions:
        tx_date_raw = tx.get("Дата операции")
        if not tx_date_raw or pd.isna(tx_date_raw):
            continue

        try:
            tx_date_str = str(tx_date_raw).strip().split()[0]

            if "." in tx_date_str:
                tx_date = pd.to_datetime(tx_date_str, format="%d.%m.%Y").date()
            else:
                tx_date = pd.to_datetime(tx_date_str, format="%Y-%m-%d").date()

            if start_date <= tx_date <= target_date:
                filtered.append(tx)
        except (ValueError, TypeError, IndexError):
            continue

    return filtered
