import os
import urllib

import cv2
import random

import imutils
import numpy


class BoundingBox:
    def __init__(self, box, label):
        (self.x, self.y, self.w, self.h) = box
        """self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)"""
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

    def draw(self, img: numpy.ndarray, color=(50, 50, 255), *args, **kwargs):
        a_boxes = absolute_size_from_relative_size([self.box, ], img.shape[:2])[0]
        draw_boxes(img, [a_boxes, ], color, *args, **kwargs)
        cv2.putText(img, self.label, (a_boxes[0], a_boxes[1]), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)


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


def img_from_url(url: str):
    url_response = urllib.request.urlopen(url)
    img_array = numpy.array(bytearray(url_response.read()), dtype=numpy.uint8)
    img = cv2.imdecode(img_array, -1)
    return img


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


def img_crop(img: numpy.ndarray, crop_area) -> numpy.ndarray:
    (x, y, w, h) = crop_area
    x1 = x + w
    y1 = y + h
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    return img[y:y1, x:x1]


def draw_bounding_boxes(img: numpy.ndarray, boxes: list[BoundingBox], color=(50, 50, 255), *args, **kwargs):
    for b in boxes:
        b.draw(img, color, *args, **kwargs)


def apply_brightness_contrast(input_img, brightness=0, contrast=0):
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow

        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()

    if contrast != 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)

        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf


def odd_paercent(in_int: int, percent: float):
    result = int(in_int * percent)
    if result % 2 == 0:
        result += 1
    return result


def gray_upscale(in_img: numpy.ndarray, height: int, blur_percent: float = 0.03):
    in_img = cv2.cvtColor(in_img, cv2.COLOR_RGB2GRAY)
    in_img = cv2.cvtColor(in_img, cv2.COLOR_GRAY2RGB)

    in_img = imutils.resize(in_img, height=height)

    blur_size = odd_paercent(height, blur_percent)
    in_img = cv2.GaussianBlur(in_img, (blur_size, blur_size), 0)
    in_img = apply_brightness_contrast(in_img, -20, 50)

    return in_img


def file_path(r_path):
    this_file = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(this_file, r_path)
    return path
