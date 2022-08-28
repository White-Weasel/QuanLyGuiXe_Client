import PlateDetector
import PlateRecognition
import cv2
import random
import imutils
import time
from ImageProcessor import draw_bounding_boxes, img_crop, gray_upscale

if __name__ == '__main__':
    fno = random.randint(1, 2000)
    a = 1916
    img = cv2.imread(rf"D:\Project\raw data_\yolo_plate_dataset\xemay{a}.jpg")
    while True:
        ctime = time.time()
        detect_result = PlateDetector.detectPlate(img, draw=True)
        exec_time = time.time() - ctime
        print(exec_time)

        plate_img = img_crop(img, detect_result[0])
        print(f"plate height: {plate_img.shape[0]}")
        gray_plate_img = gray_upscale(plate_img, height=416)
        # gray_plate_img = imutils.resize(plate_img, height=416)

        # g_re = PlateRecognition.recognisePlate(gray_plate_img, min_confidence=0.5, draw=True)
        re = PlateRecognition.recognisePlate(gray_plate_img, min_confidence=0.5, draw=True, gray_scale=False)

        # draw_bounding_boxes(plate_img, re)
        img = imutils.resize(img, height=416)
        cv2.imshow(f'detect', img)
        cv2.imshow('reco', gray_plate_img)

        key = cv2.waitKey(0)
        if key == 13:
            fno = random.randint(1, 2000)
            img = cv2.imread(rf"D:\Project\raw data_\yolo_plate_dataset\xemay{fno}.jpg")
            print(f"\nimage No.{fno}")
        if key == 27:
            break

    cv2.destroyAllWindows()
