"""
WebSocket server for real-time updates
"""
import asyncio
import json
import logging
from typing import Dict, Set
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.connected_clients: Set[str] = set()
        self.rooms: Dict[str, Set[str]] = {
            'dashboard': set(),
            'crm': set(),
            'finance': set(),
            'hr': set(),
            'inventory': set(),
            'projects': set(),
        }
        
    def add_client(self, client_id: str):
        """Add a new connected client"""
        self.connected_clients.add(client_id)
        logger.info(f"Client {client_id} connected. Total clients: {len(self.connected_clients)}")
        
    def remove_client(self, client_id: str):
        """Remove a disconnected client"""
        self.connected_clients.discard(client_id)
        # Remove from all rooms
        for room_clients in self.rooms.values():
            room_clients.discard(client_id)
        logger.info(f"Client {client_id} disconnected. Total clients: {len(self.connected_clients)}")
        
    def join_room(self, client_id: str, room: str):
        """Add client to a specific room"""
        if room in self.rooms:
            self.rooms[room].add(client_id)
            logger.info(f"Client {client_id} joined room {room}")
            
    def leave_room(self, client_id: str, room: str):
        """Remove client from a specific room"""
        if room in self.rooms:
            self.rooms[room].discard(client_id)
            logger.info(f"Client {client_id} left room {room}")
            
    def broadcast_to_room(self, room: str, event: str, data: dict):
        """Broadcast data to all clients in a room"""
        if room in self.rooms and self.rooms[room]:
            self.socketio.emit(event, data, room=room)
            logger.info(f"Broadcasted {event} to {len(self.rooms[room])} clients in room {room}")
            
    def broadcast_to_all(self, event: str, data: dict):
        """Broadcast data to all connected clients"""
        self.socketio.emit(event, data)
        logger.info(f"Broadcasted {event} to {len(self.connected_clients)} clients")

# Global WebSocket manager instance
ws_manager = None

def init_websocket(app: Flask):
    """Initialize WebSocket server"""
    global ws_manager
    
    socketio = SocketIO(
        app,
        cors_allowed_origins=app.config['CORS_ORIGINS'],  # IMPORTANT
        async_mode="threading",  # Using threading for Python 3.12+ compatibility
    )
    
    ws_manager = WebSocketManager(socketio)
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        client_id = request.sid
        ws_manager.add_client(client_id)
        emit('connected', {'message': 'Connected to real-time updates'})
        
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        client_id = request.sid
        ws_manager.remove_client(client_id)
        
    @socketio.on('join_room')
    def handle_join_room(data):
        """Handle client joining a room"""
        client_id = request.sid
        room = data.get('room', 'dashboard')
        ws_manager.join_room(client_id, room)
        join_room(room)
        emit('joined_room', {'room': room})
        
    @socketio.on('leave_room')
    def handle_leave_room(data):
        """Handle client leaving a room"""
        client_id = request.sid
        room = data.get('room', 'dashboard')
        ws_manager.leave_room(client_id, room)
        leave_room(room)
        emit('left_room', {'room': room})
        
    @socketio.on('ping')
    def handle_ping():
        """Handle ping from client"""
        emit('pong', {'timestamp': datetime.utcnow().isoformat()})
        
    return socketio

def broadcast_dashboard_update():
    """Broadcast dashboard data update"""
    if ws_manager:
        data = {
            'type': 'stats_update',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Dashboard data has been updated'
        }
        ws_manager.broadcast_to_room('dashboard', 'dashboard_update', data)

def broadcast_crm_update():
    """Broadcast CRM data update"""
    if ws_manager:
        data = {
            'type': 'crm_update',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'CRM data has been updated'
        }
        ws_manager.broadcast_to_room('crm', 'crm_update', data)

def broadcast_finance_update():
    """Broadcast finance data update"""
    if ws_manager:
        data = {
            'type': 'finance_update',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Finance data has been updated'
        }
        ws_manager.broadcast_to_room('finance', 'finance_update', data)

def broadcast_hr_update():
    """Broadcast HR data update"""
    if ws_manager:
        data = {
            'type': 'hr_update',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'HR data has been updated'
        }
        ws_manager.broadcast_to_room('hr', 'hr_update', data)

def broadcast_inventory_update():
    """Broadcast inventory data update"""
    if ws_manager:
        data = {
            'type': 'inventory_update',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Inventory data has been updated'
        }
        ws_manager.broadcast_to_room('inventory', 'inventory_update', data)

def broadcast_projects_update():
    """Broadcast projects data update"""
    if ws_manager:
        data = {
            'type': 'projects_update',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'Projects data has been updated'
        }
        ws_manager.broadcast_to_room('projects', 'projects_update', data)

def broadcast_notification(message: str, type: str = 'info'):
    """Broadcast a notification to all clients"""
    if ws_manager:
        data = {
            'type': 'notification',
            'message': message,
            'notification_type': type,
            'timestamp': datetime.utcnow().isoformat()
        }
        ws_manager.broadcast_to_all('notification', data)

# Background task for periodic updates
def start_background_tasks():
    """Start background tasks for periodic updates"""
    def periodic_updates():
        while True:
            try:
                # Simulate periodic data updates
                time.sleep(30)  # Update every 30 seconds
                
                if ws_manager and ws_manager.connected_clients:
                    # Broadcast periodic updates to different rooms
                    broadcast_dashboard_update()
                    broadcast_crm_update()
                    broadcast_finance_update()
                    broadcast_hr_update()
                    broadcast_inventory_update()
                    broadcast_projects_update()
                    
            except Exception as e:
                logger.error(f"Error in background task: {e}")
                
    # Start background thread
    thread = threading.Thread(target=periodic_updates, daemon=True)
    thread.start()
    logger.info("Background tasks started")

# Utility functions for broadcasting updates from API endpoints
def notify_customer_created(customer_data):
    """Notify when a new customer is created"""
    broadcast_crm_update()
    broadcast_notification(f"New customer {customer_data.get('name', 'Unknown')} has been added", 'success')

def notify_customer_updated(customer_data):
    """Notify when a customer is updated"""
    broadcast_crm_update()
    broadcast_notification(f"Customer {customer_data.get('name', 'Unknown')} has been updated", 'info')

def notify_customer_deleted(customer_name):
    """Notify when a customer is deleted"""
    broadcast_crm_update()
    broadcast_notification(f"Customer {customer_name} has been deleted", 'warning')

def notify_order_created(order_data):
    """Notify when a new order is created"""
    broadcast_dashboard_update()
    broadcast_notification(f"New order #{order_data.get('order_number', 'Unknown')} has been created", 'success')

def notify_product_updated(product_data):
    """Notify when a product is updated"""
    broadcast_inventory_update()
    broadcast_notification(f"Product {product_data.get('name', 'Unknown')} has been updated", 'info')

def notify_attendance_marked(user_name, action):
    """Notify when attendance is marked"""
    broadcast_hr_update()
    broadcast_notification(f"{user_name} has {action}", 'info')

def notify_project_updated(project_data):
    """Notify when a project is updated"""
    broadcast_projects_update()
    broadcast_notification(f"Project {project_data.get('name', 'Unknown')} has been updated", 'info')
