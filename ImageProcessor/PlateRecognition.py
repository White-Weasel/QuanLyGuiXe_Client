import cv2
import numpy
import numpy as np
import imutils
from ImageProcessor import absolute_size_from_relative_size, draw_boxes, BoundingBox

# Constants.
INPUT_WIDTH = 256
INPUT_HEIGHT = 256
SCORE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.45
CONFIDENCE_THRESHOLD = 0.75

# Network files location
# YOLO_WEIGHT = r"ImageProcessor/Network/plate_yolov4/backup/yolov4-obj_best.weights"
# YOLO_CFG = r"ImageProcessor/Network/plate_yolov4/cfg/yolov4-obj.cfg"
YOLO_TINY_WEIGHT = r"D:\Project\QuanLyGuiXe_Client\ImageProcessor\Network\plate_ocr_yolov4_tiny\backup\yolov4-tiny-custom_final.weights"
YOLO_TINY_CFG = r"D:\Project\QuanLyGuiXe_Client\ImageProcessor\Network\plate_ocr_yolov4_tiny\cfg\yolov4-tiny-custom.cfg"

LABELS = ['00', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
          'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

# FIXME: path not exist after installed
TINY_MODEL = cv2.dnn.readNet(YOLO_TINY_WEIGHT, YOLO_TINY_CFG)


# MODEL = cv2.dnn.readNet(YOLO_WEIGHT, YOLO_CFG)


def pre_process(input_image, net):
    # Create a 4D blob from a frame.
    blob = cv2.dnn.blobFromImage(input_image, 1 / 255, (INPUT_WIDTH, INPUT_HEIGHT), [0, 0, 0], 1, crop=False)
    # blob = cv2.dnn.blobFromImage(image=input_image, size=(300, 300), mean=(104, 117, 123), swapRB=True)

    # Sets the input to the network.
    net.setInput(blob)

    # Run the forward pass to get output of the output layers.
    outputs = net.forward(net.getUnconnectedOutLayersNames())
    return outputs


def result_labels(arr, min_confidence):
    result = {}
    for i in range(0, len(LABELS)):
        boxes = np.array([c for c in arr if c[5 + i] > min_confidence])
        if len(boxes) > 0:
            result[LABELS[i]] = boxes
    return result


def sort_boxes(boxes: list[BoundingBox]):
    half_y = numpy.average([b.y for b in boxes])
    upper_half = [b for b in boxes if b.y < half_y]
    upper_half.sort()
    lower_half = [b for b in boxes if b.y > half_y]
    lower_half.sort()
    return upper_half+lower_half


def post_process(img:numpy.ndarray, detect_result, min_confidence: float = CONFIDENCE_THRESHOLD, draw: bool = True):
    arr = np.zeros(detect_result[0][:1].shape)
    for r in detect_result:
        arr = np.concatenate([arr, np.array(r)])

    re = result_labels(arr, min_confidence)
    ouput = []
    for label, boxes_arr in re.items():
        boxes = np.array([c[:4] for c in boxes_arr])
        # TODO: LABELS.index is not optimized
        confidences = [c[5 + LABELS.index(label)] for c in boxes_arr]

        indices = cv2.dnn.NMSBoxes(boxes, confidences, min_confidence, NMS_THRESHOLD)
        boxes = [boxes[i] for i in indices]
        a_boxes = absolute_size_from_relative_size(boxes, img.shape[:2])
        ouput += [BoundingBox(b, label) for b in boxes]
        if draw:
            draw_boxes(img, a_boxes, (250, 250, 50), 2, label=label)
    ouput = sort_boxes(ouput)
    return ouput


def recognisePlate(img, network=TINY_MODEL, min_confidence: float = 0.5, draw: bool = True):
    if network is None:
        network = TINY_MODEL
    result = pre_process(img, network)
    return post_process(img, result, min_confidence=min_confidence, draw=draw)


if __name__ == '__main__':
    model = cv2.dnn.readNet(YOLO_TINY_WEIGHT, YOLO_TINY_CFG)

    img = cv2.imread(rf"D:\Project\raw data\yolo_plate_ocr_dataset\7xemay2018.jpg")
    img = imutils.resize(img, height=300)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    re = recognisePlate(img)
    cv2.imshow('result', img)
    if cv2.waitKey(0) == 13:
        pass
    cv2.destroyAllWindows()
