from typing import Any

import pytest

from src.services import investment_bank, simple_search_transactions


@pytest.fixture
def sample_transactions() -> list[dict[str, Any]]:
    """Создает тестовый набор транзакций для проверки копилки."""
    return [
        {"Дата операции": "2021-12-15 10:00:00", "Сумма операции": -1712.0},
        {"Дата операции": "2021-12-16 11:00:00", "Сумма операции": -1700.0},
        {"Дата операции": "2021-12-17 12:00:00", "Сумма операции": 5000.0},
        {"Дата операции": "2021-11-01 15:00:00", "Сумма операции": -150.0},
    ]


def test_investment_bank_rounding_50(sample_transactions: list[dict[str, Any]]) -> None:
    """Проверяет работу копилки с шагом округления 50 рублей."""
    result = investment_bank("2021-12", sample_transactions, 50)
    assert result == 38.0


def test_investment_bank_rounding_10(sample_transactions: list[dict[str, Any]]) -> None:
    """Проверяет работу копилки с шагом округления 10 рублей."""
    result = investment_bank("2021-12", sample_transactions, 10)
    assert result == 8.0


def test_investment_bank_empty_data() -> None:
    """Проверяет, что пустой список транзакций возвращает 0.0."""
    assert investment_bank("2021-12", [], 50) == 0.0


def test_simple_search_by_category() -> None:
    """Проверяет поиск транзакций по категории."""
    transactions = [{"Дата операции": "2021-12-22", "Категория": "Супермаркеты", "Описание": "Лента"}]
    result_json = simple_search_transactions(transactions, "супер")
    import json

    result = json.loads(result_json)
    assert len(result) == 1
    assert result[0]["category"] == "Супермаркеты"


def test_simple_search_by_description() -> None:
    """Проверяет поиск транзакций по описанию."""
    transactions = [{"Дата операции": "2021-12-22", "Категория": "Остальное", "Описание": "Покупка на OZON"}]
    result_json = simple_search_transactions(transactions, "ozon")
    import json

    result = json.loads(result_json)
    assert len(result) == 1
    assert result[0]["description"] == "Покупка на OZON"
