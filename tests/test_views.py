from typing import Any

import pytest

from src.views import calculate_cards_info, get_currency_rates, get_stock_prices, get_top_5_transactions


@pytest.fixture
def view_sample_transactions() -> list[dict[str, Any]]:
    """Тестовый набор транзакций для проверки логики отображения страниц."""
    return [
        {
            "Статус": "OK",
            "Номер карты": "*7197",
            "Сумма платежа": -1000.0,
            "Категория": "Супермаркеты",
            "Дата операции": "22.12.2021 10:00:00",
            "Описание": "Лента",
        },
        {
            "Статус": "OK",
            "Номер карты": "*7197",
            "Сумма платежа": -2000.0,
            "Категория": "Фастфуд",
            "Дата операции": "22.12.2021 11:00:00",
            "Описание": "Макдоналдс",
        },
        {
            "Статус": "OK",
            "Номер карты": "*4556",
            "Сумма платежа": -500.0,
            "Категория": "Транспорт",
            "Дата операции": "23.12.2021 12:00:00",
            "Описание": "Метро",
        },
        {
            "Статус": "FAILED",
            "Номер карты": "*4556",
            "Сумма платежа": -9999.0,
            "Категория": "Электроника",
            "Дата операции": "23.12.2021 13:00:00",
            "Описание": "МВидео",
        },
        {
            "Статус": "OK",
            "Номер карты": "*7197",
            "Сумма платежа": 15000.0,
            "Категория": "Пополнения",
            "Дата операции": "24.12.2021 14:00:00",
            "Описание": "Зарплата",
        },
    ]


def test_calculate_cards_info(view_sample_transactions: list[dict[str, Any]]) -> None:
    """Проверяет суммирование расходов по картам и правильность расчета кэшбэка."""
    result = calculate_cards_info(view_sample_transactions)

    assert len(result) == 2
    cards_dict = {c["last_digits"]: c for c in result}

    assert cards_dict["7197"]["total_spent"] == 3000.0
    assert cards_dict["7197"]["cashback"] == 30.0

    assert cards_dict["4556"]["total_spent"] == 500.0
    assert cards_dict["4556"]["cashback"] == 5.0


def test_get_top_5_transactions(view_sample_transactions: list[dict[str, Any]]) -> None:
    """Проверяет, что топ транзакций сортируется по модулю суммы платежа."""
    extended_tx = view_sample_transactions + [
        {
            "Статус": "OK",
            "Номер карты": "*7197",
            "Сумма платежа": -50.0,
            "Категория": "Аптеки",
            "Дата операции": "25.12.2021",
        },
        {
            "Статус": "OK",
            "Номер карты": "*7197",
            "Сумма платежа": -30000.0,
            "Категория": "Авиабилеты",
            "Дата операции": "26.12.2021",
            "Описание": "Аэрофлот",
        },
    ]

    top_5 = get_top_5_transactions(extended_tx)
    assert len(top_5) == 5
    assert top_5[0]["amount"] == -30000.0
    assert top_5[0]["category"] == "Авиабилеты"
    assert top_5[1]["amount"] == 15000.0


def test_get_currency_rates_fallback() -> None:
    """Проверяет, что без API-ключа функция успешно возвращает дефолтные курсы валют."""
    result = get_currency_rates(["USD", "EUR"])
    assert len(result) == 2
    assert result[0]["currency"] == "USD"
    assert isinstance(result[0]["rate"], float)
    assert result[0]["rate"] > 0


def test_get_stock_prices_fallback() -> None:
    """Проверяет, что при сбое API функция возвращает защитные цены-заглушки для акций."""
    stocks = ["AAPL", "TSLA"]
    result = get_stock_prices(stocks)
    assert len(result) == 2
    assert result[0]["stock"] == "AAPL"
    assert isinstance(result[0]["price"], float)
    assert result[0]["price"] > 0
