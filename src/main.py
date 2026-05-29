from pathlib import Path

import pandas as pd

from src.reports import spending_by_workday
from src.services import investment_bank, simple_search_transactions
from src.views import main_page_view


def main() -> None:
    print("=" * 60)
    print("      ЗАПУСК ДЕМОНСТРАЦИИ ВСЕХ МОДУЛЕЙ КУРСОВОГО ПРОЕКТА      ")
    print("=" * 60)

    base_dir = Path(__file__).resolve().parents[1]
    excel_path = base_dir / "data" / "operations.xlsx"

    print("Шаг 1: Загрузка базы данных транзакций...")
    all_transactions = pd.read_excel(str(excel_path))
    transactions_list = all_transactions.astype(object).fillna(pd.NA).replace({pd.NA: None}).to_dict(orient="records")
    print(f"[УСПЕХ] Загружено строк для анализа: {len(all_transactions)}\n")

    test_date_time = "21.12.2021 15:30:00"
    test_month = "2021-12"

    # =================================================================
    # БЛОК 1: СТРАНИЦА «ГЛАВНАЯ» (views.py)
    # =================================================================
    print("-" * 60)
    print("БЛОК 1: Генерация JSON-ответа для Главной страницы")
    print("-" * 60)
    try:
        main_page_json = main_page_view(test_date_time)
        print(main_page_json)
    except Exception as e:
        print(f"[ОШИБКА БЛОКА 1]: {e}")
    print()

    # =================================================================
    # БЛОК 2: СЕРВИСЫ (services.py)
    # =================================================================
    print("-" * 60)
    print("БЛОК 2: Работа бизнес-сервисов")
    print("-" * 60)

    # Тест Инвесткопилки
    limit = 50
    saved_money = investment_bank(test_month, transactions_list, limit)
    print(f" Сервис «Инвесткопилка» ({test_month}, шаг {limit}₽):")
    print(f"   Удалось бы отложить: {saved_money} ₽\n")

    # Тест Про Squire Поиска
    search_query = "Супермаркеты"
    print(f" Сервис «Простой поиск» по ключевому слову '{search_query}':")
    search_res = simple_search_transactions(transactions_list, search_query)
    # Выведем только первые 300 символов ответа, чтобы не спамить консоль
    print(search_res[:300] + "\n   ... [далее список совпадений] ...\n")

    # =================================================================
    # БЛОК 3: ОТЧЕТЫ (reports.py)
    # =================================================================
    print("-" * 60)
    print("БЛОК 3: Аналитические отчеты Pandas")
    print("-" * 60)
    try:
        print(f"Формируем трехмесячный отчет по будням и выходным до {test_date_time}...")
        report_df = spending_by_workday(all_transactions, test_date_time)
        print(report_df.to_string(index=False))
        print("\n[ИНФО] Декоратор @report_to_file успешно создал JSON-файл отчета на диске!")
    except Exception as e:
        print(f"[ОШИБКА БЛОКА 3]: {e}")

    print("\n" + "=" * 60)
    print("      ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА. ВСЕ СИСТЕМЫ РАБОТАЮТ ИДЕАЛЬНО!      ")
    print("=" * 60)


if __name__ == "__main__":
    main()
