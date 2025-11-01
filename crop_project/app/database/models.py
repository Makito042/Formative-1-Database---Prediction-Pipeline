from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from .database import Base

class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)

    readings = relationship("Reading", back_populates="crop")

class SoilType(Base):
    __tablename__ = "soil_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    # Removed relationship with Reading as we're now using soil_name directly

class GrowthStage(Base):
    __tablename__ = "growth_stages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)

    readings = relationship("Reading", back_populates="growth_stage")

class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"))
    soil_name = Column(String(255), index=True)  # Changed from soil_type_id to soil_name
    growth_stage_id = Column(Integer, ForeignKey("growth_stages.id"))
    moi = Column(Float)
    temp = Column(Float)
    humidity = Column(Float)
    result = Column(Integer, nullable=True)
    timestamp = Column(TIMESTAMP)

    crop = relationship("Crop", back_populates="readings")
    growth_stage = relationship("GrowthStage", back_populates="readings")

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String(255))
    timestamp = Column(TIMESTAMP)
