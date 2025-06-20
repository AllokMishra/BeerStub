import struct
from datetime import datetime
from ..models import DispenserMachine, DispenserChannel
from ..database import SessionLocal

def parse_frame(data: bytes) -> dict:
    """Parse incoming V5 protocol frame"""
    if not data.startswith(b'\x68') or len(data) < 10:
        return None
    
    try:
        device_id = data[1:7]
        control_code = data[8]
        length = data[9]
        
        if len(data) < 10 + length:
            return None
        
        payload = data[10:10+length]
        
        result = {
            "device_id": device_id.hex(),
            "control_code": control_code,
            "length": length,
            "payload": payload
        }
        
        # Parse specific commands
        if control_code == 0x01:  # Read command
            if payload.startswith(b'\x66\x66'):  # Heartbeat
                result["command"] = "heartbeat"
            elif payload.startswith(b'\x4A\x01'):  # Door status
                result["command"] = "door_status"
        
        elif control_code == 0x04:  # Write command
            if payload.startswith(b'\x44\x44'):  # Pour command
                result["command"] = "pour"
                result["channel"] = payload[2]
                result["volume"] = struct.unpack('<H', payload[3:5])[0]
                result["payment_id"] = payload[5:10].hex()
            elif payload.startswith(b'\x4A\x08'):  # Inventory status
                result["command"] = "inventory_status"
                result["channel"] = payload[2]
                result["status"] = "low" if payload[3] == 0x02 else "normal"
        
        return result
    
    except Exception as e:
        print(f"Frame parsing error: {e}")
        return None

def build_pour_command(device_id: str, channel: int, volume_ml: int) -> bytes:
    """Build V5 protocol pour command frame"""
    frame = bytearray()
    frame.append(0x68)  # Start flag
    frame.extend(bytes.fromhex(device_id))
    frame.append(0x68)  # Start flag again
    frame.append(0x04)  # Control code (write)
    frame.append(0x07)  # Length
    frame.extend([0x44, 0x44])  # Pour command
    frame.append(channel)
    frame.extend(struct.pack('<H', volume_ml))
    frame.extend(b'\x00\x00\x00\x00\x00')  # Default payment ID
    frame.append(calculate_checksum(frame))
    frame.append(0x16)  # End flag
    return bytes(frame)

def calculate_checksum(data: bytes) -> int:
    """Calculate V5 protocol checksum"""
    return sum(data) % 256