#!/usr/bin/env python3
"""
🚀 Servidor simple para la GUI web del Decision Maker
Ejecuta: python3 server.py
Luego abre: http://localhost:8000
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

PORT = 8000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler personalizado para servir la aplicación web"""
    
    def end_headers(self):
        # Añadir headers CORS para desarrollo local
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def log_message(self, format, *args):
        """Log personalizado con emojis"""
        print(f"🌐 {self.address_string()} - {format % args}")

def main():
    # Cambiar al directorio de la GUI web
    web_dir = Path(__file__).parent
    os.chdir(web_dir)
    
    print("🎲 Decision Maker - GUI Web")
    print("=" * 40)
    print(f"📁 Sirviendo desde: {web_dir}")
    print(f"🌐 Puerto: {PORT}")
    print("=" * 40)
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"✅ Servidor iniciado en http://localhost:{PORT}")
            print("🚀 Abriendo navegador...")
            
            # Abrir automáticamente el navegador
            webbrowser.open(f'http://localhost:{PORT}')
            
            print("\n💡 Instrucciones:")
            print("   • El navegador se abrirá automáticamente")
            print("   • Si no se abre, visita: http://localhost:8000")
            print("   • Presiona Ctrl+C para detener el servidor")
            print("\n🎯 ¡Listo para tomar decisiones con Monte Carlo!")
            print("-" * 50)
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido. ¡Gracias por usar Decision Maker!")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"\n❌ Error: Puerto {PORT} ya está en uso.")
            print("💡 Soluciones:")
            print(f"   • Usa otro puerto: python3 server.py {PORT + 1}")
            print("   • O detén el proceso que usa el puerto")
        else:
            print(f"\n❌ Error iniciando servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()