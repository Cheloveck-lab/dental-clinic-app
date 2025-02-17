import pytest # Импорт библиотеки pytest для написания и выполнения тестов
from sqlalchemy import create_engine # Импорт класса для создания движка базы данных
from sqlalchemy.orm import sessionmaker # Импорт класса для создания сессий
from datetime import datetime # Импорт класса для работы с датами и временем
from database_setup import Base, Doctor, Specialization, Patient, Appointment, Service, create_all, drop_all, get_engine # Импорт моделей и вспомогательных функций
from app import app, engine # Импорт приложения Flask и движка базы данных

@pytest.fixture(scope="function", autouse=True) # Определение фикстуры для настройки и очистки окружения перед и после каждого теста
def setup_and_teardown(): # Функция настройки и очистки окружения
    create_all(engine) # Создание всех таблиц в базе данных
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Создание класса для создания сессий
    session = TestingSessionLocal() # Создание сессии
    
    yield session # Передача управления тесту
    
    session.close() # Закрытие сессии
    drop_all(engine) # Удаление всех таблиц из базы данных

@pytest.fixture(scope="function") # Определение фикстуры для создания сессии базы данных
def db_session(request): # Функция создания сессии базы данных
    return request.getfixturevalue("setup_and_teardown") # Возвращает сессию базы данных

@pytest.fixture(scope="function") # Определение фикстуры для создания клиента тестирования
def test_client(): # Функция создания клиента тестирования
    app.config['TESTING'] = True # Включение режима тестирования
    with app.test_client() as client: # Создание клиента тестирования
        with app.app_context(): # Установка контекста приложения
            yield client # Передача управления тесту

class TestDatabase: # Определение класса для тестирования базы данных
    def test_create_doctor(self, db_session): # Тест для создания нового доктора
        new_doctor = Doctor(name="Dr. Smith") # Создание новой записи о докторе
        db_session.add(new_doctor) # Добавление записи о докторе в сессию
        db_session.commit() # Сохранение изменений в базе данных
        doctor = db_session.query(Doctor).filter_by(name="Dr. Smith").first() # Поиск записи о докторе по имени
        assert doctor is not None # Проверка, что запись о докторе найдена
        assert doctor.name == "Dr. Smith" # Проверка, что имя доктора совпадает с ожидаемым

    def test_create_specialization(self, db_session): # Тест для создания новой специализации
        new_specialization = Specialization(name="Dentistry") # Создание новой записи о специализации
        db_session.add(new_specialization) # Добавление записи о специализации в сессию
        db_session.commit() # Сохранение изменений в базе данных
        specialization = db_session.query(Specialization).filter_by(name="Dentistry").first() # Поиск записи о специализации по названию
        assert specialization is not None # Проверка, что запись о специализации найдена
        assert specialization.name == "Dentistry" # Проверка, что название специализации совпадает с ожидаемым

    def test_create_patient(self, db_session): # Тест для создания нового пациента
        new_patient = Patient(name="John Doe") # Создание новой записи о пациенте
        db_session.add(new_patient) # Добавление записи о пациенте в сессию
        db_session.commit() # Сохранение изменений в базе данных
        patient = db_session.query(Patient).filter_by(name="John Doe").first() # Поиск записи о пациенте по имени
        assert patient is not None # Проверка, что запись о пациенте найдена
        assert patient.name == "John Doe" # Проверка, что имя пациента совпадает с ожидаемым

    def test_create_service(self, db_session): # Тест для создания новой услуги
        new_service = Service(name="Cleaning") # Создание новой записи об услуге
        db_session.add(new_service) # Добавление записи об услуге в сессию
        db_session.commit() # Сохранение изменений в базе данных
        service = db_session.query(Service).filter_by(name="Cleaning").first() # Поиск записи об услуге по названию
        assert service is not None # Проверка, что запись об услуге найдена
        assert service.name == "Cleaning" # Проверка, что название услуги совпадает с ожидаемым

    def test_create_appointment(self, db_session): # Тест для создания нового назначения
        new_doctor = Doctor(name="Dr. Smith") # Создание новой записи о докторе
        new_specialization = Specialization(name="Dentistry") # Создание новой записи о специализации
        new_patient = Patient(name="John Doe") # Создание новой записи о пациенте
        new_service = Service(name="Cleaning") # Создание новой записи об услуге
        db_session.add(new_doctor) # Добавление записи о докторе в сессию
        db_session.add(new_specialization) # Добавление записи о специализации в сессию
        db_session.add(new_patient) # Добавление записи о пациенте в сессию
        db_session.add(new_service) # Добавление записи об услуге в сессию
        db_session.commit() # Сохранение изменений в базе данных

        appointment_time = datetime.strptime("2025-02-15 10:00", '%Y-%m-%d %H:%M') # Преобразование строки времени назначения в объект datetime
        new_appointment = Appointment( # Создание нового назначения
            doctor_id=new_doctor.id,
            patient_id=new_patient.id,
            service_id=new_service.id,
            specialization_id=new_specialization.id,
            appointment_time=appointment_time
        )
        db_session.add(new_appointment) # Добавление нового назначения в сессию
        db_session.commit() # Сохранение изменений в базе данных
        appointment = db_session.query(Appointment).filter_by(doctor_id=new_doctor.id).first() # Поиск назначения по id доктора
        assert appointment is not None # Проверка, что назначение найдено
        assert appointment.doctor_id == new_doctor.id # Проверка, что id доктора совпадает с ожидаемым
        assert appointment.patient_id == new_patient.id # Проверка, что id пациента совпадает с ожидаемым
        assert appointment.service_id == new_service.id # Проверка, что id услуги совпадает с ожидаемым
        assert appointment.specialization_id == new_specialization.id # Проверка, что id специализации совпадает с ожидаемым
        assert appointment.appointment_time == appointment_time # Проверка, что время назначения совпадает с ожидаемым

