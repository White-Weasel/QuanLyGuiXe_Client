import collections.abc
from typing import Union

import cv2
import numpy
import numpy as np
import imutils
from ImageProcessor import absolute_size_from_relative_size, draw_boxes, BoundingBox, gray_upscale, file_path

# Constants.
INPUT_WIDTH = 256
INPUT_HEIGHT = 256
SCORE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.45
CONFIDENCE_THRESHOLD = 0.75

# Network files location
# YOLO_WEIGHT = r"ImageProcessor/Network/plate_yolov4/backup/yolov4-obj_best.weights"
# YOLO_CFG = r"ImageProcessor/Network/plate_yolov4/cfg/yolov4-obj.cfg"
RECOGNISE_PLATE_YOLO_TINY_WEIGHT = file_path(r"Network\plate_ocr_yolov4_tiny\backup\yolov4-tiny-custom_final.weights")
RECOGNISE_PLATE_YOLO_TINY_CFG = file_path(r"Network\plate_ocr_yolov4_tiny\cfg\yolov4-tiny-custom.cfg")

LABELS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
          'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

RECOGNISE_PLATE_TINY_MODEL = cv2.dnn.readNet(RECOGNISE_PLATE_YOLO_TINY_WEIGHT, RECOGNISE_PLATE_YOLO_TINY_CFG)


# MODEL = cv2.dnn.readNet(YOLO_WEIGHT, YOLO_CFG)


def pre_process(input_image: numpy.ndarray, net, gray_scale=True):
    """
    Use yolo model to detect characters in image.

    :param input_image: a cv2 image
    :param net: yolo model that we will use
    :param gray_scale: True: Convert the image to black and white before predict. False: Do nothing with the img
    :return:
    """
    if gray_scale:
        input_image = gray_upscale(input_image, height=INPUT_HEIGHT)
    # Create a 4D blob from a frame.
    blob = cv2.dnn.blobFromImage(input_image, 1 / 255, (INPUT_WIDTH, INPUT_HEIGHT), [0, 0, 0], 1, crop=False)
    # blob = cv2.dnn.blobFromImage(image=input_image, size=(300, 300), mean=(104, 117, 123), swapRB=True)

    # Sets the input to the network.
    net.setInput(blob)

    # Run the forward pass to get output of the output layers.
    outputs = net.forward(net.getUnconnectedOutLayersNames())
    return outputs


def result_labels(arr: numpy.ndarray, min_confidence: float):
    """
    Turn yolo predict result into a dict of detected object.

    :param min_confidence:
    :param arr: numpy array from yolo detect result
    """
    result = {}
    for i in range(0, len(LABELS)):
        boxes = np.array([c for c in arr if c[5 + i] > min_confidence])
        if len(boxes) > 0:
            result[LABELS[i]] = boxes
    return result


def sort_boxes(boxes: list[BoundingBox]) -> list[BoundingBox]:
    """
    Sort detected BoundingBoxs
    """
    half_y = numpy.average([b.y for b in boxes])
    upper_half = [b for b in boxes if b.y < half_y]
    upper_half.sort()
    lower_half = [b for b in boxes if b.y > half_y]
    lower_half.sort()
    return upper_half + lower_half


def post_process(input_img: numpy.ndarray,
                 detect_result,
                 min_confidence: float = CONFIDENCE_THRESHOLD,
                 draw: bool = True) -> list[BoundingBox]:
    """
    Process results from ImageProcess.PlateRecognition.pre_process.

    :param input_img: a cv2 image
    :param detect_result: raw results from ImageProcess.PlateRecognition.pre_process
    :param min_confidence:
    :param draw: True: draw boxes and label on input image. False: do nothing
    :return: a list of BoundingBox
    """
    arr = np.zeros(detect_result[0][:1].shape)
    for r in detect_result:
        arr = np.concatenate([arr, np.array(r)])

    re = result_labels(arr, min_confidence)
    output = []
    for label, boxes_arr in re.items():
        boxes = np.array([c[:4] for c in boxes_arr])
        # TODO: LABELS.index is not very optimized
        confidences = [c[5 + LABELS.index(label)] for c in boxes_arr]

        indices = cv2.dnn.NMSBoxes(boxes, confidences, min_confidence, NMS_THRESHOLD)
        boxes = [boxes[i] for i in indices]
        output += [BoundingBox(b, label) for b in boxes]
        if draw:
            a_boxes = absolute_size_from_relative_size(boxes, input_img.shape[:2])
            draw_boxes(input_img, a_boxes, (250, 250, 50), 2, label=label)
    output = sort_boxes(output)
    return output


def recognisePlate(input_img: numpy.ndarray,
                   gray_scale: bool = True,
                   network=RECOGNISE_PLATE_TINY_MODEL,
                   min_confidence: float = 0.5,
                   draw: bool = True) -> list[BoundingBox]:
    """
    Detect characters in plate image.

    :param input_img:  input image
    :param gray_scale: True: Convert the image to black and white before predict. False: Do nothing with the img
    :param network: darknet yolo model that we are going to use
    :param min_confidence: min confidence
    :param draw: True: draw boxes and label on input image. False: do nothing
    :return: array of BoundingBox
    """
    if network is None:
        network = RECOGNISE_PLATE_TINY_MODEL
    result = pre_process(input_img, network, gray_scale)
    return post_process(input_img, result, min_confidence=min_confidence, draw=draw)


if __name__ == '__main__':
    model = cv2.dnn.readNet(RECOGNISE_PLATE_YOLO_TINY_WEIGHT, RECOGNISE_PLATE_YOLO_TINY_CFG)

    img = cv2.imread(rf"D:\Project\raw data\yolo_plate_ocr_dataset\7xemay2018.jpg")
    img = imutils.resize(img, height=300)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    re = recognisePlate(img)
    cv2.imshow('result', img)
    if cv2.waitKey(0) == 13:
        pass
    cv2.destroyAllWindows()
