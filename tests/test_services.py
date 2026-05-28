import pytest

from src.services import investment_bank, simple_search_transactions


@pytest.fixture
def sample_transactions():
    """Создает тестовый набор транзакций для проверки копилки."""
    return [
        # Расход 1712 руб (при лимите 50 должно отложить 38 руб)
        {"Дата операции": "2021-12-15 10:00:00", "Сумма операции": -1712.0},
        # Расход 1700 руб (ровная сумма, должно отложить 0 руб)
        {"Дата операции": "2021-12-16 11:00:00", "Сумma операции": -1700.0, "Сумма операции": -1700.0},
        # Пополнение 5000 руб (доходы игнорируются, должно отложить 0 руб)
        {"Дата операции": "2021-12-17 12:00:00", "Сумма операции": 5000.0},
        # Расход из ДРУГОГО месяца (должен проигнорироваться фильтром дат)
        {"Дата операции": "2021-11-01 15:00:00", "Сумма операции": -150.0},
    ]


def test_investment_bank_rounding_50(sample_transactions):
    """Проверяет работу копилки с шагом округления 50 рублей."""
    # Ожидаем только 38.0 рублей с первой транзакции
    result = investment_bank("2021-12", sample_transactions, 50)
    assert result == 38.0


def test_investment_bank_rounding_10(sample_transactions):
    """Проверяет работу копилки с шагом округления 10 рублей."""
    # 1712 должно округлиться до 1720 (разница 8.0 рублей)
    result = investment_bank("2021-12", sample_transactions, 10)
    assert result == 8.0


def test_investment_bank_empty_data():
    """Проверяет, что пустой список транзакций возвращает 0.0."""
    assert investment_bank("2021-12", [], 50) == 0.0


def test_simple_search_by_category():
    """Проверяет поиск транзакций по категории (нечувствительный к регистру)."""
    transactions = [
        {"Дата операции": "2021-12-22", "Категория": "Супермаркеты", "Описание": "Лента"},
        {"Дата операции": "2021-12-23", "Категория": "Фастфуд", "Описание": "Макдоналдс"},
    ]
    # Ищем слово "супер" в нижнем регистре
    result_json = simple_search_transactions(transactions, "супер")
    import json

    result = json.loads(result_json)

    assert len(result) == 1
    assert result[0]["category"] == "Супермаркеты"


def test_simple_search_by_description():
    """Проверяет поиск транзакций по описанию."""
    transactions = [
        {"Дата операции": "2021-12-22", "Категория": "Остальное", "Описание": "Покупка на OZON"},
        {"Дата операции": "2021-12-23", "Категория": "Остальное", "Описание": "Вайлдберриз"},
    ]
    result_json = simple_search_transactions(transactions, "ozon")
    import json

    result = json.loads(result_json)

    assert len(result) == 1
    assert result[0]["description"] == "Покупка на OZON"
