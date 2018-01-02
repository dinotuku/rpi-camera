#!/usr/bin/env python

"""
CEED Raspberry Pi Camera Tutorial
"""

import io
import os
import sys
from flask import Flask, render_template, redirect, request, url_for, Response
from PIL import Image

if sys.argv[1] == 'test':
    from camera import Camera
else:
    from camera_pi import Camera

app = Flask(__name__)
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# app.config['TEMPLATES_AUTO_RELOAD'] = True

camera = Camera()


@app.route('/')
def index():
    """ Video streaming home page. """
    return render_template(
        'index.html',
        brightness=camera.brightness,
        contrast=camera.contrast,
        saturation=camera.saturation,
        awb_mode=camera.awb_mode,
        exposure_mode=camera.exposure_mode,
        image_effect=camera.image_effect,
        state=camera.state
    )


@app.route('/<cmd>')
def _cmd(cmd=None):
    """ Control commands """
    camera.state = 'close'

    if cmd == 'brightness':
        camera.brightness = int(request.args.get('level'))
        camera.state = 'open'
    if cmd == 'contrast':
        camera.contrast = int(request.args.get('level'))
        camera.state = 'open'
    if cmd == 'saturation':
        camera.saturation = int(request.args.get('level'))
        camera.state = 'open'
    elif cmd == 'awb_mode':
        camera.awb_mode = request.args.get('mode')
    elif cmd == 'exposure_mode':
        camera.exposure_mode = request.args.get('mode')
    elif cmd == 'image_effect':
        camera.image_effect = request.args.get('mode')
    elif cmd == 'rotate':
        camera.rotation = (camera.rotation + 90) % 360
    elif cmd == 'shutter':
        frame = camera.get_frame()
        image = Image.open(io.BytesIO(frame))
        counter = len([name for name in os.listdir('images') if os.path.isfile(
            os.path.join('images', name)) and name[:5] == 'image'])
        image.save("images/image_{}.jpg".format(counter), "JPEG")

    return redirect(url_for('index'))


def gen(cam):
    """ Video streaming generator function. """
    while True:
        frame = cam.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """ Video streaming route. Put this in the src attribute of an img tag. """
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=False, threaded=True)
