import PlateDetect
import PlateRecognition
import cv2
import numpy
import random
import imutils


def img_crop(input_img: numpy.ndarray, crop_area):
    (x, y, w, h) = crop_area
    x1 = x + w
    y1 = y + h
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    return input_img[y:y1, x:x1]


if __name__ == '__main__':
    fno = random.randint(1, 2000)
    img = cv2.imread(rf"D:\Project\raw data\yolo_plate_dataset\xemay239.jpg")
    while True:
        detect_result = PlateDetect.detectPlate(img)

        plate_img = img_crop(img, detect_result[0])
        rh, rw = plate_img.shape[:2]
        plate_img = imutils.resize(plate_img, height=300)
        plate_img = cv2.GaussianBlur(plate_img, (15, 15), 0)

        re = PlateRecognition.recognisePlate(plate_img)

        cv2.imshow(f'detect', img)
        cv2.imshow('reco', plate_img)

        key = cv2.waitKey(0)
        if key == 13:
            fno = random.randint(1, 2000)
            img = cv2.imread(rf"D:\Project\raw data\yolo_plate_dataset\xemay{fno}.jpg")
            print(fno)
        if key == 27:
            break

    cv2.destroyAllWindows()
