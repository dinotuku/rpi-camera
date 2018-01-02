import io
import time
import picamera
from base_camera import BaseCamera


class Camera(BaseCamera):
    def __init__(self):
        self.awb_mode = 'auto'
        self.exposure_mode = 'auto'
        self.image_effect = 'none'
        self.brightness = 50
        self.contrast = 0
        self.saturation = 0
        self.rotation = 180
        self.state = 'close'
        super().__init__()

    def frames(self):
        with picamera.PiCamera() as camera:
            # Initial settings
            camera.resolution = (640, 480)
            camera.rotation = self.rotation

            # let camera warm up
            time.sleep(2)

            stream = io.BytesIO()

            for foo in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
                camera.awb_mode = self.awb_mode
                camera.exposure_mode = self.exposure_mode
                camera.image_effect = self.image_effect
                camera.brightness = self.brightness
                camera.contrast = self.contrast
                camera.saturation = self.saturation
                camera.rotation = self.rotation
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()
