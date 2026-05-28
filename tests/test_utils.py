from src.views import get_greeting
import json
from src.utils import load_user_settings, filter_transactions_by_date


def test_get_greeting_morning():
    """Проверяет утреннее приветствие (06:00 - 11:59)."""
    assert get_greeting("21.02.2018 09:15:00") == "Доброе утро"


def test_get_greeting_day():
    """Проверяет дневное приветствие (12:00 - 17:59)."""
    assert get_greeting("21.02.2018 14:30:00") == "Добрый день"


def test_get_greeting_evening():
    """Проверяет вечернее приветствие (18:00 - 22:59)."""
    assert get_greeting("21.02.2018 20:00:00") == "Добрый вечер"


def test_get_greeting_night():
    """Проверяет ночное приветствие (23:00 - 05:59)."""
    assert get_greeting("21.02.2018 01:00:00") == "Доброй ночи"


def test_get_greeting_invalid_format():
    """Проверяет, что при битой строке функция возвращает дефолт и не падает."""
    assert get_greeting("некорректная дата") == "Добрый день"


def test_load_user_settings_success(tmp_path):
    """Проверяет успешное чтение настроек из JSON-файла."""
    # Создаем временный тестовый JSON-файл на диске с помощью фикстуры tmp_path
    test_file = tmp_path / "test_settings.json"
    mock_data = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}

    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)

    result = load_user_settings(str(test_file))
    assert result["user_currencies"] == ["USD"]


def test_load_user_settings_file_missing():
    """Проверяет, что при отсутствии файла возвращаются пустые списки."""
    result = load_user_settings("non_existent_file.json")
    assert result == {"user_currencies": [], "user_stocks": []}


def test_filter_transactions_by_date_pandas():
    """Проверяет фильтрацию транзакций по диапазону дат."""
    transactions = [
        {"Дата операции": "05.02.2018 10:00:00"},  # Попадает
        {"Дата операции": "21.02.2018 23:00:00"},  # Попадает
        {"Дата операции": "25.02.2018 12:00:00"},  # НЕ попадает (после даты отсчета)
        {"Дата операции": "15.01.2018 00:00:00"}  # НЕ попадает (прошлый месяц)
    ]
    # Запускаем фильтр до 21.02.2018 (должен оставить только 2 транзакции февраля)
    result = filter_transactions_by_date(transactions, "21.02.2018 23:59:59")
    assert len(result) == 2
