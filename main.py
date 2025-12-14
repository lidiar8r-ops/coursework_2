from src import app_logger
from src.api import AreaAPI
from src.api_hh import HeadHunterAPI
from src.config import URL_HH
from src.vacancies import Vacancy
from src.work_files import JSONSaver

# Настройка логирования
logger = app_logger.get_logger("main.log")


def user_interaction() -> None:
    """
    Функция взаимодействия с пользователем через консольный интерфейс.

    Предоставляет меню для:
    - поиска вакансий на hh.ru;
    - просмотра топа вакансий по зарплате;
    - поиска по ключевым словам, диапазону зарплат, работодателю;
    - управления сохранёнными вакансиями (просмотр, удаление).

    Циклически отображает меню до выбора пункта «Выход» (9).
    Все действия логируются через logger.

    Поведение:
    1. Выводит приветственное сообщение и меню.
    2. Ожидает ввода номера действия от пользователя (1–9).
    3. В зависимости от выбора:
       - запрашивает дополнительные параметры (запрос, диапазон зарплат и т. п.);
       - выполняет соответствующую операцию через API и савер;
       - выводит результат или сообщение об ошибке.
    4. При выборе «9» завершает работу.

    Обработка ошибок:
    - некорректный ввод чисел (ValueError);
    - пустые обязательные поля;
    - отсутствие результатов поиска;
    - ошибки API и сохранения.

    Логирование:
    - начало/конец работы;
    - выполнение ключевых действий;
    - ошибки и предупреждения.

    Returns:
        None: Функция выполняет интерактивное взаимодействие, не возвращает значение.
    """
    logger.info("Начало работы программы")
    print("Добро пожаловать в систему поиска вакансий!")
    print("=" * 50)
    logger.info("=" * 50)

    hh_api = HeadHunterAPI()
    json_saver = JSONSaver()

    while True:
        print("\nВыберите действие:")
        print("1. Поиск вакансий на hh.ru")
        print("2. Показать топ N вакансий по зарплате")
        print("3. Поиск по ключевому слову")
        print("4. Показать все сохранённые вакансии")
        print("5. Удалить вакансию по URL")
        print("6. Поиск по диапазону зарплат")
        print("7. Поиск по работодателю")
        print("8. Удаление всех вакансий")
        print("9. Выход")

        choice = input("\nВведите номер действия (1–9): ").strip()

        if choice == "1":
            query = input("Введите поисковый запрос: ").strip()
            if not query:
                print("Запрос не может быть пустым!")
                continue

            excluded_text = input("Введите слова исключения в запросе (через запятую): ").strip()

            try:
                per_page = int(input("Сколько вакансий загрузить (по умолчанию 20): ") or 20)
                if per_page <= 0:
                    print("Количество должно быть положительным!")
                    continue
            except ValueError:
                print("Некорректное число!")
                continue

            try:
                area_str = input("Введите населенный пункт: ")
            except ValueError:
                print("Некорректный населенный пункт!")
                continue
            area_api = AreaAPI(area_str)
            area_id = area_api.get_id_area()
            print(area_id)

            logger.info(f"Ищем вакансии по запросу '{query}'...")
            print(f"Ищем вакансии по запросу '{query}'...")
            # print(query, excluded_text,area_id,per_page)
            # raw_vacancies = hh_api.get_request(query, excluded_text, area=area_id, per_page=per_page)

            raw_vacancies = hh_api.get_requests(
                query=query, excluded_text=excluded_text, area=area_id, per_page=per_page
            )

            if not raw_vacancies:
                logger.info("Вакансий не найдено.")
                print("Вакансий не найдено.")
                continue

            vacancies = [Vacancy.from_hh_api(item) for item in raw_vacancies]

            count_add_vacansies = 0
            for vacancy in vacancies:
                if json_saver._add_vacancy(vacancy):
                    count_add_vacansies += 1

            logger.info(f"Найдено {len(vacancies)} вакансий. Сохранены в файл {count_add_vacansies} новых вакансий")
            print(f"Найдено {len(vacancies)} вакансий. Сохранены в файл {count_add_vacansies} новых вакансий")

        elif choice == "2":
            try:
                n = int(input("Сколько вакансий показать в топе: "))
                if n <= 0:
                    print("Число должно быть положительным!")
                    continue
            except ValueError:
                print("Некорректное число!")
                continue

            top_vacancies = json_saver.get_top_by_salary(n)
            if not top_vacancies:
                logger.info("Нет сохранённых вакансий.")
                print("Нет сохранённых вакансий.")
            else:
                print(f"\nТоп {n} вакансий по зарплате:")
                Vacancy.print_vacancies(top_vacancies)

        elif choice == "3":
            keyword = input("Введите ключевое слово для поиска: ").strip()
            if not keyword:
                print("Ключевое слово не может быть пустым!")
                continue

            results = json_saver.filter_by_keyword(keyword)
            if not results:
                logger.info("Вакансий с таким ключевым словом не найдено.")
                print("Вакансий с таким ключевым словом не найдено.")
            else:
                logger.info(f"\nНайдено {len(results)} вакансий с ключевым словом '{keyword}'")
                print(f"\nНайдено {len(results)} вакансий с ключевым словом '{keyword}':")
                Vacancy.print_vacancies(results)

        elif choice == "4":
            all_vacancies = json_saver.get_vacancies()
            if not all_vacancies:
                logger.info("Нет сохранённых вакансий.")
                print("Нет сохранённых вакансий.")
            else:
                logger.info(f"\nВсего сохранено вакансий: {len(all_vacancies)}")
                print(f"\nВсего сохранено вакансий: {len(all_vacancies)}")
                Vacancy.print_vacancies(all_vacancies)

        elif choice == "5":
            url = input("Введите URL вакансии для удаления: ").strip()
            if not url:
                print("URL не может быть пустым!")
                continue

            vacancy_to_delete = Vacancy(title="", url=url, salary="", description="", employer="", published_at="")

            if json_saver.delete_vacancy(vacancy_to_delete):
                logger.info("Вакансия удалена.")
                print("Вакансия удалена.")
            else:
                logger.info("Вакансия не найдена.")
                print("Вакансия не найдена.")

        elif choice == "6":
            try:
                min_sal = float(input("Минимальная зарплата: ") or 0)
                max_sal = float(input("Максимальная зарплата: ") or float("inf"))
                filtered = json_saver.filter_by_salary_range(min_sal, max_sal)
                logger.info(f"Найдено {len(filtered)} вакансий в диапазоне {min_sal}–{max_sal}")
                print(f"Найдено {len(filtered)} вакансий в диапазоне {min_sal}–{max_sal}")
                Vacancy.print_vacancies(filtered)
            except ValueError:
                logger.info("Некорректный формат зарплаты!")
                print("Некорректный формат зарплаты!")

        elif choice == "7":
            employer = input("Название работодателя: ").strip()
            if not employer:
                logger.info("Название работодателя не может быть пустым!")
                print("Название работодателя не может быть пустым!")
                continue

            results = json_saver.filter_by_employer(employer)
            if not results:
                logger.info(f"Вакансий от {employer} не найдено.")
                print(f"Вакансий от {employer} не найдено.")
            else:
                logger.info(f"\nНайдено {len(results)} вакансий от {employer}:")
                print(f"\nНайдено {len(results)} вакансий от {employer}:")
                Vacancy.print_vacancies(results)

        elif choice == "8":

            str_del = input("Удалить все вакансии? ").strip()
            if json_saver.delete_vacancy(
                Vacancy(title="", url=URL_HH, salary="", description="", employer="", published_at=""), str_del
            ):
                logger.info("Все вакансии удалены")
                print("Все вакансии удалены")
            else:
                logger.info("Удаление всех вакансий отменено")
                print("Удаление всех вакансий отменено")

        elif choice == "9":
            print("До свидания!")
            logger.info("Завершение работы программы")
            break

        else:
            print("Неверный выбор. Пожалуйста, введите число от 1 до 9.")


