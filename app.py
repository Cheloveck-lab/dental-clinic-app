from flask import Flask, jsonify, request # Импорт необходимых классов из Flask
from sqlalchemy import create_engine, or_ # Импорт классов для создания движка базы данных и выполнения операций OR
from sqlalchemy.orm import sessionmaker # Импорт класса для создания сессий
from datetime import datetime # Импорт класса для работы с датой и временем
from database_setup import Base, Doctor, Specialization, Patient, Appointment, Service, get_engine, create_all, drop_all # Импорт моделей и вспомогательных функций

app = Flask(__name__) # Создание экземпляра приложения Flask

engine = get_engine() # Создание движка базы данных
create_all(engine) # Создание всех таблиц в базе данных
DBSession = sessionmaker(bind=engine) # Создание класса для создания сессий

@app.route('/') # Определение маршрута для главной страницы
def index(): # Функция для обработки запроса к главной странице
    return jsonify({"message": "Welcome to the Dental Clinic API"}) # Возвращает приветственное сообщение в формате JSON

@app.route('/search', methods=['GET']) # Определение маршрута для поиска назначений
def search(): # Функция для обработки запроса на поиск назначений
    query = request.args.get('query', '') # Получение параметра query из запроса
    datetime_str = request.args.get('datetime', '') # Получение параметра datetime из запроса
    session = DBSession() # Создание сессии

    try:
        if datetime_str: # Проверка, если параметр datetime указан
            search_date = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M') # Преобразование строки в объект datetime
            results = session.query(Appointment).join(Doctor).join(Patient).join(Service).join(Specialization).filter(
                Appointment.appointment_time == search_date
            ).all() # Поиск назначений по дате и времени
        else: # Если параметр datetime не указан
            results = session.query(Appointment).join(Doctor).join(Patient).join(Service).join(Specialization).filter(or_(
                Doctor.name.like(f'%{query}%'),
                Specialization.name.like(f'%{query}%'),
                Patient.name.like(f'%{query}%'),
                Service.name.like(f'%{query}%')
            )).all() # Поиск назначений по ключевому слову

        return jsonify([{
            'id': appointment.id,
            'doctor': appointment.doctor.name,
            'specialization': appointment.specialization.name,
            'patient': appointment.patient.name,
            'service': appointment.service.name,
            'appointment_time': appointment.appointment_time.strftime('%Y-%m-%dT%H:%M')
        } for appointment in results]) # Возвращает результаты поиска в формате JSON
    except ValueError: # Обработка исключения, если формат даты и времени неверный
        return jsonify({"error": "Invalid datetime format"}), 400 # Возвращает ошибку формата даты и времени

@app.route('/appointments', methods=['GET']) # Определение маршрута для получения списка назначений
def get_appointments(): # Функция для обработки запроса на получение списка назначений
    session = DBSession() # Создание сессии
    results = session.query(Appointment).join(Doctor).join(Patient).all() # Получение списка всех назначений
    return jsonify([{
        'id': appointment.id,
        'doctor': appointment.doctor.name,
        'specialization': appointment.specialization.name,
        'patient': appointment.patient.name,
        'service': appointment.service.name,
        'appointment_time': appointment.appointment_time.strftime('%Y-%m-%dT%H:%M')
    } for appointment in results]) # Возвращает список назначений в формате JSON

@app.route('/appointments', methods=['POST']) # Определение маршрута для создания нового назначения
def new_appointment(): # Функция для обработки запроса на создание нового назначения
    data = request.get_json() # Получение данных из запроса в формате JSON
    doctor_name = data.get('doctor_name') # Получение имени доктора из данных запроса
    specialization_name = data.get('specialization_name') # Получение названия специализации из данных запроса
    patient_name = data.get('patient_name') # Получение имени пациента из данных запроса
    appointment_time = data.get('appointment_time') # Получение времени назначения из данных запроса
    service_name = data.get('service') # Получение названия услуги из данных запроса
    session = DBSession() # Создание сессии

    appointment_time = datetime.strptime(appointment_time, '%Y-%m-%dT%H:%M') # Преобразование строки времени назначения в объект datetime

    doctor = session.query(Doctor).filter_by(name=doctor_name).first() # Поиск записи о докторе по имени
    if not doctor: # Если запись о докторе не найдена
        doctor = Doctor(name=doctor_name) # Создание новой записи о докторе
        session.add(doctor) # Добавление записи о докторе в сессию
        session.commit() # Сохранение изменений в базе данных

    patient = session.query(Patient).filter_by(name=patient_name).first() # Поиск записи о пациенте по имени
    if not patient: # Если запись о пациенте не найдена
        patient = Patient(name=patient_name) # Создание новой записи о пациенте
        session.add(patient) # Добавление записи о пациенте в сессию
        session.commit() # Сохранение изменений в базе данных

    service = session.query(Service).filter_by(name=service_name).first() # Поиск записи об услуге по названию
    if not service: # Если запись об услуге не найдена
        service = Service(name=service_name) # Создание новой записи об услуге
        session.add(service) # Добавление записи об услуге в сессию
        session.commit() # Сохранение изменений в базе данных

    specialization = session.query(Specialization).filter_by(name=specialization_name).first() # Поиск записи о специализации по названию
    if not specialization: # Если запись о специализации не найдена
        specialization = Specialization(name=specialization_name) # Создание новой записи о специализации
        session.add(specialization) # Добавление записи о специализации в сессию
        session.commit() # Сохранение изменений в базе данных

    new_appointment = Appointment( # Создание нового назначения
        doctor_id=doctor.id,
        patient_id=patient.id,
        service_id=service.id,
        specialization_id=specialization.id,
        appointment_time=appointment_time
    )
    session.add(new_appointment) # Добавление нового назначения в сессию
    session.commit() # Сохранение изменений в базе данных

    return jsonify({"id": new_appointment.id, "message": "Appointment created successfully"}), 201 # Возвращает сообщение об успешном создании назначения

