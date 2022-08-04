import threading
from tkinter import *
import tkinter as tk
from typing import Union
import numpy
import ImageProcessor.PlateDetect
import ImageProcessor.PlateRecognition
import ImageProcessor.BarcodeReader
# from ImageProcessor.FacialDetect import detectFace
import cv2
import imutils
from PIL import Image, ImageTk

from ImageProcessor import img_crop


class MyFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.entry_list = []
        self.label_list = []
        self.button_list = []
        self.text_list = []
        self.frame_list: list[MyFrame] = []
        self.canvas_list = []
        self.thread_list = []
        self.toolTip = ToolTip(self, self.widget_tooltips_content())
        try:
            master.frame_list.append(self)
        except AttributeError:
            master.frame_list = [self]

    def stopAllThread(self):
        # TODO: It would be sensible to use join here but only main thread can call to tkinter funtions,
        #   so t.join() here will make the program freeze because the thread do call to those tkinter function.
        #   A potential fix would be to remove all tkinter funtion call in other threads and use after()
        #   in main thread to fetch and process data from other threads
        for f in get_all_child_frames(self):
            for t in f.thread_list:
                t.stop()
                print(f"stoped {t}")

    def widget_tooltips_content(self):
        """return all parent widgets names"""
        result = self.winfo_name()
        for f in get_all_master_frames(self):
            result = f"{f.winfo_name()}\n" + result
        return result


class MyText(tk.Text):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        try:
            master.text_list.append(self)
        except AttributeError:
            master.text_list = [self]


class MyEntry(tk.Entry):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        try:
            master.entry_list.append(self)
        except AttributeError:
            master.entry_list = [self]


