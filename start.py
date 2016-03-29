import cv2
from imutils.object_detection import non_max_suppression
import numpy as np
import configparser
import imutils
import time
from tripline import Tripline
from peoplefinder import PeopleFinder

# load config
config = configparser.ConfigParser()
config.read('settings.ini')

# video source settings
crop_x1 = config.getint('video_source', 'frame_x1')
crop_y1 = config.getint('video_source', 'frame_y1')
crop_x2 = config.getint('video_source', 'frame_x2')
crop_y2 = config.getint('video_source', 'frame_y2')
frame_max_width = config.getint('video_source', 'max_width')
b_and_w = config.getboolean('video_source', 'b_and_w')

# hog settings
hog_win_stride = config.getint('hog', 'win_stride')
hog_padding = config.getint('hog', 'padding')
hog_scale = config.getfloat('hog', 'scale')

# opencv bug
cv2.ocl.setUseOpenCL(False)

# mog settings
mog_enabled = config.getboolean('mog', 'enabled')
if mog_enabled:
    mogbg = cv2.createBackgroundSubtractorMOG2()

# hud
last_time = time.time()
font = cv2.FONT_HERSHEY_SIMPLEX

# frame dimension (calculated below)
frame_width = 0
frame_height = 0

# people tracking
people_options = dict(config.items('person'))
finder = PeopleFinder(people_options=people_options)


# help us crop/resize frames as they come in
def crop_and_resize(frame):
    global frame_height, frame_width

    frame = frame[crop_y1:crop_y2, crop_x1:crop_x2]
    frame = imutils.resize(frame, width=min(frame_max_width, frame.shape[1]))

    frame_height = frame.shape[0]
    frame_width = frame.shape[1]

    return frame


# apply background subtraction if needed
def apply_mog(frame):
    if mog_enabled:
        mask = mogbg.apply(frame)
        frame = cv2.bitwise_and(frame, frame, mask=mask)

    return frame


# all the data that overlays the video
def render_hud(frame):
    global last_time
    this_time = time.time()
    diff = this_time - last_time
    fps = 1 / diff
    message = 'FPS: %d' % fps

    cv2.putText(frame, message, (10, frame_height - 20), font, 0.5, (255, 255, 255), 2)

    last_time = time.time()

    return frame


def handle_the_people(frame):
    (rects, weight) = hog.detectMultiScale(frame, winStride=(hog_win_stride, hog_win_stride),
                                           padding=(hog_padding, hog_padding), scale=hog_scale)

    people = finder.people(rects)

    # draw triplines
    for line in lines:
        for person in people:
            line.handle_collision(person)

        frame = line.draw(frame)

    for person in people:
        frame = person.draw(frame)
        person.colliding = False

    return frame

# STARTS HERE
# connect to camera
source = config.get('video_source', 'source')
camera = cv2.VideoCapture(source)
camera.set(cv2.CAP_PROP_FPS, 10)

# setup lines
lines = []
total_lines = config.getint('triplines', 'total_lines')

for idx in range(total_lines):
    key = 'line%d' % (idx + 1)
    start = eval(config.get('triplines', '%s_start' % key))
    end = eval(config.get('triplines', '%s_end' % key))
    buffer = config.getint('triplines', '%s_buffer' % key, fallback=10)
    direction_1 = config.get('triplines', '%s_direction_1' % key, fallback='Up')
    direction_2 = config.get('triplines', '%s_direction_2' % key, fallback='Down')
    line = Tripline(point_1=start, point_2=end, buffer_size=buffer, direction_1=direction_1, direction_2=direction_2)
    lines.append(line)

# setup detectors
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# feed in video
while camera.isOpened():
    rval, frame = camera.read()

    if frame is not None:

        if b_and_w:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        frame = crop_and_resize(frame)
        frame = apply_mog(frame)
        frame = handle_the_people(frame)

        frame = render_hud(frame)
        cv2.imshow('preview', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
