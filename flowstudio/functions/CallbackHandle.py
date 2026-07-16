import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from functools import partial
import socket
import errno

from PyQt5.QtCore import QThread, pyqtSignal


class CallbackHandler(BaseHTTPRequestHandler):
    html_content = """
                       <!DOCTYPE html>
                       <html>
                       <head>
                           <title>Login To Flow DSP</title>
                           <style>
                               body {
                                   font-family: Arial, sans-serif;
                                   background: #f0f2f5;
                                   display: flex;
                                   justify-content: center;
                                   align-items: center;
                                   height: 100vh;
                                   margin: 0;
                               }
                               .success-box {
                                   padding: 2rem;
                                   font-size: 1.5rem;
                                   text-align: center;
                               }
                               h1 {
                                   color: #4CAF50;
                                   margin: 0 0 1rem 0;
                               }
                               p {
                                   color: #666;
                               }
                           </style>
                       </head>
                       <body>
                           <div class="success-box">
                               <p>Login successful, please return to Flow Studio</p>
                           </div>
                       </body>
                       </html>
                       """.encode('utf-8')

    def __init__(self, *args, parent=None, **kwargs):
        self.parent = parent
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        if parsed_url.path == "/callback":
            token = query_params.get("token", [None])[0]
            if token:
                print(f"[Successful] Received Token: {token}")
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(self.html_content)))
                self.end_headers()
                self.wfile.write(self.html_content)
                print("-----------------")
                self.parent.shutdown_server.emit()
                self.parent.callback_token.emit(token)
                # if self.server_type == '' :
                #     self.parent.UserSignInSuccess(token)
                # else:
                #     self.parent.check_user_metadata(token)
            else:
                self.send_response(400)
                self.end_headers()

class LocalServer(QThread):
    callback_token = pyqtSignal(str)
    callback_port = pyqtSignal(str)
    shutdown_server = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.server = None
        self.port = None
        self.parent = parent
        self.shutdown_server.connect(self.stop_local_server)

    def run(self):
        self.port = 32350
        max_attempts = 10

        for j in range(max_attempts):
            try:
                res = self.is_local_port_available(self.port)
                if not res:
                    print(f"try {self.port + 1}...")
                    self.port += 1
                    continue

                handler = partial(CallbackHandler, parent=self)
                self.server = HTTPServer(('localhost', self.port), handler)
                print(f"[Listening] Service has started: http://localhost:{self.port}")
                self.callback_port.emit(str(self.port))
                self.server.serve_forever()
                break
            except OSError as e:
                print(f"{e}，try {self.port + 1}...")
                self.port += 1
        else:
            print(f"[Error] Unable to find available port between 32350-32360")
            raise RuntimeError("Unable to find available ports between 32350-32360")

    def stop_local_server(self):
        print(f"[Stopping] Stopping local server... {self.server}")
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

    def get_port(self):
        return self.port

    def is_local_port_available(self, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
            return True
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                print(f"Port {port} is already occupied.")
            elif e.errno == errno.EACCES:
                print(f"Port {port} requires administrator privileges.")
            else:
                print(f"unknown error: {e}")
            return False

# Start the server
# local_server = LocalServer()
# threading.Thread(target=local_server.run_local_server).start()
