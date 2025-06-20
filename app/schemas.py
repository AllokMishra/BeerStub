from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        orm_mode = True

class MachineBase(BaseModel):
    name: str
    device_id: str

class MachineCreate(MachineBase):
    ip_address: str

class Machine(MachineBase):
    id: int
    is_online: bool
    last_seen: Optional[datetime]
    
    class Config:
        orm_mode = True

class ChannelBase(BaseModel):
    channel_number: int
    drink_name: str
    max_volume_ml: float

class ChannelCreate(ChannelBase):
    preset_volumes: List[float]

class Channel(ChannelBase):
    id: int
    machine_id: int
    current_volume_ml: float
    is_active: bool
    
    class Config:
        orm_mode = True

class DispenseCommand(BaseModel):
    machine_id: int
    channel_id: int
    volume_ml: float

class DispenseLog(BaseModel):
    id: int
    machine_id: int
    channel_id: int
    volume_ml: float
    timestamp: datetime
    status: str
    
    class Config:
        orm_mode = True