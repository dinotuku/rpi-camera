#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from base_camera import BaseCamera


class Camera(BaseCamera):
    """An emulated camera implementation that streams a repeated sequence of
    files 1.jpg, 2.jpg, 3.jpg, ... at a rate of one frame per second."""
    imgs = [open('test.jpg', 'rb').read()]
    def __init__(self):
        self.awb_mode = 'off'
        self.exposure_mode = 'off'
        self.image_effect = 'none'
        self.rotation = 180
        self.brightness = 50
        self.contrast = 0
        self.saturation = 0
        self.state = 'close'
        super().__init__()

    @staticmethod
    def frames():
        while True:
            time.sleep(1)
            yield Camera.imgs[int(time.time()) % 1]
