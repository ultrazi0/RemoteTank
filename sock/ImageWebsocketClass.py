import json
import cv2 as cv

from time import sleep
from base64 import b64encode
from sock.socketClass import Websocket
from camera.cameraClass import Camera


class ImageWebsocket(Websocket):
    def __init__(self, uri: str, cam: Camera, delay: float = 0.1):
        super().__init__(uri)
        self.camera = cam
        self.delay = delay

    @Websocket._connect_and_run
    def read_from_memory_and_send(self) -> None:
        """ Reads image from SharedMemory and sends it to the websocket as a json string """
        try:
            while 1:
                image = self.camera.read_image_from_shared_memory(delay=0)[0]

                json_image = self.convert_image_to_json(image)

                if self.websocket is not None:
                    self.websocket.send(json_image)
                    # print("ImageWebsocket>>> Sent")
                else:
                    # Should actually never happen
                    print("ImageWebsocket>>> Cannot send image, because websocket is not initialized")

                if self.camera.closed.is_set() or self.closed.is_set():
                    raise KeyboardInterrupt

                sleep(self.delay)
        except KeyboardInterrupt:
            pass
        finally:
            self.camera.closed.set()
            self.closed.set()

            print("ImageWebsocket>>> Closing...")

    def read_from_memory_and_send_windows(self) -> None:
        """ Workaround for Windows """
        self.read_from_memory_and_send()

    @staticmethod
    def convert_image_to_json(img) -> str:
        """ Converts image (numpy.ndarray) to json string """
        success, imdata = cv.imencode('.JPG', img)

        return json.dumps({"messageType": "image", "image": b64encode(imdata.tobytes()).decode('ascii')})
