from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure, ConfigurationError

try:
    client = MongoClient(
        "mongodb://localhost:27017/",
        server_api=ServerApi('1')
    )
except ConfigurationError as e:
    raise ConfigurationError("Помилка конфігурації.") from e
except ServerSelectionTimeoutError as e:
    raise ServerSelectionTimeoutError("Помилка підключення до сервера.") from e

db = client.task1

def drop_collection():
    """
    Видаляє колекцію котів.
    Якщо колекції не існує - нічого не відбувається.
    """
    try:
        db.cats.drop()
        print("Колекцію котів видалено.")
    except ServerSelectionTimeoutError:
        print("Помилка: сервер MongoDB недоступний.")
    except OperationFailure:
        print("Помилка: недостатньо прав доступу.")

def add_cat(name: str, age: int, features: list) -> None:
    """
    Додає нового кота до колекції.
    :param name: Ім'я кота
    :param age: Вік кота
    :param features: Список характеристик кота
    """
    try:
        cat = {"name": name, "age": age, "features": features}
        result = db.cats.insert_one(cat)
        print(f"Додано кота з ID: {result.inserted_id}")
    except ServerSelectionTimeoutError:
        print("Помилка: сервер MongoDB недоступний.")
    except OperationFailure:
        print("Помилка: недостатньо прав доступу.")

def find_all() -> None:
    """
    Виводить усі документи з колекції 'cats'. 
    Якщо колекція пуста, виводить повідомлення "Empty collection."
    """
    try:
        if db.cats.count_documents({}) == 0:
            print("Пуста колекція.")
            return

        result = db.cats.find()
        for el in result:
            print(el)
    except ServerSelectionTimeoutError:
        print("Помилка: сервер MongoDB недоступний.")
    except OperationFailure:
        print("Помилка: недостатньо прав доступу.")

def find_by_name(name: str) -> None:
    """
    Знаходить і виводить документ кота за його ім'ям.
    
    :param name: Ім'я кота, якого потрібно знайти.
    Якщо кота з таким ім'ям не знайдено, виводить повідомлення "No cats with this name."
    """
    try:
        result = db.cats.find_one({"name": name})

        if result is None:
            print(f"Кіт {name} не існує.")
            return

        print(result)
    except ServerSelectionTimeoutError:
        print("Помилка: сервер MongoDB недоступний.")
    except OperationFailure:
        print("Помилка: недостатньо прав доступу.")
    except TypeError:
        print("Помилка: неправильно вказаний тип даних для параметра 'name'.")

def update_age_by_name(name: str, age: int) -> None:
    """
    Оновлює вік кота за його ім'ям.
    
    :param name: Ім'я кота, вік якого потрібно оновити.
    :param age: Новий вік кота.
    Виводить повідомлення про результат оновлення.
    """
    try:
        result = db.cats.update_one({"name": name}, {"$set": {"age": age}})

        if result.matched_count == 1 and result.modified_count == 1:
            print(f"Кота {name} оновлено.")

        elif result.matched_count == 1 and result.modified_count == 0:
            print(f"У кота {name} вже вказано вік {age}.")

        else:
            print(f"Кота {name} не було оновлено.")
    except ServerSelectionTimeoutError:
        print("Помилка: сервер MongoDB недоступний.")
    except OperationFailure:
        print("Помилка: недостатньо прав доступу.")
    except TypeError:
        print("Помилка: неправильний тип даних для параметра 'name' або 'age'.")

def add_feature_by_name(name: str, feature: str) -> None:
    """
    Додає характеристику коту за його ім'ям.
    
    :param name: Ім'я кота, до якого потрібно додати характеристику.
    :param feature: Характеристика, яку потрібно додати.
    Виводить повідомлення про результат додавання.
    """
    try:
        result = db.cats.update_one({"name": name}, {"$addToSet": {"features": feature}})

        if result.matched_count == 1 and result.modified_count == 1:
            print(f"Кота {name} оновлено.")

        elif result.matched_count == 1 and result.modified_count == 0:
            print(f"Коту {name} вже вже додано фічу {feature}.")

        else:
            print(f"Кота {name} не було оновлено.")
    except ServerSelectionTimeoutError:
        print("Помилка: сервер MongoDB недоступний.")
    except OperationFailure:
        print("Помилка: недостатньо прав доступу.")
    except TypeError:
        print("Помилка: неправильний тип даних для параметра 'name' або 'feature'.")

def delete_cat_by_name(name: str) -> None:
    """
    Видаляє кота з колекції за його ім'ям.
    
    :param name: Ім'я кота, якого потрібно видалити.
    Виводить повідомлення про результат видалення.
    """
    try:
        result = db.cats.delete_one({"name": name})
        if result.deleted_count == 1:
            print(f"Кота {name} видалено.")
            return

        print(f"Кота {name} не існує.")
    except ServerSelectionTimeoutError:
        print("Помилка: сервер MongoDB недоступний.")
    except OperationFailure:
        print("Помилка: недостатньо прав доступу.")
    except TypeError:
        print("Помилка: неправильний тип даних для параметра 'name'.")

def delete_all_cats() -> None:
    """
    Видаляє всі документи з колекції 'cats'.
    Виводить кількість видалених котів.
    """
    try:
        result = db.cats.delete_many({})
        print(f"Видалено котів: {result.deleted_count}")
    except ServerSelectionTimeoutError:
        print("Помилка: сервер MongoDB недоступний.")
    except OperationFailure:
        print("Помилка: недостатньо прав доступу.")

if __name__ == "__main__":
    drop_collection()
    print("\nСтворюємо котів.")
    add_cat("barsik", 3, ["ходить в капці", "дає себе гладити", "рудий"])
    add_cat("Liza", 4, ["ходить в лоток", "дає себе гладити", "білий"])
    add_cat("Lama", 5, ["Ходить в лоток", "не дає себе гладити", "сірий"])

    print("\nЗнаходимо котів.")
    find_all()

    print("\nЗнайти кота за ім'ям 'barsik':")
    find_by_name("barsik")

    print("\nОновлюємо коту barsik його вік.")
    update_age_by_name("barsik", 5)
    find_by_name("barsik")

    print("\nОновлюємо коту barsik його фічу.")
    add_feature_by_name("barsik", "любить рибу")
    find_by_name("barsik")

    print("\nВидаляємо кота Liza з колекції котів.")
    delete_cat_by_name("Liza")
    find_by_name("Liza")

    print("\nВидаляємо всіх котів з колекції.")
    delete_all_cats()
    find_all()