class TestApp: # Определение класса для тестирования приложения
    def test_index(self, test_client): # Тест для главной страницы
        response = test_client.get("/") # Выполнение GET-запроса к главной странице
        assert response.status_code == 200 # Проверка, что статус ответа 200 (OK)
        assert response.json == {"message": "Welcome to the Dental Clinic API"} # Проверка, что ответ содержит ожидаемое сообщение

    def test_create_appointment(self, test_client): # Тест для создания нового назначения через API
        response = test_client.post("/appointments", json={ # Выполнение POST-запроса для создания нового назначения
            "doctor_name": "Dr. Smith",
            "specialization_name": "Dentistry",
            "patient_name": "John Doe",
            "appointment_time": "2025-02-15T10:00",
            "service": "Cleaning"
        })
        assert response.status_code == 201 # Проверка, что статус ответа 201 (Created)
        assert response.json["message"] == "Appointment created successfully" # Проверка, что ответ содержит ожидаемое сообщение
        assert response.json["id"] is not None # Проверка, что ответ содержит id нового назначения

    def test_get_appointments(self, test_client): # Тест для получения списка назначений через API
        response = test_client.post("/appointments", json={ # Выполнение POST-запроса для создания нового назначения
            "doctor_name": "Dr. Smith",
            "specialization_name": "Dentistry",
            "patient_name": "John Doe",
            "appointment_time": "2025-02-15T10:00",
            "service": "Cleaning"
        })
        assert response.status_code == 201 # Проверка, что статус ответа 201 (Created)

        response = test_client.get("/appointments") # Выполнение GET-запроса для получения списка назначений
        assert response.status_code == 200 # Проверка, что статус ответа 200 (OK)
        assert len(response.json) == 1 # Проверка, что в списке назначений одно назначение

    def test_update_appointment(self, test_client): # Тест для обновления существующего назначения через API
        response = test_client.post("/appointments", json={ # Выполнение POST-запроса для создания нового назначения
            "doctor_name": "Dr. Smith",
            "specialization_name": "Dentistry",
            "patient_name": "John Doe",
            "appointment_time": "2025-02-15T10:00",
            "service": "Cleaning"
        })
        assert response.status_code == 201 # Проверка, что статус ответа 201 (Created)
        appointment_id = response.json["id"] # Получение id нового назначения
        response = test_client.put(f"/appointments/{appointment_id}", json={ # Выполнение PUT-запроса для обновления существующего назначения
            "doctor_name": "Dr. Brown",
            "specialization_name": "Orthodontics",
            "patient_name": "Jane Doe",
            "appointment_time": "2025-02-15T11:00",
            "service": "Braces"
        })
        assert response.status_code == 200 # Проверка, что статус ответа 200 (OK)
        assert response.json["message"] == "Appointment updated successfully" # Проверка, что ответ содержит ожидаемое сообщение

    def test_delete_appointment(self, test_client): # Тест для удаления существующего назначения через API
        response = test_client.post("/appointments", json={ # Выполнение POST-запроса для создания нового назначения
            "doctor_name": "Dr. Smith",
            "specialization_name": "Dentistry",
            "patient_name": "John Doe",
            "appointment_time": "2025-02-15T10:00",
            "service": "Cleaning"
        })
        assert response.status_code == 201 # Проверка, что статус ответа 201 (Created)
        appointment_id = response.json["id"] # Получение id нового назначения
        response = test_client.delete(f"/appointments/{appointment_id}") # Выполнение DELETE-запроса для удаления существующего назначения
        assert response.status_code == 200 # Проверка, что статус ответа 200 (OK)
        assert response.json["message"] == "Appointment deleted successfully" # Проверка, что ответ содержит ожидаемое сообщение
        response = test_client.get("/appointments") # Выполнение GET-запроса для получения списка назначений
        assert len(response.json) == 0 # Проверка, что список назначений пуст

    def test_search_appointments_by_query(self, test_client): # Тест для поиска назначений по ключевому слову через API
        response = test_client.post("/appointments", json={ # Выполнение POST-запроса для создания нового назначения
            "doctor_name": "Dr. Smith",
            "specialization_name": "Dentistry",
            "patient_name": "John Doe",
            "appointment_time": "2025-02-15T10:00",
            "service": "Cleaning"
        })
        assert response.status_code == 201 # Проверка, что статус ответа 201 (Created)
        response = test_client.get("/search?query=Smith") # Выполнение GET-запроса для поиска назначений по ключевому слову
        assert response.status_code == 200 # Проверка, что статус ответа 200 (OK)
        assert len(response.json) == 1 # Проверка, что найдено одно назначение
        assert response.json[0]["doctor"] == "Dr. Smith" # Проверка, что имя доктора в найденном назначении совпадает с ожидаемым

    def test_search_appointments_by_datetime(self, test_client): # Тест для поиска назначений по дате и времени через API
        response = test_client.post("/appointments", json={ # Выполнение POST-запроса для создания нового назначения
            "doctor_name": "Dr. Smith",
            "specialization_name": "Dentistry",
            "patient_name": "John Doe",
            "appointment_time": "2025-02-15T10:00",
            "service": "Cleaning"
        })
        assert response.status_code == 201 # Проверка, что статус ответа 201 (Created)
        response = test_client.get("/search?datetime=2025-02-15T10:00") # Выполнение GET-запроса для поиска назначений по дате и времени
        assert response.status_code == 200 # Проверка, что статус ответа 200 (OK)
        assert len(response.json) == 1 # Проверка, что найдено одно назначение
        assert response.json[0]["appointment_time"] == "2025-02-15T10:00" # Проверка, что время назначения в найденном назначении совпадает с ожидаемым

    def test_invalid_datetime_format(self, test_client): # Тест для проверки обработки неверного формата даты и времени через API
        response = test_client.get("/search?datetime=invalid-datetime") # Выполнение GET-запроса с неверным форматом даты и времени
        assert response.status_code == 400 # Проверка, что статус ответа 400 (Bad Request)
        assert response.json == {"error": "Invalid datetime format"} # Проверка, что ответ содержит ожидаемое сообщение об ошибке