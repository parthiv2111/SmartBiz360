"""
WSGI entry point for the SmartBiz360 application
This file is used by Flask-Migrate and other tools that need access to the Flask app
"""

from app import app

if __name__ == '__main__':
    app.run(debug=True)
