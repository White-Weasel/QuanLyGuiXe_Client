import threading
from tkinter import *
import tkinter as tk

import numpy

import ImageProcessor.PlateDetect
from ImageProcessor.FacialDetect import detectFace
import cv2
import imutils
from PIL import Image, ImageTk


def from_rgb(rgb):
    """translates a rgb tuple of int to a tkinter friendly color code
    """
    r, g, b = rgb
    return f'#{r:02x}{g:02x}{b:02x}'


def get_all_child_frames(frame):
    if frame is not None and frame is not list:
        result = frame.frame_list
        if len(result) > 0:
            for f in frame.frame_list:
                result += get_all_child_frames(f)
        return result


def get_all_master_frames(frame):
    result = []
    parent = frame.master
    while parent is not None:
        result.append(parent)
        parent = parent.master
    return result


def getAllThread(frame):
    if hasattr(frame, 'thread_list'):
        result = frame.thread_list
        if len(result) > 0:
            for f in frame.thread_list:
                result += getAllThread(f)
        return result
    else:
        return []


def img_crop(img: numpy.ndarray, crop_area):
    (x, y, w, h) = crop_area
    x1 = x + w
    y1 = y + h
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    return img[y:y1, x:x1]


class MyFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.entry_list = []
        self.label_list = []
        self.button_list = []
        self.text_list = []
        self.frame_list = []
        self.canvas_list = []
        self.thread_list = []
        try:
            master.frame_list.append(self)
        except AttributeError:
            master.frame_list = [self]

    def stopAllThread(self):
        for thread in getAllThread(self):
            thread.join()
            thread.stop()


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


class ToolTip(object):

    def __init__(self, widget):
        self.text = None
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        """Display text in tooltip window"""
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def createToolTip(widget, text):
    toolTip = ToolTip(widget)

    def enter(event):
        toolTip.showtip(text)

    def leave(event):
        toolTip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


def deleteToolTip(widget: tk.Widget):
    """delete the help tool tip of a widget"""
    widget.unbind('<Enter>')
    widget.unbind('<Leave>')


def photo_from_ndarray(img, height: int = None):
    img = imutils.resize(img, height=height)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(image=img)

    return img


def setLabelImg(label: tk.Label, img):
    label.imgtk = img
    label.configure(image=img)


class VideoFeed(tk.Label):
    """REMEMBER to stop it with the program"""

    def __init__(self, master: MyFrame, cap: cv2.VideoCapture, img_height: int = 250, *args, **kwargs):
        super(VideoFeed, self).__init__(master, *args, **kwargs)
        self.imgtk = None
        try:
            master.thread_list.append(self)
        except AttributeError:
            master.thread_list = [self]

        self.cap = cap
        self.img_height = img_height
        self._stop_lock = False
        self.thread = threading.Thread(target=self.showFrame)
        self.thread.start()

    def showFrame(self):
        if not self._stop_lock:
            succ, frame = self.cap.read()
            if succ:
                imgtk = photo_from_ndarray(frame, self.img_height)
                setLabelImg(self, imgtk)

                self.after(20, self.showFrame)
        else:
            self.cap.release()

    def stop(self):
        self._stop_lock = True

    def join(self):
        self.thread.join()


class FaceDetectCam(VideoFeed):
    def __init__(self, min_confidence: float = 0.5,
                 output_widget: tk.Label = None,
                 output_height: int = 100,
                 *args, **kwargs):
        super(FaceDetectCam, self).__init__(*args, **kwargs)

        self.detect_result = None
        self.frame = None
        self.min_confidence = min_confidence
        self.output_widget = output_widget
        self.output_height = output_height

    def output_frame_to_widget(self, widget):
        if len(self.detect_result) > 0:
            face_img = img_crop(self.frame, self.detect_result[0])
            face_img = photo_from_ndarray(face_img, self.output_height)
            setLabelImg(widget, face_img)

    def showFrame(self):
        if not self._stop_lock:
            success, self.frame = self.cap.read()

            if success:
                """remove this later"""
                self.frame = cv2.flip(self.frame, 1)

                # TODO: potential bug here, frame and detect_result should be in local scope only to prevent old
                #  result being used
                self.detect_result = detectFace(self.frame, draw=True)

                imgtk = photo_from_ndarray(self.frame, self.img_height)
                setLabelImg(self, imgtk)
                if self.output_widget is not None:
                    if len(self.detect_result) > 0:
                        self.output_frame_to_widget(self.output_widget)
                    else:
                        self.output_widget.configure(image='')
                self.after(20, self.showFrame)
        else:
            self.cap.release()


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
    def __init__(self, network=ImageProcessor.PlateDetect.TINY_MODEL, min_confidence: float = 0.5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.network = network
        self.min_confidence = min_confidence

    def set_img(self, img: numpy.ndarray = None, img_height: int = None):
        if img_height is None:
            img_height = self.img_height
        self.cv2_img = img
        ImageProcessor.PlateDetect.detectPlate(self.cv2_img, draw=True)
        self.photo = photo_from_ndarray(self.cv2_img, img_height)
        setLabelImg(self, self.photo)


from .ToolTips import *
