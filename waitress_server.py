# waitress_server.py
from waitress import serve
from PyMonitor.wsgi import application
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Waitress production server on http://localhost:{port}")
    
    # Absolute minimum parameters - these are guaranteed to work
    serve(application, host='0.0.0.0', port=port)