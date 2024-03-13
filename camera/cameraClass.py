import cv2 as cv
import numpy as np

from os import getpid
from time import sleep
from multiprocessing import Event
from multiprocessing.shared_memory import SharedMemory


class Camera:
    def __init__(self, width: int = 640, height: int = 480, camera_id: int = 0):
        self.width = width
        self.height = height
        self.camera_id = camera_id

        self.cap = None
        self.window_name = f"Camera {self.camera_id}"
        self.image_channels = 3

        self.image_memory_name = "ImageMemory" + str(self.camera_id)
        self.image_memory = SharedMemory(name=self.image_memory_name, create=True,
                                         size=self.width*self.height*self.image_channels)
        self.closed = Event()

    def capture_and_show(self):
        self.cap = cv.VideoCapture(self.camera_id, cv.CAP_DSHOW)
        self.cap.set(3, self.width)
        self.cap.set(4, self.height)

        try:
            while 1:
                success, img = self.cap.read()
                if not success:
                    print("Camera>>> Failed to get a frame... jammer!")
                    break

                cv.imshow(self.window_name, img)
                k = cv.waitKey(1)

                if k % 256 == ord("q"):
                    # Q was pressed, quitting
                    raise KeyboardInterrupt
        except KeyboardInterrupt:
            print("Closing...")
        finally:
            cv.destroyWindow(self.window_name)

    def read_image_from_shared_memory(self, n=1, delay=1) -> np.ndarray:
        """ Reads n images from shared memory created for this camera with specified delay between them """

        # Create an empty array for future images
        images = np.empty((n, self.height, self.width, self.image_channels), dtype=np.uint8)

        for i in range(n):
            # Read the image from memory
            img = np.ndarray(shape=(self.height, self.width, self.image_channels),
                             buffer=self.image_memory.buf, dtype=np.uint8)

            # Write it into the array
            images[i] = img

            # Wait for a new image/frame to come up
            sleep(delay)

        return images

    def capture(self):
        """ Open capture on the camera. Designed to be run as a process """
        print(f"Camera>>> Capture on Camera {self.camera_id}: Running in process {getpid()}", flush=True)

        # Initialize capture object
        self.cap = cv.VideoCapture(self.camera_id, cv.CAP_DSHOW)
        self.cap.set(3, self.width)
        self.cap.set(4, self.height)

        try:
            while not self.closed.is_set():
                # Read the image
                success, img = self.cap.read()
                if not success:
                    print('Camera>>> Failed to get a frame...')
                    break

                # Create an array with the same properties as the image
                array = np.ndarray(img.shape, dtype=img.dtype, buffer=self.image_memory.buf)

                # Copy the image into the array
                array[:] = img[:]

                cv.waitKey(1)
        except KeyboardInterrupt:
            print('Camera>>> Capture: Closing', flush=True)
        finally:
            self.image_memory.close()
            self.cap.release()
            print('Camera>>> Sender: Done', flush=True)

    def show(self):
        """ Open show window to read from SharedMemory. Designed to be run as a process """
        print(f'Camera>>> Showing Camera {self.camera_id}: Running in process {getpid()}', flush=True)

        try:
            while 1:
                # Read image
                img = np.ndarray(shape=(self.height, self.width, self.image_channels),
                                 buffer=self.image_memory.buf, dtype=np.uint8)

                # Show image
                cv.imshow(self.window_name, img)
                k = cv.waitKey(1)

                if k % 256 == ord('q'):
                    raise KeyboardInterrupt
                if k % 256 == ord(' '):
                    print(img.size)

                if self.closed.is_set():
                    print('Camera>>> Receiver: Heard that must be closed...', flush=True)
                    break
        except KeyboardInterrupt:
            print('Camera>>> Receiver: Closing...', flush=True)
        finally:
            self.closed.set()

            self.image_memory.close()

            cv.destroyWindow(self.window_name)
            print('Camera>>> Receiver: Done', flush=True)
