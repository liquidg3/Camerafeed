import cv2
from shapely.geometry import LineString
from shapely import geometry
import math

line_index = 0


class Tripline:
    _point_1 = None
    _point_2 = None
    _color = None
    _stroke = None
    colliding = False
    _buffer_size = 10
    count = 0
    _line = None
    _collisions = None
    _direction_1 = None
    _direction_2 = None
    _buffer_1 = None
    _buffer_2 = None
    _is_buffer = False
    _line_index = 0

    def __init__(self, point_1=(0, 0), point_2=(100, 0), color=(255, 0, 0), stroke=2, buffer_size=10,
                 direction_1='north', direction_2='south'):

        global line_index

        self._collisions = {}
        self._point_1 = point_1
        self._point_2 = point_2
        self._stroke = stroke
        self._color = color
        self._direction_1 = direction_1
        self._direction_2 = direction_2
        self._buffer_size = buffer_size

        self._line = LineString([point_1, point_2])
        self._line_index = line_index
        line_index += 1

        # for meta data
        self._line_key = "line-%d" % self._line_index

        # cache angle
        self._angle = self.angle()

        # draw buffer lines (really thin trip lines)
        if buffer_size is not None:
            buffer1_point_1 = self._buffer_position(self._point_1, self._angle)
            buffer1_point_2 = self._buffer_position(self._point_2, self._angle)

            self._buffer_1 = Tripline(point_1=buffer1_point_1, point_2=buffer1_point_2, color=color, stroke=1,
                                      buffer_size=None)

            buffer2_point_1 = self._buffer_position(self._point_1, self._angle - 180)
            buffer2_point_2 = self._buffer_position(self._point_2, self._angle - 180)

            self._buffer_2 = Tripline(point_1=buffer2_point_1, point_2=buffer2_point_2, color=color, stroke=1,
                                      buffer_size=None)
        else:
            self._is_buffer = True

    def _buffer_position(self, point, angle):
        x = point[0]
        y = point[1]
        r = self._buffer_size
        a = angle * math.pi / 180

        new_point = (int(x + r * math.sin(a)), int(y + r * math.cos(a)))

        return new_point

    def angle(self):
        dx = self._point_2[0] - self._point_1[0]
        dy = self._point_2[1] - self._point_1[1]
        theta = math.atan2(dy, dx)
        theta *= 180 / math.pi
        if theta < 0:
            theta += 360
        return theta * -1

    def draw(self, frame):

        # draw buffer lines
        if self._buffer_1 is not None:
            self._buffer_1.draw(frame)

        if self._buffer_2 is not None:
            self._buffer_2.draw(frame)

        cv2.line(frame, self._point_1, self._point_2, self._color, self._stroke)

        if not self._is_buffer:
            font = cv2.FONT_HERSHEY_SIMPLEX
            msg = 'Count: %d' % self.count

            height = 15
            width = 50
            top_left = (self._point_1[0], int(self._point_1[1] - height / 2))

            cv2.rectangle(frame, (top_left[0], top_left[1]), (top_left[0] + width, top_left[1] + height), self._color,
                          thickness=-1)
            cv2.putText(frame, msg, (self._point_1[0] + 5, self._point_1[1] + 2), font, 0.3, (255, 255, 255))

        return frame

    def collides_with(self, person):
        center = person.center()
        point = geometry.Point(center[0], center[1])
        circle = point.buffer(10).boundary

        intersection = circle.intersection(self._line)

        return not intersection.is_empty

    # 1 means new collision, 2 means old collision
    def add_collision(self, person):
        self.colliding = True
        person.colliding = True
        key = person.name

        # if first hit
        if key not in self._collisions:

            self.count += 1
            self._collisions[key] = 10

            buffer_key = self._line_key + '-buffer'
            direction = None

            if buffer_key in person.meta:
                direction = person.meta[buffer_key]
                person.labels[self._line_key] = 'Heading %s' % direction
                person.meta[self._line_key] = direction
                del person.meta[buffer_key]

            return 1

        return 2

    def remove_collision(self, person):
        key = person.name
        if key in self._collisions:
            self._collisions[key] -= 1
            if self._collisions[key] == 0:
                del self._collisions[key]

    # returning 0 means no collission, 1 means new collision, 2 means old collision
    def handle_collision(self, person):

        buffer_key = self._line_key + '-buffer'

        # do buffer checks
        for i in range(1, 3):

            buffer = getattr(self, '_buffer_%d' % i, None)

            if buffer is not None:
                if buffer.collides_with(person):
                    direction = getattr(self, '_direction_%d' % i)
                    person.meta[buffer_key] = direction

        if self.collides_with(person):
            return self.add_collision(person)
        else:
            self.remove_collision(person)
            return 0
