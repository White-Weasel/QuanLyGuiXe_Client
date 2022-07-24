import cv2
import random
import numpy


class BoundingBox:
    def __init__(self, box, label):
        (self.x, self.y, self.w, self.h) = box
        self.label = label

    def __gt__(self, other: 'BoundingBox'):
        return self.x > other.x

    def __lt__(self, other: 'BoundingBox'):
        return self.x < other.x

    def __repr__(self):
        return self.label

    @property
    def box(self):
        box = (self.x, self.y, self.w, self.h)
        return box


class Plate:
    def __init__(self, box: list[BoundingBox], img: numpy.ndarray):
        self.upper_half: list[BoundingBox] = []
        self.lower_half: list[BoundingBox] = []
        self.boxes = box
        self.img = img
        self.sort_boxes()

    # noinspection PyShadowingNames
    def sort_boxes(self):
        half_y = numpy.average([b.y for b in self.boxes])
        self.upper_half = [b for b in self.boxes if b.y < half_y]
        self.upper_half.sort()
        self.lower_half = [b for b in self.boxes if b.y > half_y]
        self.lower_half.sort()
        return self.upper_half + self.lower_half

    # noinspection PyShadowingNames
    def __str__(self):
        result = ''
        for b in self.upper_half:
            result += b.label
        result += ''


def random_color():
    r = random.randint(0, 250)
    g = random.randint(0, 250)
    b = random.randint(0, 250)
    result = (r, g, b)
    return result


def absolute_size_from_relative_size(input_arr, size):
    result = []
    (H, W) = size
    for box in input_arr:
        (x, y, w, h) = box
        x = int((x - w / 2) * W)
        y = int((y - h / 2) * H)
        w = int(w * W)
        h = int(h * H)
        result.append([x, y, w, h])

    return result


def draw_boxes(img, boxes, *args, **kwargs):
    label = None
    try:
        label = kwargs.pop('label')
    except KeyError:
        pass
    for box in boxes:
        (x, y, w, h) = box
        cv2.rectangle(img, (x, y), (x + w, y + h), *args, **kwargs)
        if label is not None:
            cv2.putText(img, label, (x, y), cv2.FONT_HERSHEY_PLAIN, 2, (50, 50, 255), 2)


def draw_bounding_boxes(img, boxes: list[BoundingBox], color=(50, 50, 255), *args, **kwargs):
    for b in boxes:
        cv2.rectangle(img, (b.x, b.y), (b.x + b.w, b.y + b.h), color, *args, **kwargs)
        cv2.putText(img, b.label, (b.x, b.y), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)

