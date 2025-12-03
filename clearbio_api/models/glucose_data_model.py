from clearbio_api.database.get_db import Base
from sqlalchemy import Column, Integer, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

class GlucoseData(Base):
    __tablename__ = 'glucose_data'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    timestamp = Column(TIMESTAMP, primary_key=True)
    glucose_mmol = Column(DECIMAL(5, 2), nullable=False)

    user = relationship("Users", back_populates="glucose_data")