if __name__ == "__main__":
    user_interaction()

    # hh_api = HeadHunterAPI()
    # json_saver = JSONSaver()
    #
    # query = "программист"
    #
    # excluded_text = "1С"
    # per_page = 1
    # area_str = "Челябинск"
    # area_api = AreaAPI(area_str)
    # area_id = area_api.get_id_area()
    # print(area_id)
    #
    # print(f"Ищем вакансии по запросу '{query}'...")
    # # raw_vacancies = hh_api.get_request(query, excluded_text, area=area_id, per_page=per_page)
    # raw_vacancies = hh_api.get_requests(query=query, excluded_text=excluded_text, area=area_id, per_page=per_page)
    # if not raw_vacancies:
    #     print("Вакансий не найдено.")
    #
    # vacancies = [Vacancy.from_hh_api(item) for item in raw_vacancies]
    #
    # for vacancy in vacancies:
    #     json_saver._add_vacancy(vacancy)
    #
    # print(f"Найдено {len(vacancies)} вакансий. Они сохранены в файл.")
    #
    # top_vacancies = json_saver.get_top_by_salary(10)
    # for i, vacancy in enumerate(top_vacancies, 1):
    #     print(f"{i}. {vacancy.title()}")
    #     print(f"Зарплата: {vacancy.salary()}")
    #     print(f"Работодатель: {vacancy.employer()}")
    #     print(f"Ссылка: {vacancy.url()}")
    #     print("-! * 50")
