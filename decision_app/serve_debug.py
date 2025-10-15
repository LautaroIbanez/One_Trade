#!/usr/bin/env python3
"""
Servidor HTTP para página de debug
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path

def serve_debug():
    PORT = 3000
    DIRECTORY = Path(__file__).parent
    
    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(DIRECTORY), **kwargs)
        
        def end_headers(self):
            # Añadir headers CORS
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def do_GET(self):
            # Si la ruta es /, servir debug.html
            if self.path == '/' or self.path == '':
                self.path = '/debug.html'
            super().do_GET()
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print("="*60)
            print("🔍 Debug Server - One Trade Decision App")
            print("="*60)
            print()
            print(f"📡 Serving on: http://localhost:{PORT}")
            print(f"📁 File: debug.html")
            print()
            print("🔗 URLs:")
            print(f"   Debug Page: http://localhost:{PORT}")
            print(f"   Backend: http://localhost:8000")
            print()
            print("⚡ Press Ctrl+C to stop the server")
            print("="*60)
            print()
            
            # Abrir navegador automáticamente
            webbrowser.open(f'http://localhost:{PORT}')
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n👋 Debug server stopped. Goodbye!")
        exit(0)
    except OSError as e:
        if e.errno == 10048:  # Puerto en uso
            print(f"❌ Port {PORT} is already in use.")
            print("Try a different port or stop the process using this port.")
        else:
            print(f"❌ Error starting server: {e}")
        exit(1)

if __name__ == "__main__":
    serve_debug()

