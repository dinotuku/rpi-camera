#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Raspberry Pi Camera Tutorial
"""

from argparse import ArgumentParser
from datetime import datetime
import io
import math
import os

from flask import Flask, render_template, redirect, request, url_for, Response
import numpy as np
from PIL import Image

# Simple argument parser
parser = ArgumentParser()
parser.add_argument('-t', '--test', action='store_true', help='Run this app without using rpi camera')
args = parser.parse_args()

if args.test:
    from camera import Camera
else:
    from camera_pi import Camera

# Setup Flask
app = Flask(__name__)

# Debug settings
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# app.config['TEMPLATES_AUTO_RELOAD'] = True

# Setup camera
camera = Camera()

if not os.path.exists('static/pic'):
    os.makedirs('static/pic')


@app.route('/')
def index():
    """ Home page """
    recent_file_name = ''
    files = [name for name in os.listdir('static/pic') if os.path.isfile(
        os.path.join('static/pic', name)) and name[:5] == 'image']
    files.sort()
    if files:
        recent_file_name = files[-1]
    return render_template(
        'index.html',
        brightness=camera.brightness,
        contrast=camera.contrast,
        saturation=camera.saturation,
        awb_mode=camera.awb_mode,
        exposure_mode=camera.exposure_mode,
        image_effect=camera.image_effect,
        state=camera.state,
        recent_file_name=recent_file_name
    )


@app.route('/gallery')
def gallery():
    """ Gallery page """
    files = [name for name in os.listdir('static/pic') if os.path.isfile(
        os.path.join('static/pic', name)) and name[:5] == 'image']
    files.sort()
    files_names = ','.join(files)
    return render_template(
        'gallery.html',
        files_names=files_names
    )


@app.route('/<cmd>')
def _cmd(cmd=None):
    """ Control commands """
    camera.state = 'close'

    if cmd == 'brightness':
        new_brightness = int(request.args.get('level'))
        camera.state = 'open'

        camera.brightness = new_brightness
    if cmd == 'contrast':
        new_contrast = int(request.args.get('level'))
        camera.state = 'open'

        camera.contrast = new_contrast
    if cmd == 'saturation':
        new_saturation = int(request.args.get('level'))
        camera.state = 'open'

        camera.saturation = new_saturation
    elif cmd == 'awb_mode':
        new_awb_mode = request.args.get('mode')

        camera.awb_mode = new_awb_mode
    elif cmd == 'exposure_mode':
        new_exposure_mode = request.args.get('mode')

        camera.exposure_mode = new_exposure_mode
    elif cmd == 'image_effect':
        new_image_effect = request.args.get('mode')

        camera.image_effect = new_image_effect
    elif cmd == 'homework':
        frame = camera.get_frame()
        im = Image.open(io.BytesIO(frame))

        column, row = im.size
        im_grey = im.convert('L')
        im_array = np.array(im_grey)
        im_db = im_array / 255.

        im_r1 = np.zeros((row, column))
        for i in range(0, row - 1):
            for j in range(0, column - 1):
                im_r1[i, j] = -1 * im_db[i, j] + 0 + 0 + 1 * im_db[i + 1, j + 1]
                im_r1[i, j] = im_r1[i, j] * im_r1[i, j]

        im_r2 = np.zeros((row, column))
        for i in range(0, row - 1):
            for j in range(0, column - 1):
                im_r2[i, j] = 0 - 1 * im_db[i, j + 1] + 1 * im_db[i + 1, j] + 0
                im_r2[i, j] = im_r2[i, j] * im_r2[i, j]

        gradient = np.zeros((row, column))
        for i in range(0, row - 1):
            for j in range(0, column - 1):
                gradient[i, j] = math.sqrt(im_r1[i, j] + im_r2[i, j])

        threshold = 0.06
        im_robert = np.zeros((row, column), dtype='uint8')
        for i in range(0, row):
            for j in range(0, column):
                if (gradient[i, j] >= threshold):
                    im_robert[i, j] = 0
                else:
                    im_robert[i, j] = 255

        image = Image.fromarray(im_robert)

        counter = 0
        files = [name for name in os.listdir('static/pic') if os.path.isfile(
            os.path.join('static/pic', name)) and name[:5] == 'image']
        files.sort()

        if files:
            counter = int(files[-1].split('_')[1]) + 1

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        image.save("static/pic/image_{}_{}.jpg".format(counter, timestamp), "JPEG")
    elif cmd == 'shutter':
        frame = camera.get_frame()
        image = Image.open(io.BytesIO(frame))
        counter = 0
        files = [name for name in os.listdir('static/pic') if os.path.isfile(
            os.path.join('static/pic', name)) and name[:5] == 'image']
        files.sort()

        if files:
            counter = int(files[-1].split('_')[1]) + 1

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        image.save("static/pic/image_{}_{}.jpg".format(counter, timestamp), "JPEG")
    elif cmd == 'remove':
        idx = int(request.args.get('index'))
        files = [name for name in os.listdir('static/pic') if os.path.isfile(
            os.path.join('static/pic', name)) and name[:5] == 'image']
        files.sort()
        os.remove(os.path.join('static/pic', list(reversed(files))[idx]))

        return redirect(url_for('gallery'))

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
