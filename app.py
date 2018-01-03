#!/usr/bin/env python

"""
CEED Raspberry Pi Camera Tutorial
"""

from datetime import datetime
import io
import os
import sys
from flask import Flask, render_template, redirect, request, url_for, Response
from PIL import Image

if len(sys.argv) != 2:
    print('Wrong usage! It should be --> python app.py <Type(test or pi)>')
    sys.exit()
elif sys.argv[1] == 'test':
    from camera import Camera
elif sys.argv[1] == 'pi':
    from camera_pi import Camera
else:
    print('Wrong usage! Type should be test or pi')
    sys.exit()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

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
        os.remove(os.path.join('static/pic', files[idx]))

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
