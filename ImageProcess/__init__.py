import cv2


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
    for box in boxes:
        (x, y, w, h) = box
        cv2.rectangle(img, (x, y), (x + w, y + h), *args, **kwargs)
