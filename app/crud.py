from datetime import datetime
from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
import json

def get_machine(db: Session, machine_id: int):
    return db.query(models.DispenserMachine).filter(models.DispenserMachine.id == machine_id).first()

def get_machine_by_device_id(db: Session, device_id: str):
    return db.query(models.DispenserMachine).filter(models.DispenserMachine.device_id == device_id).first()

def get_machines(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DispenserMachine).offset(skip).limit(limit).all()

def create_machine(db: Session, machine: schemas.MachineCreate):
    db_machine = models.DispenserMachine(**machine.dict())
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine

def get_channel(db: Session, channel_id: int):
    return db.query(models.DispenserChannel).filter(models.DispenserChannel.id == channel_id).first()

def get_channels_by_machine(db: Session, machine_id: int):
    channels = db.query(models.DispenserChannel).filter(
        models.DispenserChannel.machine_id == machine_id
    ).all()
    for channel in channels:
        if channel.preset_volumes:
            channel.preset_volumes = json.loads(channel.preset_volumes)
    return channels

def update_channel_volume(db: Session, channel_id: int, volume_ml: float):
    channel = db.query(models.DispenserChannel).filter(models.DispenserChannel.id == channel_id).first()
    if channel:
        channel.current_volume_ml = volume_ml
        db.commit()
        return channel
    return None

def create_dispense_log(
    db: Session,
    machine_id: int,
    channel_id: int,
    volume_ml: float,
    user_id: int,
    status: str = "success",
    error_message: str = None
):
    log = models.DispenseLog(
        machine_id=machine_id,
        channel_id=channel_id,
        volume_ml=volume_ml,
        user_id=user_id,
        status=status,
        error_message=error_message,
        timestamp=datetime.now()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_dispense_logs(
    db: Session,
    machine_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
):
    query = db.query(models.DispenseLog)
    
    if machine_id:
        query = query.filter(models.DispenseLog.machine_id == machine_id)
    if channel_id:
        query = query.filter(models.DispenseLog.channel_id == channel_id)
    if start_date:
        query = query.filter(models.DispenseLog.timestamp >= start_date)
    if end_date:
        query = query.filter(models.DispenseLog.timestamp <= end_date)
    
    return query.offset(skip).limit(limit).all()