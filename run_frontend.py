#!/usr/bin/env python3
"""
Simple local server for RentAware frontend
This solves CORS issues when opening index.html directly from file://
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8080
FRONTEND_DIR = Path(__file__).parent / "frontend"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def start_server():
    os.chdir(FRONTEND_DIR)
    
    print("╔════════════════════════════════════════════════════════╗")
    print("║          RentAware Frontend Server                     ║")
    print("╚════════════════════════════════════════════════════════╝")
    print(f"\n📁 Serving from: {FRONTEND_DIR}")
    print(f"🌐 Open in browser: http://127.0.0.1:{PORT}")
    print(f"\n✅ Server is running. Press Ctrl+C to stop.\n")
    
    # Open browser automatically
    webbrowser.open(f"http://127.0.0.1:{PORT}")
    
    handler = MyHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n❌ Server stopped.")
            exit(0)

if __name__ == "__main__":
    start_server()
