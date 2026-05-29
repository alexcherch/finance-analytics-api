import functools
from datetime import datetime
from typing import Any, Callable, Optional

import pandas as pd


def report_to_file(filename: Any = None) -> Callable[..., Any]:
    """Декоратор для функций-отчетов.

    Сохраняет возвращаемый функцией DataFrame в JSON-файл.
    """

    def decorator(func: Any) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result_df = func(*args, **kwargs)

            if filename and isinstance(filename, str):
                out_file = filename
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                out_file = f"report_default_{timestamp}.json"

            if isinstance(result_df, pd.DataFrame) and not result_df.empty:
                result_df.to_json(out_file, orient="records", force_ascii=False, indent=2)

            return result_df

        return wrapper

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
    if transactions.empty:
        return pd.DataFrame()

    if date:
        end_date = pd.to_datetime(date, dayfirst=True)
    else:
        end_date = pd.to_datetime(datetime.now())

    start_date = end_date - pd.DateOffset(months=3)

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True, errors="coerce")

    filtered_df = df[
        (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date) & (df["Сумма платежа"] < 0)
    ].copy()

    if filtered_df.empty:
        return pd.DataFrame(columns=["Тип дня", "Средние траты"])

    filtered_df["Сумма платежа"] = filtered_df["Сумма платежа"].abs()

    filtered_df["Тип дня"] = "Рабочий день"
    weekdays = filtered_df["Дата операции"].dt.weekday
    filtered_df.loc[weekdays >= 5, "Тип дня"] = "Выходной день"  # type: ignore

    result_df = filtered_df.groupby("Тип дня", as_index=False)[["Сумма платежа"]].mean()

    result_df.columns = ["Тип дня", "Средние траты"]
    result_df["Средние траты"] = result_df["Средние траты"].round(0).astype(int)

    return result_df
