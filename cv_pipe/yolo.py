import pipeline.core as core
import utils


class Yolov5(core.Worker):
    def __init__(self, name, weight_path: str = None):
        super().__init__(name)
        net = None
        if weight_path is None:
            weight_path = 'aaa.pt'

    def process(self, frame: core.Frame):
        if 'img' not in frame.data.keys():
            return frame

        # 正式开始
        frame.data['detection'] = self.net.detcter(frame.data['img'])
        return frame
