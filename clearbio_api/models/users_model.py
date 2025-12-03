from clearbio_api.database.get_db import Base
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)

    glucose_data = relationship("GlucoseData", back_populates="user")