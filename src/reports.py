import functools
from datetime import datetime
from typing import Optional, Any, Callable

import pandas as pd


def report_to_file(filename: Optional[str] = None) -> Callable[..., Any]:
    """Декоратор для функций-отчетов.

    Сохраняет возвращаемый функцией DataFrame в JSON-файл.
    """

    def decorator(func):  # type: ignore
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # type: ignore
            # 1. Вызываем саму функцию отчета и получаем DataFrame
            result_df = func(*args, **kwargs)

            # 2. Определяем имя файла
            if filename and isinstance(filename, str):
                out_file = filename
            else:
                # Если имя не передано, создаем уникальное по времени
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                out_file = f"report_workday_{timestamp}.json"

            # 3. Если функция вернула Датафрейм, сохраняем его на диск
            if isinstance(result_df, pd.DataFrame) and not result_df.empty:
                result_df.to_json(out_file, orient="records", force_ascii=False, indent=2)

            return result_df

        return wrapper

    # Магия Python для поддержки вызова декоратора без скобок
    if callable(filename):
        func_to_decor = filename
        filename = None
        return decorator(func_to_decor)

    return decorator


@report_to_file
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает средние траты в рабочий и в выходной день за последние три месяца от переданной даты.

    Если дата не передана, берется текущая дата.
    """
    # Защита: если на вход пришла пустая таблица, сразу возвращаем пустой DataFrame
    if transactions.empty:
        return pd.DataFrame()

    # 1. Определяем конечную дату отсчета
    if date:
        end_date = pd.to_datetime(date, dayfirst=True)
    else:
        end_date = pd.to_datetime(datetime.now())

    # 2. Вычисляем дату старта (минус 3 месяца назад с помощью DateOffset)
    start_date = end_date - pd.DateOffset(months=3)

    # 3. Безопасно подготавливаем колонки данных
    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True, errors="coerce")

    # 4. Фильтруем: берем только нужный период времени и только ТРАТЫ (где Сумма платежа < 0)
    filtered_df = df[
        (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date) & (df["Сумма платежа"] < 0)
    ].copy()

    # Если после фильтрации ничего не осталось, возвращаем пустую структуру
    if filtered_df.empty:
        return pd.DataFrame(columns=["Тип дня", "Средние траты"])

    # Переводим расходы в положительные числа для человекочитаемого отчета
    filtered_df["Сумма платежа"] = filtered_df["Сумма платежа"].abs()

    # 5. Группируем дни: .dt.weekday возвращает числа от 0 (понедельник) до 6 (воскресенье)
    # Суббота (5) и воскресенье (6) — это выходные, всё что меньше 5 — рабочие
    filtered_df["Тип дня"] = filtered_df["Дата операции"].dt.weekday.apply(
        lambda x: "Выходной день" if x >= 5 else "Рабочий день"
    )

    # 6. Считаем среднее значение расходов (.mean()) для каждой группы
    result_df = filtered_df.groupby("Тип дня", as_index=False)["Сумма платежа"].mean()

    # Переименовываем колонки согласно ТЗ и округляем до целых чисел, как требует ТЗ
    result_df.columns = ["Тип дня", "Средние траты"]
    result_df["Средние траты"] = result_df["Средние траты"].round(0).astype(int)

    return result_df
