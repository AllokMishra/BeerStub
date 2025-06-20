from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class DispenserMachine(Base):
    __tablename__ = "dispenser_machines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    device_id = Column(String, unique=True, index=True)
    ip_address = Column(String)
    firmware_version = Column(String)
    last_seen = Column(DateTime)
    is_online = Column(Boolean, default=False)
    channels = relationship("DispenserChannel", back_populates="machine")

class DispenserChannel(Base):
    __tablename__ = "dispenser_channels"
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("dispenser_machines.id"))
    channel_number = Column(Integer)
    drink_name = Column(String)
    current_volume_ml = Column(Float)
    max_volume_ml = Column(Float)
    preset_volumes = Column(String)  # JSON string of [250, 500, 1000]
    is_active = Column(Boolean, default=True)
    machine = relationship("DispenserMachine", back_populates="channels")

class DispenseLog(Base):
    __tablename__ = "dispense_logs"
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("dispenser_machines.id"))
    channel_id = Column(Integer, ForeignKey("dispenser_channels.id"))
    volume_ml = Column(Float)
    timestamp = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String)  # "success", "failed", "partial"
    error_message = Column(String)