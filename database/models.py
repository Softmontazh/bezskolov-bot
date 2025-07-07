from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import declarative_base  # <-- ORM здесь правильно

# или: from sqlalchemy.ext.declarative import declarative_base (если старый стиль)

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PaintRequest(BaseModel):  # Наследуем от BaseModel
    __tablename__ = "paint_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    color_code = Column(String, nullable=True, index=True)
    vin = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    image_id = Column(String, nullable=True)  # ID изображения в хранилище
    phone_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    notes = Column(String, nullable=True)  # Дополнительные заметки
    status = Column(String, default="pending")  # Статус запроса
