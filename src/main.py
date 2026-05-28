from pathlib import Path
import pandas as pd
from src.reports import spending_by_workday


def run_reports_test() -> None:
    print("=" * 50)
    print("ЗАПУСК ОТЧЕТА: РАБОЧИЕ И ВЫХОДНЫЕ ДНИ")
    print("=" * 50)

    # Путь к нашему файлу транзакций
    base_dir = Path(__file__).resolve().parents[1]
    excel_path = base_dir / "data" / "my_operations.xlsx"

    # Загружаем Excel напрямую в DataFrame для pandas
    print("Читаем Excel файл...")
    df_transactions = pd.read_excel(str(excel_path))
    print(f"Успешно загружено строк для анализа: {len(df_transactions)}")

    # Укажем историческую дату (например, конец декабря 2021 года)
    # Чтобы посмотреть траты за октябрь, ноябрь и декабрь 2021
    target_date = "31.03.2026 21:16:09"
    print(f"Анализируем трехмесячное окно до даты: {target_date}\n")

    # Вызываем нашу функцию, обернутую в декоратор
    report_df = spending_by_workday(df_transactions, target_date)

    print("РЕЗУЛЬТАТЫ СРЕДНИХ ТРАТ:")
    print(report_df.to_string(index=False))

    print("\n" + "=" * 50)
    print("[ИНФО] Загляни в корень проекта! Там должен появиться новый файл report_workday_*.json")
    print("=" * 50)


if __name__ == "__main__":
    run_reports_test()
