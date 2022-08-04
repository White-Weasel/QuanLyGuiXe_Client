# Importing library
import cv2
import numpy
from ImageProcessor import draw_boxes

BARDET = cv2.barcode_BarcodeDetector()


class Barcode:
    def __init__(self, info, decoded_type, box):
        self.info = info
        self.decoded_type = decoded_type
        self.box = box

    def __repr__(self):
        return f"{self.info} at {self.box}"


def readBarcode(img):
    ok, decoded_info, decoded_type, corners = BARDET.detectAndDecode(img)
    result = []
    if ok:
        """boxes = [corners_to_rectangle(x) for x in corners]
        draw_boxes(frame, boxes, (0, 255, 0), 2)
        result = (ok, decoded_info, decoded_type, boxes)
        pass"""
        for i in range(0, len(decoded_type)):
            bar = Barcode(decoded_info[i], decoded_type[i], corners_to_rectangle(corners[i]))
            result.append(bar)
            draw_boxes(img, (bar.box,), (0, 255, 0), 2)

        result = [x for x in result if x.info != '']
        pass
    return result


def barcode_info_postprocess(info: tuple):
    return [x for x in info if x != '']


def corners_to_rectangle(coners: numpy.ndarray):
    x = int(numpy.amin(coners[:, 0]))
    y = int(numpy.amin(coners[:, 1]))
    w = int(numpy.amax(coners[:, 0]) - x)
    h = int(numpy.amax(coners[:, 1]) - y)
    result = (x, y, w, h)
    return result


"""
if __name__ == "__main__":
    # Take the image from user
    cap = cv2.VideoCapture(0)
    bardet = cv2.barcode_BarcodeDetector()
    old_info = None
    while True:
        succ, frame = cap.read()
        if succ:
            # frame = cv2.flip(frame, 1)
            res = readBarcode(frame)
            if len(res) > 0:
                print(res)

            cv2.imshow('barcode', frame)
            key = cv2.waitKey(1)
            if key == 27:
                break

    cap.release()
"""
