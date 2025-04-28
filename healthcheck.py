import http.server
import socketserver
import threading
import os

PORT = int(os.environ.get("PORT", 8080))

class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/healthcheck':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')

def run_health_server():
    with socketserver.TCPServer(("", PORT), HealthCheckHandler) as httpd:
        print(f"Health check server running at port {PORT}")
        httpd.serve_forever()

# Add this to your bot.py file
def start_health_check_server():
    thread = threading.Thread(target=run_health_server, daemon=True)
    thread.start()

# Then call this function before your bot starts
# In the main() function of bot.py, add: start_health_check_server()
