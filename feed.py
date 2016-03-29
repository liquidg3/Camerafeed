import sys
import os
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from threading import Timer


# serve out of html
os.chdir('./html')

camera = None

# # start taking photos
if len(sys.argv) > 1 and sys.argv[1] == 'mac':
    def take_photo():
        global camera

        if camera is None:
            pass

        return cv2.VideoCapture()
else:
    def take_photo():
        import picamera
        global camera

        if camera is None:
            # setup camera (getting screen from footfall)
            camera = picamera.PiCamera()

        camera.resolution = (640, 480)

        return camera.capture('image/image.png')


def save_screen():
    img = take_photo()
    print('saving screen');
    Timer(5.0, save_screen).start()


save_screen()

# setup server
HandlerClass = SimpleHTTPRequestHandler
ServerClass = BaseHTTPServer.HTTPServer
Protocol = "HTTP/1.0"

port = 8080
server_address = ('0.0.0.0', port)

HandlerClass.protocol_version = Protocol
httpd = ServerClass(server_address, HandlerClass)

sa = httpd.socket.getsockname()
print "Serving HTTP on", sa[0], "port", sa[1], "..."
httpd.serve_forever()
