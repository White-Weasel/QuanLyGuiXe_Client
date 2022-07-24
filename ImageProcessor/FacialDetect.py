import cv2
import mediapipe as mp
import time

MIN_CONFIDENCE = 0.5

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
FACE_DETECTION = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=MIN_CONFIDENCE)


def detectFace(img, face_detection=FACE_DETECTION, draw: bool = True):
    (H, W) = img.shape[:2]
    detect_result = face_detection.process(img)
    result = []
    if detect_result.detections:
        for detection in detect_result.detections:
            face = detection.location_data.relative_bounding_box
            x = int(face.xmin * W)
            y = int(face.ymin * H)
            w = int(face.width * W)
            h = int(face.height * H)

            if draw:
                # mp_drawing.draw_detection(img, detection)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            result.append([x, y, w, h])
    return result


"""
if __name__ == '__main__':

    cap = cv2.VideoCapture(0)
    face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
    cTime = 0
    pTime = 0

    while True:
        success, frame = cap.read()
        frame = cv2.flip(frame, 1)
        (H, W) = frame.shape[:2]
        if not success:
            continue
        else:
            results = face_detection.process(frame)

        count = 1
        if results.detections:
            for detection in results.detections:
                # mp_drawing.draw_detection(frame, detection)
                face = detection.location_data.relative_bounding_box
                x = int(face.xmin * W)
                y = int(face.ymin * H)
                w = int(face.width * W)
                h = int(face.height * H)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Face {count}", (x, y), cv2.FONT_HERSHEY_PLAIN, 2, (50, 50, 255), 2)
                count += 1

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)

        cv2.imshow("Image", frame)
        if cv2.waitKey(1) == 27:
            break
"""
