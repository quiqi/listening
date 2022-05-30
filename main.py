import task.task1
import pipeline


if __name__ == '__main__':
    pipeline.mul.MulIgnition(task.task1.all_cameras).run()
    # task = pipeline.core.Node(name='load', worker=pipeline.utils.Load())
    # while True:
    #     a = task.run(pipeline.core.Frame())