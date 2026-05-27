from src.views import main_page_view


def run_application() -> None:
    test_date_time = "29.12.2021 14:15:35"

    # Вызываем функцию и печатаем результат
    json_response = main_page_view(test_date_time)
    print(json_response)


if __name__ == "__main__":
    run_application()