class MyLabel(tk.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        try:
            master.label_list.append(self)
        except AttributeError:
            master.label_list = [self]


class MyButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        try:
            master.button_list.append(self)
        except AttributeError:
            master.button_list = [self]


class MyCanvas(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        try:
            master.canvas_list.append(self)
        except AttributeError:
            master.canvas_list = [self]


def photo_from_ndarray(img, height: int = None):
    img = imutils.resize(img, height=height)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(image=img)

    return img


def setLabelImg(label: tk.Label, img):
    label.imgtk = img
    label.configure(image=img)


def print_to_text_widget(widget: Union[MyText, MyEntry], text):
    """print to a disabled text widget"""
    if widget['state'] == DISABLED:
        widget.config(state=NORMAL)
        widget.delete(0, END)
        widget.insert(0, text)
        widget.config(state=DISABLED)
    else:
        widget.delete(0, END)
        widget.insert(0, text)
    return


class VideoFeed(tk.Label):
    """REMEMBER to stop it with the program"""

    def __init__(self, master: MyFrame, cap: cv2.VideoCapture, img_height: int = 250, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.imgtk = None
        try:
            master.thread_list.append(self)
        except AttributeError:
            master.thread_list = [self]

        self.cap = cap
        self.img_height = img_height
        self.stop_lock = False
        self.thread = threading.Thread(target=self.showFrame)
        self.thread.start()

    def showFrame(self):
        """if not self.stop_lock:
            succ, frame = self.cap.read()
            if succ:
                imgtk = photo_from_ndarray(frame, self.img_height)
                setLabelImg(self, imgtk)

                self.after(20, self.showFrame)
        else:
            self.cap.release()"""
        return

    def stop(self):
        self.stop_lock = True

    def join(self):
        self.thread.join()


# class FaceDetectCam(VideoFeed):
#     def __init__(self, min_confidence: float = 0.5,
#                  output_widget: tk.Label = None,
#                  output_height: int = 100,
#                  *args, **kwargs):
#         super(FaceDetectCam, self).__init__(*args, **kwargs)
#
#         self.detect_result = None
#         self.frame = None
#         self.min_confidence = min_confidence
#         self.output_widget = output_widget
#         self.output_height = output_height
#
#     def output_frame_to_widget(self, widget):
#         if len(self.detect_result) > 0:
#             face_img = img_crop(self.frame, self.detect_result[0])
#             face_img = photo_from_ndarray(face_img, self.output_height)
#             setLabelImg(widget, face_img)
#
#     def showFrame(self):
#         if not self.stop_lock:
#             success, self.frame = self.cap.read()
#
#             if success:
#                 """remove this later"""
#                 self.frame = cv2.flip(self.frame, 1)
#
#                 # TODO: potential bug here, frame and detect_result should be in local scope to prevent old result
#                 #  being used
#                 self.detect_result = detectFace(self.frame, draw=True)
#
#                 imgtk = photo_from_ndarray(self.frame, self.img_height)
#                 setLabelImg(self, imgtk)
#                 if self.output_widget is not None:
#                     if len(self.detect_result) > 0:
#                         self.output_frame_to_widget(self.output_widget)
#                     else:
#                         self.output_widget.configure(image='')
#                 self.after(20, self.showFrame)
#         else:
#             self.cap.release()


class ImageViewer(tk.Label):
    def __init__(self, master,
                 cv2_img: numpy.ndarray = None,
                 img_height: int = 100,
                 *args, **kwargs):
        super(ImageViewer, self).__init__(master, *args, **kwargs)
        self.img_height = img_height

        if cv2_img is not None:
            self.set_img(cv2_img)
        else:
            self.cv2_img = cv2_img
            self.photo = None

    def set_img(self, img: numpy.ndarray = None, img_height: int = None):
        if img_height is None:
            img_height = self.img_height
        self.cv2_img = img
        self.photo = photo_from_ndarray(self.cv2_img, img_height)
        setLabelImg(self, self.photo)

    def set_img_file(self, file_path: str, img_height: int = None):
        img = cv2.imread(file_path)
        self.set_img(img, img_height)


class PlateDetectWidget(ImageViewer):
    def __init__(self, network=ImageProcessor.PlateDetect.PLATE_DETECT_TINY_MODEL,
                 min_confidence: float = 0.5,
                 img_out_widget: ImageViewer = None,
                 output_height: int = 100,
                 txt_out_widget: Union[MyText, MyEntry] = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.network = network
        self.min_confidence = min_confidence
        self.img_out_widget = img_out_widget
        self.txt_out_widget = txt_out_widget
        self.output_height = output_height

    def set_img(self, img: numpy.ndarray = None, img_height: int = None):
        if img_height is None:
            img_height = self.img_height
        self.cv2_img = img
        detect_result = ImageProcessor.PlateDetect.detectPlate(self.cv2_img, draw=True)
        self.photo = photo_from_ndarray(self.cv2_img, img_height)
        setLabelImg(self, self.photo)

        plate_img = img_crop(self.cv2_img, detect_result[0])
        recognise_result = ImageProcessor.PlateRecognition.recognisePlate(plate_img, draw=False)
        if self.img_out_widget is not None:
            setLabelImg(self.img_out_widget, photo_from_ndarray(plate_img, self.output_height))
        plate = ''
        for b in recognise_result:
            plate += b.label
        if self.txt_out_widget is not None:
            print_to_text_widget(self.txt_out_widget, plate)


class BarcodeWidget(VideoFeed):
    def __init__(self, txt_out_widget: Union[MyText, MyEntry] = None, *args, **kwargs):
        self.barcodes: list[ImageProcessor.BarcodeReader.Barcode] = []
        self.txt_out_widget = txt_out_widget
        super().__init__(*args, **kwargs)
        self.stop_lock = False

    # noinspection PyAttributeOutsideInit
    """def showFrame(self):
        if self.stop_lock:
            # FIXME: code doesnt go in here even if stop lock is true
            self.cap.release()
            print('closed cap')
        else:
            succ, self.frame = self.cap.read()
            if succ:
                self.frame = cv2.flip(self.frame, 1)

                self.barcodes = ImageProcessor.BarcodeReader.readBarcode(self.frame)

                if len(self.barcodes) > 0:
                    if self.txt_out_widget is not None:
                        barcode = self.barcodes[0].info
                        print_to_text_widget(self.txt_out_widget, barcode)

                imgtk = photo_from_ndarray(self.frame, self.img_height)
                setLabelImg(self, imgtk)
                self.after(20, self.showFrame)"""

    # noinspection PyAttributeOutsideInit
    def showFrame(self):
        while not self.stop_lock:
            succ, self.frame = self.cap.read()
            if succ:
                self.frame = cv2.flip(self.frame, 1)

                self.barcodes = ImageProcessor.BarcodeReader.readBarcode(self.frame)

                if len(self.barcodes) > 0:
                    if self.txt_out_widget is not None:
                        barcode = self.barcodes[0].info
                        print_to_text_widget(self.txt_out_widget, barcode)

                imgtk = photo_from_ndarray(self.frame, self.img_height)
                setLabelImg(self, imgtk)
        else:
            print_to_text_widget(self.txt_out_widget, 'closing')
            self.cap.release()
            return


def from_rgb(rgb):
    """translates a rgb tuple of int to a tkinter friendly color code
    """
    r, g, b = rgb
    return f'#{r:02x}{g:02x}{b:02x}'


def get_all_child_frames(frame: MyFrame) -> list[MyFrame]:
    result = [frame]
    for f in frame.frame_list:
        result += get_all_child_frames(f)
    return result


def get_all_master_frames(frame: MyFrame) -> Union[list[MyFrame], list]:
    result = []
    parent = frame.master
    while parent is not None:
        result.append(parent)
        parent = parent.master
    return result


def getAllThread(frame: MyFrame):
    result = []
    for f in get_all_child_frames(frame):
        if len(f.thread_list) > 0:
            result += f.thread_list
    return result


from .ToolTips import *
