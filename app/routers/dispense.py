from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..services.tcp_server import tcp_server
from ..utils.protocol import build_pour_command
from ..crud import create_dispense_log, update_channel_volume
from datetime import datetime
import json

router = APIRouter(prefix="/api/v1/dispense", tags=["dispense"])

@router.post("/pour")
def dispense_beer(command: schemas.DispenseCommand, db: Session = Depends(get_db)):
    # Get machine and channel
    machine = db.query(models.DispenserMachine).filter(
        models.DispenserMachine.id == command.machine_id
    ).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    channel = db.query(models.DispenserChannel).filter(
        models.DispenserChannel.id == command.channel_id,
        models.DispenserChannel.machine_id == command.machine_id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Check if machine is online
    if not machine.is_online:
        raise HTTPException(status_code=400, detail="Machine is offline")
    
    # Check channel status
    if not channel.is_active:
        raise HTTPException(status_code=400, detail="Channel is inactive")
    
    # Check volume
    if command.volume_ml > channel.current_volume_ml:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough volume in channel. Available: {channel.current_volume_ml}ml"
        )
    
    # Build and send command
    command_frame = build_pour_command(
        machine.device_id,
        channel.channel_number,
        command.volume_ml
    )
    
    if not tcp_server.send_command(machine.device_id, command_frame):
        raise HTTPException(status_code=500, detail="Failed to send command to machine")
    
    # Update channel volume
    new_volume = channel.current_volume_ml - command.volume_ml
    update_channel_volume(db, channel.id, new_volume)
    
    # Log the dispense
    log = create_dispense_log(
        db,
        machine_id=machine.id,
        channel_id=channel.id,
        volume_ml=command.volume_ml,
        user_id=1  # Replace with actual user ID from auth
    )
    
    return {
        "status": "success",
        "volume_dispensed": command.volume_ml,
        "remaining_volume": new_volume,
        "log_id": log.id
    }

@router.post("/emergency-stop/{machine_id}")
def emergency_stop(machine_id: int, db: Session = Depends(get_db)):
    machine = db.query(models.DispenserMachine).filter(
        models.DispenserMachine.id == machine_id
    ).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Implementation would send emergency stop command via TCP
    return {"status": "emergency_stop_sent"}