import json

from fastapi import FastAPI, HTTPException, Query

from src.reports import spending_by_workday
from src.services import investment_bank, simple_search_transactions
from src.utils import glob_load_transactions
from src.views import events_page_view, main_page_view

app = FastAPI(
    title="Finance Analytics API",
    description="API для анализа финансовых транзакций (на основе курсовой работы)",
    version="1.0.0",
)

# Путь к файлу с данными
EXCEL_PATH = "data/operations.xlsx"


@app.get("/")
def read_root() -> dict:
    """Корневой эндпоинт для проверки работоспособности API."""
    return {"message": "API работает. Перейдите на /docs для просмотра документации."}


@app.get("/views/main")
def get_main_page(
    dt: str = Query(
        ...,
        description="Дата и время в формате YYYY-MM-DD HH:MM:SS",
        examples=["2021-12-21 15:30:00"],
    )
) -> dict:
    """Эндпоинт для страницы «Главная».

    Возвращает приветствие, данные по картам, топ-5 транзакций, курсы валют и акции.
    """
    try:
        # Твоя функция возвращает JSON-строку, поэтому мы её парсим в словарь
        result_json = main_page_view(dt)
        return json.loads(result_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке: {str(e)}")


@app.get(
    "/views/events",
    summary="Страница «События»",
    description="Возвращает расходы и поступления с группировкой по категориям за указанный период.",
)
def get_events_page(
    dt: str = Query(
        ...,
        description="Дата и время в формате YYYY-MM-DD HH:MM:SS",
        examples=["2021-12-21 15:30:00"],
    ),
    range_type: str = Query(
        "M",
        alias="range",
        description="Диапазон данных: W (неделя), M (месяц), Y (год), ALL (все данные)",
        examples=["M"],
    ),
) -> dict:
    try:
        result_json = events_page_view(dt, range_type)
        parsed_data = json.loads(result_json)
        if "error" in parsed_data:
            raise HTTPException(status_code=400, detail=parsed_data["error"])
        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке: {str(e)}")


@app.get("/services/invest")
def get_investment_bank(
    month: str = Query(..., description="Месяц в формате YYYY-MM", examples=["2021-12"]),
    limit: int = Query(50, description="Шаг округления (10, 50, 100)", ge=1),
) -> dict:
    """Сервис «Инвесткопилка»."""
    try:
        transactions = glob_load_transactions(EXCEL_PATH)
        result = investment_bank(month, transactions, limit)
        return {"month": month, "limit": limit, "saved_amount": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке: {str(e)}")


@app.get("/services/search")
def get_search(query: str = Query(..., description="Строка для поиска по описанию или категории")) -> list:
    """Сервис «Простой поиск»."""
    try:
        transactions = glob_load_transactions(EXCEL_PATH)
        result_json = simple_search_transactions(transactions, query)
        return json.loads(result_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке: {str(e)}")


@app.get("/reports/workday")
def get_workday_report(
    date: str = Query(
        None,
        description="Дата в формате DD.MM.YYYY (если не передана, берется текущая)",
        examples=["21.12.2021"],
    )
) -> list:
    """Отчёт: средние траты в рабочий и выходной день за последние 3 месяца."""
    try:
        transactions = glob_load_transactions(EXCEL_PATH)
        # Важно: твоя функция работает с DataFrame, поэтому конвертируем список обратно
        import pandas as pd

        df = pd.DataFrame(transactions)
        result_df = spending_by_workday(df, date)
        # Конвертируем DataFrame в список словарей для JSON-ответа
        return result_df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
