import cv2

import ig_task.task1
import pipeline
import flask


if __name__ == '__main__':
    a = ig_task.task1.get_img_push()
    # while True:
    #     a.run(pipeline.core.Frame(end='classroom'))
    pipeline.mul.MulIgnition(a).run()
