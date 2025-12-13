from src import app_logger
from src.api import AreaAPI
from src.api_hh import HeadHunterAPI
from src.vacancies import Vacancy
from src.work_files import JSONSaver


# Настройка логирования
logger = app_logger.get_logger("main.log")

def user_interaction():
    """ ФУНКЦИЯ ВЗАИМОДЕЙСТВИЯ С ПОЛЬЗОВАТЕЛЕМ"""

    print("Добро пожаловать в систему поиска вакансий!")
    print("=" * 50)

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
        print("8. Выход")

        choice = input("\nВведите номер действия (1–8): ").strip()

        if choice == "1":
            query = input("Введите поисковый запрос: ").strip()
            if not query:
                print("Запрос не может быть пустым!")
                continue

            excluded_text = input("Введите слова исключения в запросе: ").strip()


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


            print(f"Ищем вакансии по запросу '{query}'...")
            raw_vacancies = hh_api.get_vacancies(query, excluded_text, area=area_id, per_page=per_page)

            if not raw_vacancies:
                print("Вакансий не найдено.")
                continue

            vacancies = [Vacancy.from_hh_api(item) for item in raw_vacancies]

            for vacancy in vacancies:
                json_saver.add_vacancy(vacancy)

            print(f"Найдено {len(vacancies)} вакансий. Они сохранены в файл.")

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
                print("Нет сохранённых вакансий.")
            else:
                print(f"\nТоп {n} вакансий по зарплате:")
                for i, vacancy in enumerate(top_vacancies, 1):
                    print(f"{i}. {vacancy.title()}")
                    print(f"Зарплата: {vacancy.salary()}")
                    print(f"Работодатель: {vacancy.employer()}")
                    print(f"Ссылка: {vacancy.url()}")
                    print("-! * 50")

        elif choice == "3":
            keyword = input("Введите ключевое слово для поиска: ").strip()
            if not keyword:
                print("Ключевое слово не может быть пустым!")
                continue

            results = json_saver.filter_by_keyword(keyword)
            if not results:
                print("Вакансий с таким ключевым словом не найдено.")
            else:
                print(f"\nНайдено {len(results)} вакансий с ключевым словом '{keyword}':")
                for i, vacancy in enumerate(results, 1):
                    print(f"{i}. {vacancy.title()}")
                    print(f"Зарплата: {vacancy.salary()}")
                    print(f"Описание: {vacancy.description()[:100]}...")
                    print(f"Ссылка: {vacancy.url()}")
                    print("-! * 50")

        elif choice == "4":
            all_vacancies = json_saver.get_vacancies()
            if not all_vacancies:
                print("Нет сохранённых вакансий.")
            else:
                print(f"\nВсего сохранено вакансий: {len(all_vacancies)}")
                for i, vacancy in enumerate(all_vacancies, 1):
                    print(f"{i}. {vacancy.title()}")
                    print(f"Зарплата: {vacancy.salary()}")
                    print(f"   Работодатель: {vacancy.employer()}")
                    print(f"Ссылка: {vacancy.url()}")
                    print("-! * 50")

        elif choice == "5":
            url = input("Введите URL вакансии для удаления: ").strip()
            if not url:
                print("URL не может быть пустым!")
                continue

            vacancy_to_delete = Vacancy(
                title="",
                url=url,
                salary=None,
                description="",
                employer=""
            )

            if json_saver.delete_vacancy(vacancy_to_delete):
                print("Вакансия удалена.")
            else:
                print("Вакансия не найдена.")

        elif choice == "6":
            try:
                min_sal = float(input("Минимальная зарплата: ") or 0)
                max_sal = float(input("Максимальная зарплата: ") or float('inf'))
                filtered = json_saver.filter_by_salary_range(min_sal, max_sal)
                print(f"Найдено {len(filtered)} вакансий в диапазоне {min_sal}–{max_sal}")
                for i, vacancy in enumerate(filtered, 1):
                    print(f"{i}. {vacancy.title()} ({vacancy.salary()})")
                    print(f"{vacancy.url()}")
                    print("-! * 50")
            except ValueError:
                print("Некорректный формат зарплаты!")

        elif choice == "7":
            employer = input("Название работодателя: ").strip()
            if not employer:
                print("Название работодателя не может быть пустым!")
                continue

            results = json_saver.filter_by_employer(employer)
            if not results:
                print(f"Вакансий от {employer} не найдено.")
            else:
                print(f"\nНайдено {len(results)} вакансий от {employer}:")
                for i, vacancy in enumerate(results, 1):
                    print(f"{i}. {vacancy.title()} ({vacancy.salary()})")
                    print(f"{vacancy.url()}")
                    print("-! * 50")

        elif choice == "8":
            print("До свидания!")
            break

        else:
            print("Неверный выбор. Пожалуйста, введите число от 1 до 8.")


if __name__ == "__main__":
    user_interaction()