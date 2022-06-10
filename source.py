from pipeline.core import *
from pipeline.utils import *
from pipeline.mul import *
import cv_pipe
import sensor.sensors as sensors
import socket


if __name__ == '__main__':
    ip = socket.gethostbyname(socket.gethostname())
    print(ip)
    task = [
        NodeSet([
            Node('head_classroom', subsequents=['camera']),
            Node('camera', subsequents=['img_zip'], worker=sensors.get_web_camera_input('classroom')),
            Node('img_zip', subsequents=['push'], worker=cv_pipe.image_zip.ImageZip()),
            Node('push', worker=TCPServer(ip, port=8088))
        ], source='head_classroom')
    ]
    print('ip{}, port:{}'.format(ip, 8088))
    MulIgnition(task).run()
