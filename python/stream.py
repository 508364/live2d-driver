import cv2
import threading
import socketserver
from http.server import BaseHTTPRequestHandler
from io import BytesIO

class StreamingHandler(BaseHTTPRequestHandler):
    def __init__(self, streamer, *args, **kwargs):
        self.streamer = streamer
        super().__init__(*args, **kwargs)
        
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
        self.end_headers()
        
        while True:
            frame = self.streamer.get_frame()
            if frame is None:
                break
                
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                break
                
            self.wfile.write(b'--frame\r\n')
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Content-Length', len(jpeg))
            self.end_headers()
            self.wfile.write(jpeg.tobytes())
            self.wfile.write(b'\r\n')

class VideoStreamServer:
    def __init__(self, port=9000):
        self.port = port
        self.server = None
        self.latest_frame = None
        self.lock = threading.Lock()
        self.thread = None
        self.running = False
        
    def start(self):
        if self.running:
            return
            
        self.running = True
        handler = lambda *args: StreamingHandler(self, *args)
        self.server = socketserver.ThreadingTCPServer(('0.0.0.0', self.port), handler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        print(f"Streaming server started at http://localhost:{self.port}")
        
    def stop(self):
        if self.running:
            self.running = False
            self.server.shutdown()
            self.server.server_close()
            if self.thread:
                self.thread.join(timeout=1.0)
                
    def push_frame(self, frame):
        with self.lock:
            self.latest_frame = frame.copy()
            
    def get_frame(self):
        with self.lock:
            return self.latest_frame