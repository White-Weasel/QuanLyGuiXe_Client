import json
import threading
from tkinter import *
import tkinter as tk
from typing import Union, Callable
import numpy
import ImageProcessor.PlateDetector
import ImageProcessor.PlateRecognition
import ImageProcessor.BarcodeReader
import ImageProcessor.FaceDetector
import cv2
import imutils
from PIL import Image, ImageTk
import websocket
from ImageProcessor import img_crop, BoundingBox
import logging


# TODO: create detect_plate function sepereated from the main frunction so GUI can call them without reload the frame
class MyFrame(tk.Frame):
    """
    A frame that hold lists of its child
    """

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.entry_list: list[MyEntry] = []
        self.label_list: list[MyLabel] = []
        self.button_list: list[MyButton] = []
        self.text_list: list[MyText] = []
        self.frame_list: list[MyFrame] = []
        self.canvas_list = []
        self.img_list = []
        self.thread_list = []
        self.toolTip = ToolTip(self, self.widget_tooltips_content())
        try:
            master.frame_list.append(self)
        except AttributeError:
            master.frame_list = [self]

    def all_text_widget(self):
        result = []
        for f in get_all_child_frames(self):
            result += f.entry_list
            result += f.text_list
        return result

    def stopAllThread(self):
        """
        Stop all thread in this frame and all of its child
        """
        # TODO: It would be sensible to use join here but only main thread can call to tkinter funtions,
        #   so t.join() here will make the program freeze because the thread do call to those tkinter function.
        #   A potential fix would be to remove all tkinter funtion call in other threads and use after()
        #   in main thread to fetch and process data from other threads
        for f in get_all_child_frames(self):
            for t in f.thread_list:
                t.stop()
                print(f"stoped {t}")
                logging.info(f"stoped {t}")

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
    def __init__(self, master: MyFrame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
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
    """Turn a cv2 image in numpy.ndarray format into a format that tkinter can use"""
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


class ImageViewer(tk.Label):
    """Widget to show a statis image"""

    def __init__(self, master,
                 cv2_img: numpy.ndarray = None,
                 img_height: int = 100,
                 *args, **kwargs):
        super(ImageViewer, self).__init__(master, *args, **kwargs)
        try:
            master.img_list.append(self)
        except AttributeError:
            master.img_list = [self]
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
    """
    A widget that show a static image, detect plate in it and show detect result on other widgets.
    """

    def __init__(self,
                 detect_network=ImageProcessor.PlateDetector.PLATE_DETECT_TINY_MODEL,
                 recognise_network=ImageProcessor.PlateRecognition.RECOGNISE_PLATE_TINY_MODEL,
                 min_confidence: float = 0.5,
                 output_height: int = 100,
                 *args, **kwargs):
        """
        init.

        :param recognise_network: Deep learning network used to recognise plate.
        :param detect_network: Deep learning network used to detect plate.
        :param min_confidence:
        :param img_out_widget: widget to show cropped image of plate.
        :param output_height: the height that the cropped image will be resized to.
        :param txt_out_widget: widget to print plate text to.
        """
        super().__init__(*args, **kwargs)
        self.detect_result = None
        self.recognise_result = None
        self.recognise_network = recognise_network
        self.detect_network = detect_network
        self.min_confidence = min_confidence
        self.output_height = output_height
        self.plate_list = []
        self.plate_imgs = None

    def set_img(self, img: numpy.ndarray = None, img_height: int = None):
        if img_height is None:
            img_height = self.img_height
        self.cv2_img = img
        self.detect_result = ImageProcessor.PlateDetector.detectPlate(self.cv2_img, draw=True)
        self.photo = photo_from_ndarray(self.cv2_img, img_height)
        setLabelImg(self, self.photo)

        if len(self.detect_result) > 0:
            self.plate_imgs = [img_crop(self.cv2_img, p) for p in self.detect_result]
            self.recognise_result = [ImageProcessor.PlateRecognition.recognisePlate(i, draw=False)
                                     for i in self.plate_imgs]
            """
            if self.img_out_widget is not None:
                setLabelImg(self.img_out_widget, photo_from_ndarray(self.plate_imgs, self.output_height))
            """
            p_list = []
            for p in self.recognise_result:
                plate = ''
                for b in p:
                    plate += b.label
                p_list.append(plate)
            self.plate_list = p_list
            """
            if self.txt_out_widget is not None:
                print_to_text_widget(self.txt_out_widget, plate[:2] + '-' + plate[2:4] + '-' + plate[4:])
            """


class VideoFeed(MyLabel):
    """
    Widget to show webcam video\n
    REMEMBER TO STOP IT PROPERLY. Use the stop_lock attribute to stop it.
    """

    def __init__(self,
                 master: MyFrame,
                 cap: cv2.VideoCapture,
                 img_height: int = 250,
                 onBarcodeDetected: Callable = None,
                 onBarcodeNotDetected: Callable = None,
                 *args, **kwargs):
        super(VideoFeed, self).__init__(master=master, *args, **kwargs)
        self.imgtk = None
        try:
            master.thread_list.append(self)
        except AttributeError:
            master.thread_list = [self]

        self.onBarcodeNotDetectedCallback = onBarcodeNotDetected
        self.onBarcodeDetectedCallback = onBarcodeDetected

        self.barcodes: list[ImageProcessor.BarcodeReader.Barcode] = []
        self.faces: list[BoundingBox] = []

        self.cap = cap
        self.img_height = img_height
        self.stop_lock = False
        self.thread = threading.Thread(target=self.showFrame)
        self.thread.start()

    # noinspection PyAttributeOutsideInit
    def showFrame(self):
        """
        This function will be running on another thread.
        BEWARE that tkinter functions will run in the main thread so joining this thread will cause freezing.
        """
        # TODO: The self.after method will slow the app down, but the while method will cause flashing
        while not self.stop_lock:
            succ, self.frame = self.cap.read()
            if succ:
                self.frame = cv2.flip(self.frame, 1)

                self.barcodes = ImageProcessor.BarcodeReader.readBarcode(self.frame, draw=True)
                self.faces = ImageProcessor.FaceDetector.detectFace(self.frame, draw=True)

                if len(self.barcodes) > 0:
                    if self.onBarcodeDetectedCallback is not None:
                        self.onBarcodeDetectedCallback()
                else:
                    if self.onBarcodeNotDetectedCallback is not None:
                        self.onBarcodeNotDetectedCallback()

                imgtk = photo_from_ndarray(self.frame, self.img_height)
                setLabelImg(self, imgtk)
            # self.after(20, self.showFrame)
        else:
            self.cap.release()
            print('closed cap')
            logging.info('Closed cv2 cap')

    def stop(self):
        self.stop_lock = True

    def join(self):
        self.thread.join()


# noinspection PyUnusedLocal,PyMethodMayBeStatic
class GateStatusWidget(MyLabel):
    """Widget with a websocket to show gate status. It runs on another thread so REMEMBER to stop it"""

    def __init__(self, master: MyFrame, backend_url: str, *args, **kwargs):
        super(GateStatusWidget, self).__init__(master, *args, **kwargs)
        self.backend_url = backend_url
        master.thread_list.append(self)
        self.thread = threading.Thread(target=self.websocket_thread)
        self.thread.start()

    # noinspection PyAttributeOutsideInit
    def websocket_thread(self):
        """
        This function will run on another thread. Closing the socket will stop this thread.
        Since it doesn't use any tkinter funtion, it might be safe to join it.
        """
        self.websocket = websocket.WebSocketApp(f"ws://{self.backend_url}/gate_status",
                                                on_message=self.on_message,
                                                on_open=self.on_open,
                                                on_error=self.on_error)
        self.websocket.run_forever()

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if data['gate_status']:
                gate_status = 'Mo'
            else:
                gate_status = 'Dong'
            self.config(text=gate_status)
        except KeyError:
            pass

    def on_open(self, ws):
        print("opening websocket")
        self.websocket.send('status')

    def on_error(self, ws, error):
        print(error)

    def stop(self):
        self.websocket.close()
        self.join()

    def join(self):
        self.thread.join()


def from_rgb(rgb):
    """
    Translates a rgb tuple of int to a tkinter friendly color code
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
