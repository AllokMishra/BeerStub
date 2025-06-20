from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .routers import devices, channels, dispense, reports, auth
from .services.tcp_server import TCPServer
from .services.websocket import websocket_manager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Beer Dispenser Management System")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(channels.router)
app.include_router(dispense.router)
app.include_router(reports.router)

# WebSocket endpoint
app.add_api_websocket_route("/ws", websocket_manager.handle_websocket)

# TCP Server instance
tcp_server = TCPServer()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting TCP server...")
    tcp_server.start()
    logger.info("Service startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down TCP server...")
    tcp_server.stop()
    logger.info("Service shutdown complete")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}