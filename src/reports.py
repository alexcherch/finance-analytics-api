import functools
import logging
from datetime import datetime
from typing import Any, Callable, Optional

import pandas as pd

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def report_to_file(filename: Any = None) -> Callable[..., Any]:
    """Декоратор для функций-отчетов.

    Сохраняет возвращаемый функцией DataFrame в JSON-файл.
    """

    def decorator(func: Any) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.info(f"Старт отчета: функция '{func.__name__}' вызвана.")

            try:
                result_df = func(*args, **kwargs)
                logger.info(f"Функция '{func.__name__}' успешно выполнена. Строк в результате: {len(result_df)}")
            except Exception as e:
                logger.error(f"Критическая ошибка внутри функции '{func.__name__}': {e}")
                raise e

            if filename and isinstance(filename, str):
                out_file = filename
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                out_file = f"report_default_{timestamp}.json"

            if isinstance(result_df, pd.DataFrame) and not result_df.empty:
                result_df.to_json(out_file, orient="records", force_ascii=False, indent=2)
                logger.info(f"Результат отчета успешно сохранен в файл: {out_file}")

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
    logger.info(f"Параметры spending_by_workday: дата отсчета={
        date if date else 'текущая'}, всего транзакций для анализа={len(transactions)}")

    if transactions.empty:
        logger.warning("На вход spending_by_workday передан пустой DataFrame транзакций!")
        return pd.DataFrame()

    if date:
        end_date = pd.to_datetime(date)
    else:
        end_date = pd.to_datetime(datetime.now())

    start_date = end_date - pd.DateOffset(months=3)

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")

    filtered_df = df[
        (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date) & (df["Сумма платежа"] < 0)
    ].copy()

    if filtered_df.empty:
        logger.warning(f"После фильтрации за 3 месяца не найдено ни одного расхода до даты {end_date}")
        return pd.DataFrame(columns=["Тип дня", "Средние траты"])

    filtered_df["Сумма платежа"] = filtered_df["Сумма платежа"].abs()

    filtered_df["Тип дня"] = "Рабочий день"
    weekdays = filtered_df["Дата операции"].dt.weekday
    filtered_df.loc[weekdays >= 5, "Тип дня"] = "Выходной день"  # type: ignore

    result_df = filtered_df.groupby("Тип дня", as_index=False)[["Сумма платежа"]].mean()

    result_df.columns = ["Тип дня", "Средние траты"]
    result_df["Средние траты"] = result_df["Средние траты"].round(0).astype(int)

    return result_df


@report_to_file
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние три месяца от переданной даты."""
    logger.info(f"Параметры spending_by_category: категория={category}, дата={date if date else 'текущая'}")

    if transactions.empty:
        return pd.DataFrame()

    if date:
        end_date = pd.to_datetime(date)
    else:
        end_date = pd.to_datetime(datetime.now())

    start_date = end_date - pd.DateOffset(months=3)

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")

    filtered_df = df[
        (df["Дата операции"] >= start_date) &
        (df["Дата операции"] <= end_date) &
        (df["Категория"] == category) &
        (df["Сумма платежа"] < 0)
        ].copy()

    if filtered_df.empty:
        return pd.DataFrame(columns=["Дата операции", "Сумма платежа", "Категория"])

    filtered_df["Сумма платежа"] = filtered_df["Сумма платежа"].abs()

    return filtered_df[["Дата операции", "Сумма платежа", "Категория"]]


@report_to_file
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает средние траты в каждый из дней недели за последние три месяца."""
    if transactions.empty:
        return pd.DataFrame()

    if date:
        end_date = pd.to_datetime(date)
    else:
        end_date = pd.to_datetime(datetime.now())

    start_date = end_date - pd.DateOffset(months=3)

    df = transactions.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")

    filtered_df = df[
        (df["Дата операции"] >= start_date) &
        (df["Дата операции"] <= end_date) &
        (df["Сумма платежа"] < 0)
        ].copy()

    if filtered_df.empty:
        return pd.DataFrame(columns=["День недели", "Средние траты"])

    filtered_df["Сумма платежа"] = filtered_df["Сумма платежа"].abs()

    # 0 - Понедельник, 6 - Воскресенье
    days_map = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"}
    filtered_df["День недели"] = filtered_df["Дата операции"].dt.weekday.map(days_map)

    result_df = filtered_df.groupby("День недели", as_index=False)[["Сумма платежа"]].mean()
    result_df.columns = ["День недели", "Средние траты"]
    result_df["Средние траты"] = result_df["Средние траты"].round(0).astype(int)

    # Сортируем по порядку дней недели
    order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    result_df["День недели"] = pd.Categorical(result_df["День недели"], categories=order, ordered=True)
    result_df = result_df.sort_values("День недели")

    return result_df
