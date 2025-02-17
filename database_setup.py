from sqlalchemy import Column, ForeignKey, Integer, String, DateTime # Импорт необходимых классов из SQLAlchemy
from sqlalchemy.orm import relationship, declarative_base # Импорт классов для создания отношений и базовой модели
from sqlalchemy.orm import sessionmaker # Импорт класса для создания сессий
from sqlalchemy import create_engine # Импорт класса для создания движка базы данных

Base = declarative_base() # Создание базового класса для всех моделей

class Doctor(Base): # Определение модели Doctor (Доктор)
    __tablename__ = 'doctor' # Название таблицы в базе данных
    id = Column(Integer, primary_key=True) # Определение столбца id как первичного ключа
    name = Column(String(250), nullable=False) # Определение столбца name как строки длиной до 250 символов, обязательное поле
    appointments = relationship('Appointment', back_populates='doctor', cascade="all, delete-orphan") # Определение отношения с таблицей Appointment

class Specialization(Base): # Определение модели Specialization (Специализация)
    __tablename__ = 'specialization' # Название таблицы в базе данных
    id = Column(Integer, primary_key=True) # Определение столбца id как первичного ключа
    name = Column(String(250), nullable=False) # Определение столбца name как строки длиной до 250 символов, обязательное поле
    appointments = relationship('Appointment', back_populates='specialization', cascade="all, delete-orphan") # Определение отношения с таблицей Appointment

class Patient(Base): # Определение модели Patient (Пациент)
    __tablename__ = 'patient' # Название таблицы в базе данных
    id = Column(Integer, primary_key=True) # Определение столбца id как первичного ключа
    name = Column(String(250), nullable=False) # Определение столбца name как строки длиной до 250 символов, обязательное поле
    appointments = relationship('Appointment', back_populates='patient', cascade="all, delete-orphan") # Определение отношения с таблицей Appointment

class Service(Base): # Определение модели Service (Услуга)
    __tablename__ = 'service' # Название таблицы в базе данных
    id = Column(Integer, primary_key=True) # Определение столбца id как первичного ключа
    name = Column(String(250), nullable=False) # Определение столбца name как строки длиной до 250 символов, обязательное поле
    appointments = relationship('Appointment', back_populates='service', cascade="all, delete-orphan") # Определение отношения с таблицей Appointment

class Appointment(Base): # Определение модели Appointment (Назначение)
    __tablename__ = 'appointment' # Название таблицы в базе данных
    id = Column(Integer, primary_key=True) # Определение столбца id как первичного ключа
    doctor_id = Column(Integer, ForeignKey('doctor.id')) # Определение столбца doctor_id как внешнего ключа, ссылающегося на таблицу doctor
    patient_id = Column(Integer, ForeignKey('patient.id')) # Определение столбца patient_id как внешнего ключа, ссылающегося на таблицу patient
    service_id = Column(Integer, ForeignKey('service.id')) # Определение столбца service_id как внешнего ключа, ссылающегося на таблицу service
    specialization_id = Column(Integer, ForeignKey('specialization.id')) # Определение столбца specialization_id как внешнего ключа, ссылающегося на таблицу specialization
    appointment_time = Column(DateTime, nullable=False) # Определение столбца appointment_time как даты и времени, обязательное поле
    
    doctor = relationship('Doctor', back_populates='appointments') # Определение отношения с таблицей Doctor
    patient = relationship('Patient', back_populates='appointments') # Определение отношения с таблицей Patient
    service = relationship('Service', back_populates='appointments') # Определение отношения с таблицей Service
    specialization = relationship('Specialization', back_populates='appointments') # Определение отношения с таблицей Specialization

def get_engine(): # Функция для создания движка базы данных
    return create_engine('sqlite:///:memory:') # Создание движка базы данных SQLite в памяти

def create_all(engine): # Функция для создания всех таблиц в базе данных
    Base.metadata.create_all(engine) # Создание всех таблиц на основе определенных моделей

def drop_all(engine): # Функция для удаления всех таблиц из базы данных
    Base.metadata.drop_all(engine) # Удаление всех таблиц