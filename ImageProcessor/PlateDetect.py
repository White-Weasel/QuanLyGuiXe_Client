import cv2
import numpy as np
import imutils
from ImageProcessor import absolute_size_from_relative_size, draw_boxes

# Constants.
INPUT_WIDTH = 320
INPUT_HEIGHT = 320
SCORE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.45
CONFIDENCE_THRESHOLD = 0.75

# Network files location
# YOLO_WEIGHT = r"ImageProcessor/Network/plate_yolov4/backup/yolov4-obj_best.weights"
# YOLO_CFG = r"ImageProcessor/Network/plate_yolov4/cfg/yolov4-obj.cfg"
PLATE_DETECT_YOLO_TINY_WEIGHT = r"D:\Project\QuanLyGuiXe_Client\ImageProcessor\Network\plate_yolov4_tiny\backup\yolov4-tiny-obj_best.weights"
PLATE_DETECT_YOLO_TINY_CFG = r"D:\Project\QuanLyGuiXe_Client\ImageProcessor\Network\plate_yolov4_tiny\cfg\yolov4-tiny-obj.cfg"

# FIXME: path not exist after installed
PLATE_DETECT_TINY_MODEL = cv2.dnn.readNet(PLATE_DETECT_YOLO_TINY_WEIGHT, PLATE_DETECT_YOLO_TINY_CFG)


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


def post_process(img, detect_result, min_confidence: float = CONFIDENCE_THRESHOLD, draw: bool = True):
    arr = np.zeros(detect_result[0][:1].shape)
    for r in detect_result:
        arr = np.concatenate([arr, np.array(r)])

    re = np.array([c for c in arr if c[4] > min_confidence])
    boxes = np.array([c[:4] for c in re])
    confidences = [c[4] for c in re]

    indices = cv2.dnn.NMSBoxes(boxes, confidences, min_confidence, NMS_THRESHOLD)
    boxes = [boxes[i] for i in indices]
    boxes = absolute_size_from_relative_size(boxes, img.shape[:2])
    if draw:
        draw_boxes(img, boxes, (250, 250, 50), 2)
    return boxes


def detectPlate(img, network=PLATE_DETECT_TINY_MODEL, min_confidence: float = 0.5, draw: bool = True):
    if network is None:
        network = PLATE_DETECT_TINY_MODEL
    result = pre_process(img, network)
    return post_process(img, result, min_confidence=min_confidence, draw=draw)


if __name__ == '__main__':
    model = cv2.dnn.readNet(PLATE_DETECT_YOLO_TINY_WEIGHT, PLATE_DETECT_YOLO_TINY_CFG)

    cap = cv2.VideoCapture(r"D:\Project\raw data\raw\20220701_171831.mp4")
    # img = cv2.imread(rf"D:\Project\raw data\raw\20220701_171809.jpg")
    # img = cv2.resize(img, None, fx=0.25, fy=0.25)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    while cap.isOpened():

        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 0)
            frame = cv2.flip(frame, 1)

            frame = imutils.resize(frame, height=900)

            result = pre_process(frame, model)

            post_process(frame, result)

            cv2.imshow("video", frame)

            if cv2.waitKey(1) == 27:
                break
        else:
            break
