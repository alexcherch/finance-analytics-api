from pathlib import Path
from src.utils import glob_load_transactions
from src.services import investment_bank


def run_services_test() -> None:
    print("=" * 50)
    print("ЗАПУСК СЕРВИСА «ИНВЕСТКОПИЛКА»")
    print("=" * 50)

    # Динамически вычисляем путь к Excel-файлу в корне проекта
    base_dir = Path(__file__).resolve().parents[1]
    excel_path = base_dir / "data" / "operations.xlsx"

    # Загружаем ВСЕ транзакции из файла
    all_transactions = glob_load_transactions(str(excel_path))
    print(f"Всего строк загружено для анализа: {len(all_transactions)}")

    # Настройки для проверки сервиса (укажите ваш рабочий год и месяц)
    test_month = "2021-12"
    rounding_limit = 50  # Порог округления (можно протестировать 10, 50 или 100)

    print(f"Анализируем месяц: {test_month}")
    print(f"Установленный шаг округления: {rounding_limit} ₽\n")

    # Вызываем функцию инвесткопилки
    money_saved = investment_bank(test_month, all_transactions, rounding_limit)

    print("РЕЗУЛЬТАТ РАСЧЕТА:")
    print(f"За месяц {test_month} вам удалось бы накопить: {money_saved} ₽")
    print("=" * 50)


if __name__ == "__main__":
    run_services_test()
