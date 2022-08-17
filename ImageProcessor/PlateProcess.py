import PlateDetector
import PlateRecognition
import cv2
import random
import imutils
from ImageProcessor import draw_bounding_boxes, img_crop, gray_upscale

if __name__ == '__main__':
    fno = random.randint(1, 2000)
    a = 567
    img = cv2.imread(rf"D:\Project\raw data_\yolo_plate_dataset\xemay{a}.jpg")
    while True:
        detect_result = PlateDetector.detectPlate(img)

        plate_img = img_crop(img, detect_result[0])
        # gray_plate_img = gray_upscale(plate_img, height=300)
        plate_img = imutils.resize(plate_img, height=300)

        # g_re = PlateRecognition.recognisePlate(gray_plate_img, min_confidence=0.5, draw=True)
        re = PlateRecognition.recognisePlate(plate_img, min_confidence=0.5, draw=True)
        # draw_bounding_boxes(plate_img, re)

        cv2.imshow(f'detect', img)
        cv2.imshow('reco', plate_img)

        key = cv2.waitKey(0)
        if key == 13:
            fno = random.randint(1, 2000)
            img = cv2.imread(rf"D:\Project\raw data_\yolo_plate_dataset\xemay{fno}.jpg")
            print(fno)
        if key == 27:
            break

    cv2.destroyAllWindows()