@app.route('/appointments/<int:appointment_id>', methods=['PUT']) # Определение маршрута для обновления существующего назначения
def edit_appointment(appointment_id): # Функция для обработки запроса на обновление существующего назначения
    data = request.get_json() # Получение данных из запроса в формате JSON
    session = DBSession() # Создание сессии
    appointment = session.query(Appointment).filter_by(id=appointment_id).one() # Поиск назначения по id

    doctor_name = data.get('doctor_name') # Получение имени доктора из данных запроса
    specialization_name = data.get('specialization_name') # Получение названия специализации из данных запроса
    patient_name = data.get('patient_name') # Получение имени пациента из данных запроса
    appointment_time = data.get('appointment_time') # Получение времени назначения из данных запроса
    service_name = data.get('service') # Получение названия услуги из данных запроса

    appointment_time = datetime.strptime(appointment_time, '%Y-%m-%dT%H:%M') # Преобразование строки времени назначения в объект datetime

    doctor = session.query(Doctor).filter_by(id=appointment.doctor_id).first() # Поиск записи о докторе по id
    if doctor: # Если запись о докторе найдена
        doctor.name = doctor_name # Обновление имени доктора
    else: # Если запись о докторе не найдена
        doctor = Doctor(name=doctor_name) # Создание новой записи о докторе
        session.add(doctor) # Добавление записи о докторе в сессию

    patient = session.query(Patient).filter_by(id=appointment.patient_id).first() # Поиск записи о пациенте по id
    if patient: # Если запись о пациенте найдена
        patient.name = patient_name # Обновление имени пациента
    else: # Если запись о пациенте не найдена
        patient = Patient(name=patient_name) # Создание новой записи о пациенте
        session.add(patient) # Добавление записи о пациенте в сессию

    service = session.query(Service).filter_by(id=appointment.service_id).first() # Поиск записи об услуге по id
    if service: # Если запись об услуге найдена
        service.name = service_name # Обновление названия услуги
    else: # Если запись об услуге не найдена
        service = Service(name=service_name) # Создание новой записи об услуге
        session.add(service) # Добавление записи об услуге в сессию

    specialization = session.query(Specialization).filter_by(id=appointment.specialization_id).first() # Поиск записи о специализации по id
    if specialization: # Если запись о специализации найдена
        specialization.name = specialization_name # Обновление названия специализации
    else: # Если запись о специализации не найдена
        specialization = Specialization(name=specialization_name) # Создание новой записи о специализации
        session.add(specialization) # Добавление записи о специализации в сессию

    appointment.doctor_id = doctor.id # Обновление id доктора в записи о назначении
    appointment.patient_id = patient.id # Обновление id пациента в записи о назначении
    appointment.service_id = service.id # Обновление id услуги в записи о назначении
    appointment.specialization_id = specialization.id # Обновление id специализации в записи о назначении
    appointment.appointment_time = appointment_time # Обновление времени назначения

    session.commit() # Сохранение изменений в базе данных

    return jsonify({"message": "Appointment updated successfully"}) # Возвращает сообщение об успешном обновлении назначения

@app.route('/appointments/<int:appointment_id>', methods=['DELETE']) # Определение маршрута для удаления существующего назначения
def delete_appointment(appointment_id): # Функция для обработки запроса на удаление существующего назначения
    session = DBSession() # Создание сессии
    appointment = session.query(Appointment).filter_by(id=appointment_id).one() # Поиск назначения по id
    session.delete(appointment) # Удаление назначения из базы данных
    session.commit() # Сохранение изменений в базе данных
    return jsonify({"message": "Appointment deleted successfully"}) # Возвращает сообщение об успешном удалении назначения

if __name__ == '__main__': # Проверка, выполняется ли скрипт напрямую
    app.debug = True # Включение режима отладки
    app.run(port=4996) # Запуск приложения на порту 4996