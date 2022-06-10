import pipeline.core as core
import cv2


class ShowImage(core.Worker):
    def __init__(self, name: str = 'show_img'):
        super().__init__(name)

    def process(self, frame: core.Frame):
        if 'img' not in frame.data.keys():
            return frame
        cv2.imshow(self.name, frame.data['img'])
        cv2.waitKey(1)
        return frame
