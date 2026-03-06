#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Server Wrapper for Android
This module wraps the original WEB-VIM Flask application for running inside Android
using Chaquopy Python runtime.
"""

import os
import sys
import threading
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global server instance
_server_instance: Optional['FlaskServer'] = None
_server_lock = threading.Lock()


class FlaskServer:
    """Wrapper class for Flask server to run in Android environment"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.thread: Optional[threading.Thread] = None
        self.app = None
        self.running = False
        self._setup_environment()
        
    def _setup_environment(self):
        """Setup the environment for Flask app"""
        # Get the Python files directory in Android
        python_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Add server directory to path
        server_dir = os.path.join(python_dir, 'server')
        if server_dir not in sys.path:
            sys.path.insert(0, server_dir)
            
        # Set environment variables
        os.environ['FLASK_ENV'] = 'production'
        os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
        
        logger.info(f"Environment setup complete. Server dir: {server_dir}")
        
    def _create_app(self):
        """Create and configure Flask application"""
        try:
            # Import the original Flask app
            from app import app as flask_app
            
            # Configure for Android environment
            flask_app.config['DEBUG'] = False
            flask_app.config['TESTING'] = False
            flask_app.config['SECRET_KEY'] = 'android-secret-key-2024'
            
            logger.info("Flask app created successfully")
            return flask_app
            
        except Exception as e:
            logger.error(f"Failed to create Flask app: {e}")
            raise
            
    def _run_server(self):
        """Run the Flask server in a thread"""
        try:
            self.app = self._create_app()
            self.running = True
            
            logger.info(f"Starting Flask server on port {self.port}")
            
            # Use threaded=True for handling multiple requests
            self.app.run(
                host='127.0.0.1',
                port=self.port,
                debug=False,
                threaded=True,
                use_reloader=False  # Important: disable reloader for embedded use
            )
            
        except Exception as e:
            logger.error(f"Server error: {e}")
            self.running = False
            
    def start(self):
        """Start the Flask server in a background thread"""
        if self.running:
            logger.warning("Server is already running")
            return
            
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        logger.info("Server thread started")
        
    def stop(self):
        """Stop the Flask server"""
        self.running = False
        logger.info("Server stop requested")
        
    def is_running(self) -> bool:
        """Check if server is running"""
        return self.running and self.thread is not None and self.thread.is_alive()


def start_server(port: int = 8080) -> FlaskServer:
    """
    Start the Flask server (called from Android/Kotlin)
    
    Args:
        port: Port number to run the server on
        
    Returns:
        FlaskServer instance
    """
    global _server_instance
    
    with _server_lock:
        if _server_instance is None or not _server_instance.is_running():
            _server_instance = FlaskServer(port)
            _server_instance.start()
            
    return _server_instance


def stop_server():
    """Stop the running Flask server"""
    global _server_instance
    
    with _server_lock:
        if _server_instance is not None:
            _server_instance.stop()
            _server_instance = None
            

def get_server_status() -> dict:
    """Get current server status"""
    global _server_instance
    
    return {
        'running': _server_instance.is_running() if _server_instance else False,
        'port': _server_instance.port if _server_instance else None
    }


# For direct testing
if __name__ == '__main__':
    server = start_server(8080)
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        stop_server()
