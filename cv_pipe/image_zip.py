import time

import numpy as np
from pipeline.core import *
import cv2
from scipy.sparse import csr_matrix


class ImageZip(Worker):
    def __init__(self, name: str = 'img_zip', is_gray: bool = True,  interval: float = 5, skip: int = 5, th: int = 100):
        super().__init__(name)
        self.mog = None
        self.is_gray = is_gray
        self.keyframe_time = time.time()
        self.interval = interval
        self.delayed = time.time()
        self.skip = skip
        self.skip_count = -1
        self.th = th

    def process(self, frame: Frame):
        if 'img' not in frame.data.keys():
            return frame
        self.skip_count += 1
        self.skip_count = self.skip_count % self.skip
        if self.skip_count % self.skip != 0:
            frame.itinerary.append(None)
            return frame

        if self.mog is None:
            self.mog = cv2.createBackgroundSubtractorMOG2(history=1, varThreshold=5, detectShadows=True)
            self.keyframe_time = time.time() - self.interval

        img = frame.data['img']

        # 如果 is_gray 为真，则对图像灰度化
        if self.is_gray:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        if time.time() - self.keyframe_time < self.interval:
            t_img = cv2.GaussianBlur(img, (3, 3), 1)
            img_mask = self.mog.apply(t_img, learningRate=-1)
            # img_mask = cv2.dilate(img_mask, np.ones((3, 3), np.float32))
            # img_mask = cv2.erode(img_mask, np.ones((7, 7), np.float32))
            # img_mask = cv2.dilate(img_mask, np.ones((3, 3), np.float32))
            img_mask[img_mask < self.th] = 0
            img_mask[img_mask != 0] = img[img_mask != 0]
            img_mask = csr_matrix(img_mask)
            frame.data['img'] = img_mask
            frame.data['is_keyframe'] = False
        else:
            frame.data['is_keyframe'] = True
            frame.data['img'] = img
            self.keyframe_time = time.time()
        return frame


class ImageUnzip(Worker):
    def __init__(self, name):
        super().__init__(name)
        self.keyframe = None

    def process(self, frame: Frame):
        if 'img' not in frame.data.keys():
            return frame

        if frame.data['is_keyframe']:
            self.keyframe = frame.data['img']
            return frame

        if self.keyframe is not None:
            img = frame.data['img'].toarray()
            self.keyframe[img != 0] = img[img != 0]
            frame.data['img'] = self.keyframe
            # frame.data['img'] = img
            return frame
