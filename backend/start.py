#!/usr/bin/env python3
"""
Startup script for SmartBiz360 Backend API
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

if __name__ == '__main__':
    # Get configuration from environment
    config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create and run the application
    app = create_app(config_name)
    
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))
    
    print(f"Starting SmartBiz360 Backend API on port {port}")
    print(f"Environment: {config_name}")
    print(f"API Base URL: http://localhost:{port}/api/v1")
    print("Press Ctrl+C to stop the server")
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=(config_name == 'development')
        )
    except KeyboardInterrupt:
        print("\nShutting down SmartBiz360 Backend API...")
        sys.exit(0)
