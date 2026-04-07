#!/usr/bin/env python
"""Production WSGI entry point for the Flask application"""
import os
from src.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv('PORT', 3001))
    app.run(host='0.0.0.0', port=port, debug=False)
