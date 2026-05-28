import json
import os
from typing import Optional, cast
import pandas as pd


def glob_load_transactions(file_path: str) -> list[dict]:
    """Читает Excel-файл с финансовыми транзакциями
    и возвращает список словарей
    """
    if not os.path.exists(file_path):
        # Здесь будет: logger.error(f"Файл не найден: {file_path}")
        return []

    try:
        df = pd.read_excel(file_path)

        # Заменяем NaN на None для корректной последующей конвертации в JSON
        df = df.astype(object).fillna(pd.NA).replace({pd.NA: None})

        return df.to_dict(orient="records")

    except Exception:
        # Здесь будет: logger.exception("Ошибка при чтении Excel-файла")
        return []


def load_user_settings(settings_path: str = "user_settings.json") -> dict:
    """Читает пользовательские настройки из JSON-файла.
    Возвращает словарь с валютами и акциями
    """
    if not os.path.exists(settings_path):
        return {"user_currencies": [], "user_stocks": []}

    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            # Метод cast принудительно подсказывает mypy: "Здесь точно dict!"
            return cast(dict, json.load(f))
    except Exception:
        return {"user_currencies": [], "user_stocks": []}


def filter_transactions_by_date(transactions: list[dict], date_str: str) -> list[dict]:
    """Фильтрует список транзакций по диапазону дат:

    от 1-го числа месяца переданной даты до самой даты включительно.
    """
    if not transactions:
        return []

    try:
        # 1. Принудительно берем только текстовую дату до пробела (строку, а не список)
        # "21.02.2018 22:34:36" -> "21.02.2018"
        just_date_str = str(date_str).strip().split()[0]

        # Превращаем в чистый объект даты
        if "." in just_date_str:
            target_date = pd.to_datetime(just_date_str, format="%d.%m.%Y").date()
        else:
            target_date = pd.to_datetime(just_date_str, format="%Y-%m-%d").date()

        # Вычисляем первое число месяца
        start_date = target_date.replace(day=1)
    except Exception:
        return []

    filtered = []
    for tx in transactions:
        tx_date_raw = tx.get("Дата операции")
        if not tx_date_raw or pd.isna(tx_date_raw):
            continue

        try:
            # 2. Точно так же вытаскиваем чистую дату транзакции до пробела
            tx_date_str = str(tx_date_raw).strip().split()[0]

            if "." in tx_date_str:
                tx_date = pd.to_datetime(tx_date_str, format="%d.%m.%Y").date()
            else:
                tx_date = pd.to_datetime(tx_date_str, format="%Y-%m-%d").date()

            # 3. Прямое сравнение чистых календарных дней
            if start_date <= tx_date <= target_date:
                filtered.append(tx)
        except Exception:
            continue

    return filtered
