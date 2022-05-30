import pipeline.core as core
import pipeline.utils as utils
from sensor.sensors import *


class MySave(utils.Save):
    def process(self, frame: Frame):
        if len(frame.data) == 0:
            return frame
        else:
            return super().process(frame)


all_cameras = [
    core.Node('classroom', subsequents=['save'], worker=get_web_camera_input('classroom'), source='classroom'),
    core.Node('living_room', subsequents=['save'], worker=get_web_camera_input('living_room'), source='living_room'),
    core.Node('bed_room', subsequents=['save'], worker=get_web_camera_input('bed_room'), source='bed_room'),
    core.Node('save', worker=utils.Save())
]

