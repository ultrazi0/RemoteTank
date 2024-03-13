import time

from camera.cameraClass import *
from multiprocessing import Process

if __name__ == "__main__":
    cam = Camera()

    capture = Process(target=cam.capture)
    show = Process(target=cam.show)

    try:
        capture.start()
        show.start()

        capture.join()
        show.join()
    finally:
        cam.image_memory.unlink()
        print("THE END")
