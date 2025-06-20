from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/v1/machines", tags=["machines"])

@router.post("/", response_model=schemas.Machine)
def create_machine(machine: schemas.MachineCreate, db: Session = Depends(get_db)):
    db_machine = models.DispenserMachine(**machine.dict())
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine

@router.get("/", response_model=list[schemas.Machine])
def read_machines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.DispenserMachine).offset(skip).limit(limit).all()

@router.get("/{machine_id}", response_model=schemas.Machine)
def read_machine(machine_id: int, db: Session = Depends(get_db)):
    machine = db.query(models.DispenserMachine).filter(
        models.DispenserMachine.id == machine_id
    ).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.post("/{machine_id}/door")
def control_door(machine_id: int, open: bool, db: Session = Depends(get_db)):
    machine = db.query(models.DispenserMachine).filter(
        models.DispenserMachine.id == machine_id
    ).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Implementation would use TCP server to send command
    return {"status": "success", "action": "open" if open else "close"}