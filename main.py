import time
import tkinter as tk
from tkinter import ttk
from functools import partial
from MyTkinter.ToolTips import CreateToolTip
from MyTkinter.MyTkinter import *
import random
from utls.StopableThread import StopableThread

COLORS = ["red", "orange", "yellow", "green", "blue", "violet", "black", ]


def random_rgb():
    r = random.randint(0, 250)
    g = random.randint(0, 250)
    b = random.randint(0, 250)

    return from_rgb((r, g, b))


# noinspection PyAttributeOutsideInit
class MainFrame(MyFrame):
    def __init__(self, master: tk.Tk, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        master.title("Quan ly gui tra xe")
        master.geometry("1000x600")
        master.bind("<Key>", handle_keypress)
        self.master.protocol('WM_DELETE_WINDOW', self.on_closing)

        self._debug = False
        self.CAMERA_HEIGHT = 300
        self.OUTPUT_HEIGHT = 100
        self.auto_entry = tk.BooleanVar()

        self.left_frame = MyFrame(self, name='cameras feed')
        self.left_frame.pack(fill=BOTH, expand=NO, side=LEFT)

        self.face_cam_frame = MyFrame(self.left_frame, name='frame 1-1')
        self.face_cam_frame.pack(fill=BOTH, expand=1, side=TOP)

        self.plate_cam_frame = MyFrame(self.left_frame, name='frame 1-2')
        self.plate_cam_frame.pack(fill=BOTH, expand=1, side=BOTTOM)

        self.right_frame = MyFrame(self, name='frame 2')
        self.right_frame.pack(fill=BOTH, expand=1, side=RIGHT, padx=50)

        self.entry_control_frame = MyFrame(self.right_frame, name='entry control')
        self.entry_control_frame.pack(fill=BOTH, expand=1, side=TOP)

        self.gate_control_frame = MyFrame(self.right_frame, name='gate control')
        self.gate_control_frame.pack(fill=BOTH, expand=1, side=BOTTOM)

        self.detect_result_frame = MyFrame(self.entry_control_frame, name='detect results')
        self.detect_result_frame.pack(side=LEFT, fill=BOTH, expand=YES)

        self.entry_control_btns_frame = MyFrame(self.entry_control_frame, name='entry control btns')
        self.entry_control_btns_frame.pack(side=RIGHT, fill=BOTH, expand=YES)

        self.l1 = MyLabel(self.face_cam_frame, text="Camera 1")
        self.l1.pack(anchor=NW)

        self.l2 = MyLabel(self.plate_cam_frame, text="Camera 2")
        self.l2.pack(side=TOP, anchor=NW)

        self.img1 = PlateDetectCam(master=self.plate_cam_frame,
                                   img=rf"D:\Project\raw data\yolo_plate_dataset\xemay{random.randint(0, 2000)}.jpg",
                                   img_height=self.CAMERA_HEIGHT)
        self.img1.pack(side=TOP)

        def random_plate_img():
            a = random.randint(0, 2000)
            self.img1.set_img(rf"D:\Project\raw data\yolo_plate_dataset\xemay{a}.jpg", self.CAMERA_HEIGHT)

        self.b1 = MyButton(self.plate_cam_frame, text='Next random img', height=2, command=partial(random_plate_img))
        self.b1.pack(side=BOTTOM)

        self.plate_detect_result_frame = MyFrame(self.detect_result_frame, name='bien so')
        self.plate_detect_result_frame.pack(fill=BOTH)
        self.l3 = MyLabel(self.plate_detect_result_frame, text="Bien so: ")
        self.l3.pack(side=LEFT)
        self.plate_textbox = MyEntry(self.plate_detect_result_frame, state=DISABLED)
        self.plate_textbox.pack(side=RIGHT, fill=X, expand=YES)

        self.face_detect_result_frame = MyFrame(self.detect_result_frame, name='khuon mat')
        self.face_detect_result_frame.pack(fill=BOTH, pady=25)
        self.l4 = MyLabel(self.face_detect_result_frame, text="Khuon mat: ")
        self.l4.pack(anchor=NW)
        self.face_detect_ouput_img = MyLabel(self.face_detect_result_frame)
        self.face_detect_ouput_img.pack(anchor=NW)

        cap = cv2.VideoCapture(0)
        self.cam1 = FaceDetectCam(master=self.face_cam_frame, cap=cap, img_height=self.CAMERA_HEIGHT,
                                  output_widget=self.face_detect_ouput_img)
        self.cam1.pack(anchor=CENTER)

        self.snap_btn = MyButton(self.entry_control_btns_frame,
                                 text="Chup anh",
                                 height=3, width=15,
                                 command=partial(self.cam1.output_frame_to_widget, self.face_detect_ouput_img),
                                 state=DISABLED)
        self.snap_btn.pack(side=TOP, pady=25)
        self.enter_btn = MyButton(self.entry_control_btns_frame, text='Gui xe', height=3, width=15)
        self.enter_btn.pack(side=TOP, pady=25)
        self.auto_checkbox = tk.Checkbutton(self.entry_control_btns_frame,
                                            text="Tu dong gui",
                                            variable=self.auto_entry,
                                            onvalue=True,
                                            offvalue=False,
                                            command=partial(self.toggle_auto))
        self.auto_checkbox.select()
        self.auto_checkbox.pack(side=TOP, pady=25)

        menubar = Menu(master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.home)
        filemenu.add_command(label="Open")
        filemenu.add_command(label="Save")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=master.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        viewmenu = Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Debug mode", command=partial(self.toggle_debug))
        menubar.add_cascade(label="View", menu=viewmenu)

        master.config(menu=menubar)

        self.tooptip_list = [CreateToolTip(f, self.widget_tooltips_content(f)) for f in get_all_child_frames(self)]
        self.home()

    def home(self):
        self.default_frame_color = []
        for f in get_all_child_frames(self):
            self.default_frame_color.append(f.cget("background"))
        self.pack(fill=BOTH, expand=YES, padx=25, pady=25)

    def snapshot(self):
        self.plate_textbox.insert(INSERT, 'abc')

    def toggle_debug(self):
        """Toggle frame backgroud color, used to check widget size and location"""

        self._debug = not self._debug
        for tt in self.tooptip_list:
            if self._debug:
                tt.bind()
            else:
                tt.unbind()

        if self._debug:
            for frame in get_all_child_frames(self):
                frame.configure(bg=random_rgb())
        else:
            for frame, color in zip(get_all_child_frames(self), self.default_frame_color):
                frame.configure(bg=color)

    def toggle_auto(self):
        if self.auto_entry.get():
            self.cam1.output_widget = self.face_detect_ouput_img
            self.plate_textbox.configure(state=DISABLED)
            self.snap_btn.configure(state=DISABLED)
        else:
            self.cam1.output_widget = None
            self.face_detect_ouput_img.configure(image='')
            self.plate_textbox.configure(state=NORMAL)
            self.snap_btn.configure(state=NORMAL)

    def on_closing(self):
        self.stopAllThread()

        self.master.destroy()

    @staticmethod
    def widget_tooltips_content(frame: MyFrame):
        result = frame.winfo_name()
        for f in get_all_master_frames(frame):
            result = f"{f.winfo_name()}\n" + result
        return result


if __name__ == '__main__':
    root = tk.Tk()


    def handle_keypress(event: tk.Event):
        """Print the key code to the key pressed"""
        # print(event.keycode)
        if event.keycode == 27:
            root.destroy()


    window = MainFrame(root, name="main frame")
    window.mainloop()
