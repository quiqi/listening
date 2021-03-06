# 这是一个连接工具包
import time
import serial
import cv2
import numpy as np
import platform
from bleak import BleakClient

from pipeline.core import Worker, Frame


class ConnectWorker(Worker):
    """
    连接类
    """
    def __init__(self, name):
        super().__init__(name)
        self.state = False    # 状态分为监听状态 “Listening”（False） 和读取状态 “r、Reading”（True）

    def listening(self):
        """
        监听状态
        :return: 监听结果，如果监听到对应传感器的信号并成功连接则返回真，否则返回假
        """
        return False

    def reading(self, frame: Frame):
        return Frame

    def process(self, frame: Frame):
        if self.state:      # 如果为读取状态
            try:
                frame = self.reading(frame)
            except Exception as e:      # 如果在读取中出错
                print(e)                # 打印出错信息
        else:               # 如果为监听状态
            try:
                c = self.listening()        # 进行监听
                if c is True:
                    self.state = True       # 如果连接成功则设置 self.state 为真
            except Exception as e:
                print(e)                # 打印出错信息
        return frame


class PortConnect(ConnectWorker):
    """
    串口连接工具
    """
    def __init__(self, name, port: str = 'com11', baud_rate: int = 115200, timeout: float = 1, read_size: int = 33,
                 interval: float = 1):
        super().__init__(name)
        self.ser = None
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.off_line = 0
        self.read_size = read_size
        self.interval = interval
        self.last_time = time.time() + self.interval    # 第一次连接时默认不等待时间间隔

    def listening(self):
        try:
            if time.time() - self.last_time < self.interval:    # 每 self.interval 秒连接一次
                return False
            else:
                self.last_time = time.time()    # 重置链接时间
                self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)   # 尝试连接
                print('串口：{}连接成功!'.format(self.port))   # 连接成功
                self.off_line = 0   # 将self.off_line置为零
                return True
        except serial.SerialException as e:
            print(e)
            print('{}模块没有监听到 串口：{} 的数据，请检测设备开关是否打开，将在{}s后继续监听'.format(self.name, self.port, self.interval))
            self.ser = None
            return False

    def reading(self, frame: Frame):
        try:
            data = self.ser.read(self.read_size)    # 常数从串口读取数据
            if len(data) < self.read_size:          # 如果读取到的数据长度小于设定长度
                self.off_line += 1                  # 认为设备离线
                print('设备第{}次离线'.format(self.off_line))
                if self.off_line >= 3:               # 如果设备连续离线三次，则关闭设备重新连接
                    print('设备离线三次，正在关闭连接并尝试重新连接...')
                    self.ser.close()                # 关闭连接
                    self.state = False              # 设置为连接模式
            frame.data[self.port] = data            # 否则写入数据，数据名为串口号
        except Exception as e:      # 差错处理
            print(e)

        return frame


class WebCamera(ConnectWorker):
    def __init__(self, name, url: str, interval: float = 1, scaling: float = 0.25, dip: int = 360, fps: int = 1):
        super().__init__(name)
        self.url = url
        self.camera = None
        self.interval = interval
        self.last_time = time.time() + self.interval
        self.scaling = scaling
        self.off_line = 0
        self.dip = dip
        self.fps = fps

    def listening(self):
        try:        # 尝试连接摄像头
            if time.time() - self.last_time < self.interval:    # 每 self.interval 秒连接一次
                return False
            print('正在尝试连接摄像头...')
            self.camera = cv2.VideoCapture(self.url)
            if not self.camera.isOpened():
                self.camera.release()
                print('模块{}：摄像头{}连接失败，将在{}s后重新连接'.format(self.name, self.url, self.interval))
                return False    # 如果该摄像头没打开，表示连接失败
            else:
                print('摄像头连接成功!')
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.dip)
                self.camera.set(cv2.CAP_PROP_FPS, self.fps)
                return True     # 否则连接成功
        except Exception as e:  # 异常处理
            print(e)            # 打印异常信息
            return False        # 返回连接失败

    def reading(self, frame: Frame):
        try:
            ret, img = self.camera.read()
            if ret:
                img = cv2.resize(img, (0, 0), fx=self.scaling, fy=self.scaling, interpolation=cv2.INTER_AREA)
                frame.data['img'] = img
            else:
                self.off_line += 1
                print('模块{}：摄像头{}第{}次读取失败'.format(self.name, self.url, self.off_line))
                if self.off_line > 10:
                    print('设备离线三次，正在关闭连接并尝试重新连接...')
                    self.camera.release()   # 关闭连接
                    self.state = False      # 设置为连接模式
        except Exception as e:
            print(e)

        return frame


class BLEConnect(ConnectWorker):
    def __init__(self, name: str = 'ble_connect', uddi: str = "00002a37-0000-1000-8000-00805f9b34fb", addr: str = "8C:CE:4E:A5:C2:E6"):
        super().__init__(name)
        self.uddi = uddi
        self.addr = addr

    def listening(self):
        try:
            pass
        except Exception as e:
            print(e)
            return False



if __name__ == '__main__':
    from pipeline.core import Node, NodeSet
    from pipeline.utils import Source, PrintData, Save
    from pipeline.mul import MulIgnition
    from sensor.sensors import get_web_camera_input
    wc1 = Node('dot1', worker=get_web_camera_input('bed_room'), source='dot1')    # 卧室
    wc2 = Node('dot2', worker=WebCamera('web_camera2', 'rtsp://admin:a1234567@192.168.111.8:554/stream1'), source='dot2')    # 客厅
    wc3 = Node('dot3', worker=WebCamera('web_camera3', 'rtsp://admin:a1234567@192.168.111.6:554/stream1'), source='dot3')    # 教室
    MulIgnition([wc1, wc2, wc3]).run()

    # ig_task = NodeSet(dots=[
    #     Node('head', subsequents=['bwt901cl_listener'], worker=Source()),
    #     Node(worker=PortListener('bwt901cl_listener', port='com11'), subsequents=['bwt', 'save'], send_mod='copy'),
    #     Node(worker=BWT901CL('bwt'), subsequents=['print']),
    #     # Node(worker=PrintData('print', ['bwt901cl_listener_data'])),
    #     # Node(worker=Save('save'))
    # ])
    #
    # for i in range(100):
    #     frame = Frame(end='head')
    #     ig_task.run(frame)
