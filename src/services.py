import json
import math

import pandas as pd


def investment_bank(month: str, transactions: list[dict], limit: int) -> float:
    """Рассчитывает сумму, которую удалось бы отложить в «Инвесткопилку» за указанный месяц.

    Округляются только расходные операции (где сумма операции < 0).
    month передается в формате 'YYYY-MM'.
    """
    # Если список транзакций пуст или лимит равен нулю, копить нечего
    if not transactions or not limit:
        return 0.0

    total_saved = 0.0
    # Очищаем строку месяца от лишних пробелов
    target_month = month.strip()

    for tx in transactions:
        tx_date_raw = tx.get("Дата операции")
        if not tx_date_raw or pd.isna(tx_date_raw):
            continue

        # Проверяем, относится ли транзакция к нужному месяцу
        # Так как дата в Excel может быть "2021-12-21" или "21.12.2021",
        # мы принудительно приводим её к стандарту ISO (YYYY-MM-DD) через pandas
        try:
            tx_date_iso = pd.to_datetime(tx_date_raw).strftime("%Y-%m")
        except Exception:
            continue

        if tx_date_iso != target_month:
            continue

        # Проверяем сумму операции (именно оригинальную сумму траты)
        amount = tx.get("Сумма операции")
        if amount is None or not isinstance(amount, (int, float)):
            continue

        # Округляем ТОЛЬКО траты (в Excel они идут со знаком минус, например -1712.0)
        if amount < 0:
            # Переводим сумму в положительное число для удобства расчетов
            spent_amount = abs(amount)

            # Магия округления вверх:
            # Делим на лимит (10, 50, 100), округляем вверх до целого и умножаем обратно
            rounded_amount = math.ceil(spent_amount / limit) * limit

            # Находим разницу, которая пойдет в копилку
            savings = rounded_amount - spent_amount
            total_saved += savings

    # Возвращаем общую сумму, округленную до двух знаков после запятой
    return round(total_saved, 2)


def simple_search_transactions(transactions: list[dict], query: str) -> str:
    """Ищет транзакции по совпадению подстроки в описании или категории.

    Поиск нечувствителен к регистру. Возвращает JSON-строку.
    """
    if not transactions or not query:
        return json.dumps([], ensure_ascii=False)

    # Приводим поисковый запрос к нижнему регистру и убираем лишние пробелы
    query_lower = str(query).strip().lower()
    matched_transactions = []

    for tx in transactions:
        # Безопасно достаем описание и категорию, заменяя пустые ячейки (NaN) на пустую строку
        description = tx.get("Описание")
        description_str = str(description).lower() if description and not pd.isna(description) else ""

        category = tx.get("Категория")
        category_str = str(category).lower() if category and not pd.isna(category) else ""

        # Если запрос есть в описании ИЛИ категории — забираем транзакцию
        if query_lower in description_str or query_lower in category_str:

            # Форматируем дату, чтобы в JSON улетала чистая дата без времени
            date_raw = tx.get("Дата операции")
            try:
                formatted_date = str(date_raw).strip().split()[0]
            except Exception:
                formatted_date = str(date_raw)

            matched_transactions.append(
                {
                    "date": formatted_date,
                    "amount": round(tx.get("Сумма платежа", 0), 2),
                    "category": category if category and not pd.isna(category) else "Остальное",
                    "description": description if description and not pd.isna(description) else "",
                }
            )

    # Возвращаем красивый структурированный JSON с поддержкой кириллицы
    return json.dumps(matched_transactions, ensure_ascii=False, indent=2)
