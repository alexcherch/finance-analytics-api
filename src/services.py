import json
import logging
import math

import pandas as pd

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def investment_bank(month: str, transactions: list[dict], limit: int) -> float:
    """Рассчитывает сумму, которую удалось бы отложить в «Инвесткопилку» за указанный месяц.

    Округляются только расходные операции (где сумма операции < 0).
    """
    logger.info(f"Запуск сервиса 'Инвесткопилка' для месяца {month} с шагом округления {limit}₽")

    if not transactions or not limit:
        logger.warning("В сервис Инвесткопилка переданы пустые данные или нулевой лимит.")
        return 0.0

    total_saved = 0.0
    target_month = month.strip()

    for tx in transactions:
        tx_date_raw = tx.get("Дата операции")
        if not tx_date_raw or pd.isna(tx_date_raw):
            continue

        try:
            tx_date_iso = pd.to_datetime(tx_date_raw).strftime("%Y-%m")
        except (ValueError, TypeError, Exception):
            continue

        if tx_date_iso != target_month:
            continue

        amount = tx.get("Сумма операции")
        if amount is None or not isinstance(amount, (int, float)):
            continue

        if amount < 0:
            spent_amount = abs(amount)

            rounded_amount = math.ceil(spent_amount / limit) * limit

            savings = rounded_amount - spent_amount
            total_saved += savings

    logger.info(f"Сервис 'Инвесткопилка' успешно завершил расчет. Итого отложено: {round(total_saved, 2)}₽")

    return round(total_saved, 2)


def simple_search_transactions(transactions: list[dict], query: str) -> str:
    """Ищет транзакции по совпадению подстроки в описании или категории."""
    if not transactions or not query:
        return json.dumps([], ensure_ascii=False)

    query_lower = str(query).strip().lower()
    matched_transactions = []

    for tx in transactions:
        description = tx.get("Описание")
        description_str = str(description).lower() if description and not pd.isna(description) else ""

        category = tx.get("Категория")
        category_str = str(category).lower() if category and not pd.isna(category) else ""

        if query_lower in description_str or query_lower in category_str:

            date_raw = tx.get("Дата операции")
            try:
                formatted_date = str(date_raw).strip().split()[0]
            except (IndexError, ValueError, TypeError):
                formatted_date = str(date_raw)

            matched_transactions.append(
                {
                    "date": formatted_date,
                    "amount": round(tx.get("Сумма платежа", 0), 2),
                    "category": category if category and not pd.isna(category) else "Остальное",
                    "description": description if description and not pd.isna(description) else "",
                }
            )

    return json.dumps(matched_transactions, ensure_ascii=False, indent=2)


def cashback_categories(transactions: list[dict], year: int, month: int) -> dict:
    """Анализирует, сколько на каждой категории можно заработать кешбэка (1%) в указанном месяце."""
    if not transactions:
        return {}

    result = {}
    for tx in transactions:
        tx_date_raw = tx.get("Дата операции")
        if not tx_date_raw or pd.isna(tx_date_raw):
            continue

        try:
            tx_date = pd.to_datetime(tx_date_raw)
            if tx_date.year == year and tx_date.month == month:
                amount = tx.get("Сумма платежа")
                if isinstance(amount, (int, float)) and amount < 0:
                    category = tx.get("Категория", "Остальное")
                    # Считаем 1% от трат как потенциальный кешбэк
                    cashback = abs(amount) * 0.01
                    result[category] = result.get(category, 0.0) + cashback
        except (ValueError, TypeError):
            continue

    # Округляем до 2 знаков
    return {k: round(v, 2) for k, v in sorted(result.items(), key=lambda item: item[1], reverse=True)}
