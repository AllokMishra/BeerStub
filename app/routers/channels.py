from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
import json

router = APIRouter(prefix="/api/v1/channels", tags=["channels"])

@router.post("/", response_model=schemas.Channel)
def create_channel(channel: schemas.ChannelCreate, db: Session = Depends(get_db)):
    db_channel = models.DispenserChannel(
        **channel.dict(exclude={"preset_volumes"}),
        preset_volumes=json.dumps(channel.preset_volumes)
    )
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel

@router.get("/machine/{machine_id}", response_model=list[schemas.Channel])
def read_machine_channels(machine_id: int, db: Session = Depends(get_db)):
    channels = db.query(models.DispenserChannel).filter(
        models.DispenserChannel.machine_id == machine_id
    ).all()
    
    # Convert preset_volumes from JSON string to list
    for channel in channels:
        if channel.preset_volumes:
            channel.preset_volumes = json.loads(channel.preset_volumes)
    return channels

@router.put("/{channel_id}", response_model=schemas.Channel)
def update_channel(
    channel_id: int, 
    channel: schemas.ChannelCreate, 
    db: Session = Depends(get_db)
):
    db_channel = db.query(models.DispenserChannel).filter(
        models.DispenserChannel.id == channel_id
    ).first()
    if not db_channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    for key, value in channel.dict(exclude={"preset_volumes"}).items():
        setattr(db_channel, key, value)
    
    db_channel.preset_volumes = json.dumps(channel.preset_volumes)
    db.commit()
    db.refresh(db_channel)
    return db_channel