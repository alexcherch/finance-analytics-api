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
            tx_date_iso = pd.to_datetime(tx_date_raw, dayfirst=True).strftime("%Y-%m")
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
