from typing import Any

from src.utils import filter_transactions_by_date, load_user_settings
from src.views import get_greeting


def test_get_greeting_morning() -> None:
    """Проверяет утреннее приветствие (06:00 - 11:59)."""
    assert get_greeting("2018-02-21 09:15:00") == "Доброе утро"


def test_get_greeting_day() -> None:
    """Проверяет дневное приветствие (12:00 - 17:59)."""
    assert get_greeting("2018-02-21 14:30:00") == "Добрый день"


def test_get_greeting_evening() -> None:
    """Проверяет вечернее приветствие (18:00 - 22:59)."""
    assert get_greeting("2018-02-21 20:00:00") == "Добрый вечер"


def test_get_greeting_night() -> None:
    """Проверяет ночное приветствие (23:00 - 05:59)."""
    assert get_greeting("2018-02-21 01:00:00") == "Доброй ночи"


def test_get_greeting_invalid_format() -> None:
    """Проверяет, что при битой строке функция возвращает дефолт и не падает."""
    assert get_greeting("некорректная дата") == "Добрый день"


def test_load_user_settings_success(tmp_path: Any) -> None:
    """Проверяет успешное чтение настроек из JSON-файла."""
    import json

    test_file = tmp_path / "test_settings.json"
    mock_data = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}

    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)

    result = load_user_settings(str(test_file))
    assert result["user_currencies"] == ["USD"]


def test_load_user_settings_file_missing() -> None:
    """Проверяет, что при отсутствии файла возвращаются пустые списки."""
    result = load_user_settings("non_existent_file.json")
    assert result == {"user_currencies": [], "user_stocks": []}


def test_filter_transactions_by_date_pandas() -> None:
    """Проверяет фильтрацию транзакций по диапазону дат."""
    transactions = [
        {"Дата операции": "2018-02-05 10:00:00"},
        {"Дата операции": "2018-02-21 23:00:00"},
        {"Дата операции": "2018-02-25 12:00:00"},
        {"Дата операции": "2018-01-15 00:00:00"},
    ]
    result = filter_transactions_by_date(transactions, "2018-02-21 23:59:59")
    assert len(result) == 2
