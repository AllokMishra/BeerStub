import socket
import threading
from datetime import datetime
from ..database import SessionLocal
from ..models import DispenserMachine
from ..utils.protocol import parse_frame, build_response

class TCPServer:
    def __init__(self, host='0.0.0.0', port=9000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.active_connections = {}
        self.running = False

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"TCP Server started on {self.host}:{self.port}")
        threading.Thread(target=self._accept_connections, daemon=True).start()

    def _accept_connections(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr),
                    daemon=True
                ).start()
            except Exception as e:
                print(f"Accept error: {e}")

    def _handle_client(self, client_socket, addr):
        device_id = None
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                # Parse incoming frame
                result = parse_frame(data)
                if not result:
                    continue

                device_id = result['device_id']
                self.active_connections[device_id] = client_socket

                # Update machine status
                db = SessionLocal()
                machine = db.query(DispenserMachine).filter(
                    DispenserMachine.device_id == device_id
                ).first()
                
                if machine:
                    machine.last_seen = datetime.now()
                    machine.is_online = True
                    db.commit()

                # Process command and send response
                response = build_response(result)
                if response:
                    client_socket.sendall(response)

        except Exception as e:
            print(f"Client error: {e}")
        finally:
            if device_id and device_id in self.active_connections:
                del self.active_connections[device_id]
                db = SessionLocal()
                machine = db.query(DispenserMachine).filter(
                    DispenserMachine.device_id == device_id
                ).first()
                if machine:
                    machine.is_online = False
                    db.commit()
            client_socket.close()

    def send_command(self, device_id, command_frame):
        if device_id in self.active_connections:
            try:
                self.active_connections[device_id].sendall(command_frame)
                return True
            except Exception as e:
                print(f"Send command error: {e}")
                return False
        return False

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()