import cv2
import time
import math


class Person:
    _current_rect = None  # where we are in the frame
    _x1 = 0  # caching
    _y1 = 0
    _x2 = 0
    _y2 = 0
    life = 0  # hom much life we have left
    _full_life = 0
    _time = None  # last time touched
    _center = None
    _max_distance = 10  # how far will i go to consider someone a candidate
    name = None
    _color = None
    _colliding_color = None
    _charge = 0  # how many frames of detection before i'm considered "detected"
    colliding = False
    meta = None  # lets others store meta data for us
    labels = None  # special labels others may want to drop in

    def __init__(self, rect=None, life=10, death_delay=5, max_distance=10, name='Person Dude', color=(0, 255, 0),
                 colliding_color=(255, 0, 0), charge=5):

        self.meta = {}
        self.labels = {}
        self._max_distance = float(max_distance)
        self.name = name
        self.life = int(life)
        self._full_life = int(life)
        self._color = color
        self._colliding_color = colliding_color
        self._death_delay = float(death_delay)
        self._time = time.time()
        self._full_charge = int(charge)
        self._charge = 0


        if rect is not None:
            self.set_rect(rect)

    def match(self, rect):

        x1 = rect[0]
        y1 = rect[1]
        x2 = x1 + rect[2]
        y2 = y1 + rect[3]

        x_center = x1 + (x2 - x1) / 2
        y_center = y1 + (y2 - y1) / 2

        distance = math.hypot(x_center - self._center[0], y_center - self._center[1])

        if distance > self._max_distance:
            return 0

        match = 1 - (distance / self._max_distance)

        return max(0, min(match, 100))

    def set_rect(self, rect):
        self._current_rect = rect
        x1 = rect[0]
        y1 = rect[1]
        x2 = x1 + rect[2]
        y2 = y1 + rect[3]

        x_center = x1 + (x2 - x1) / 2
        y_center = y1 + (y2 - y1) / 2

        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2

        self._center = (int(x_center), int(y_center))

        self.touch()

    def draw(self, frame):

        #we are not fully charged yet, don't show
        if self._charge < self._full_charge:
            return frame

        # square
        alpha = (self.life / self._full_life)

        c = self._colliding_color if self.colliding else self._color
        color = (c[2], c[1], c[0], alpha)
        cv2.rectangle(frame, (self._x1, self._y1), (self._x2, self._y2), color, 1)

        # center dot
        cv2.circle(frame, self._center, 2, color, thickness=8)

        # labels
        font = cv2.FONT_HERSHEY_PLAIN
        label_x = self._x1 + 5
        label_y = self._y2 - 5
        label_y_increment = -12

        cv2.putText(frame, self.name, (label_x, label_y), font, 0.8, color)

        # draw extra labels
        for k in self.labels:
            label = self.labels[k]
            label_y += label_y_increment
            cv2.putText(frame, label, (label_x, label_y), font, 0.6, color)

        return frame

    def touch(self):
        self.life = self._full_life  # we like being touched
        self._time = time.time()
        self._charge += 1

    def tick(self):
        self.life -= 1  # we die with each tick
        if self.life > 0:
            self._how_dead = 0
        else:
            age = time.time() - self._time
            self._how_dead = age / self._death_delay

    def is_dead(self):
        return self.life == 0

    def point1(self):
        return self._x1, self._y1

    def point2(self):
        return self._x2, self._y2

    def center(self):
        return self._center
