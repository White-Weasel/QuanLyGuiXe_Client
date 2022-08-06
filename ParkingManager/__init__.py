import tkinter
from functools import partial
from MyTkinter import *
import random
from ImageProcessor import img_from_url
import requests

COLORS = ["red", "orange", "yellow", "green", "blue", "violet", "black", ]
DEFAULT_BTN_HEIGHT = 3
DEFAULT_BTN_WIDTH = 15


# TODO: click result img to choose which barcode/plate to use
def random_rgb():
    r = random.randint(0, 250)
    g = random.randint(0, 250)
    b = random.randint(0, 250)

    return from_rgb((r, g, b))


class GUI(tkinter.Tk):
    """Import this in main script"""

    def __init__(self, *args, **kwargs):
        super(GUI, self).__init__(*args, **kwargs)
        self.mainFrame = MainFrame(self)
        self.mainloop()


# noinspection PyAttributeOutsideInit
class MainFrame(MyFrame):
    def __init__(self, master: tk.Tk, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        """Key event example"""
        def handle_keypress(event: tk.Event):
            if event.keycode == 27:
                self.on_closing()

        master.title("Quan ly gui tra xe")
        master.geometry('1000x700+250+30')
        master.bind("<Key>", handle_keypress)
        master.protocol('WM_DELETE_WINDOW', self.on_closing)

        self._debug = False
        self.CAMERA_HEIGHT = 250
        self.OUTPUT_HEIGHT = 100
        self.auto_entry = tk.BooleanVar()

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

        self.tooptip_list = [f.toolTip for f in get_all_child_frames(self)]
        master.after(10, self.home)

    def home(self):
        """Frames initialize"""
        self.left_frame = MyFrame(self, name='cameras feed')
        self.left_frame.pack(fill=BOTH, expand=NO, side=LEFT)

        self.face_cam_frame = MyFrame(self.left_frame, name='face cam frame')
        self.face_cam_frame.pack(fill=BOTH, expand=1, side=TOP)

        self.plate_cam_frame = MyFrame(self.left_frame, name='plate_cam_frame')
        self.plate_cam_frame.pack(fill=BOTH, expand=1, side=BOTTOM)

        self.right_frame = MyFrame(self, name='right_frame')
        self.right_frame.pack(fill=BOTH, expand=1, side=RIGHT, padx=50)

        self.entry_control_frame = MyFrame(self.right_frame, name='entry control')
        self.entry_control_frame.pack(fill=BOTH, expand=1, side=TOP)

        self.gate_control_frame = MyFrame(self.right_frame, name='gate control')
        self.gate_control_frame.pack(fill=BOTH, expand=1, side=BOTTOM)

        self.detect_result_frame = MyFrame(self.entry_control_frame, name='detect results')
        self.detect_result_frame.pack(side=LEFT, fill=BOTH, expand=YES)

        self.entry_control_btns_frame = MyFrame(self.entry_control_frame, name='entry control btns')
        self.entry_control_btns_frame.pack(side=RIGHT, fill=BOTH, expand=YES)

        """Result frames"""
        self.txt_result_frame = MyFrame(self.detect_result_frame, name='bien so')
        self.txt_result_frame.pack(fill=X, side=TOP, pady=25)

        # self.plate_num_result_frame = MyFrame(self.txt_result_frame, name='plate_num')
        # self.plate_num_result_frame.pack(side=TOP, fill=X, expand=YES)
        self.l3 = MyLabel(self.txt_result_frame, text="Bien so: ")
        self.l3.grid(row=1, column=1)
        self.plate_textbox = MyEntry(self.txt_result_frame, state=DISABLED, font='TkTextFont 16')
        self.plate_textbox.grid(row=1, column=2)

        # self.barcode_detect_result_frame = MyFrame(self.txt_result_frame, name='barcode')
        # self.barcode_detect_result_frame.pack(fill=X, side=BOTTOM)
        self.l4 = MyLabel(self.txt_result_frame, text="Ma ve: ")
        self.l4.grid(row=2, column=1)
        self.barcode_textbox = MyEntry(self.txt_result_frame, state=DISABLED, font='TkTextFont 16')
        self.barcode_textbox.grid(row=2, column=2)

        self.plate_detect_result_frame = MyFrame(self.detect_result_frame, name='anh bien so')
        self.plate_detect_result_frame.pack(fill=BOTH, pady=25, side=TOP)
        self.l5 = MyLabel(self.plate_detect_result_frame, text='Bien so: ')
        self.l5.pack(anchor=NW)
        self.plate_detect_output_img = ImageViewer(self.plate_detect_result_frame, img_height=100)
        self.plate_detect_output_img.pack(anchor=NW)

        """Cam frames widgets"""
        self.l1 = MyLabel(self.face_cam_frame, text="Camera 1")
        self.l1.pack(anchor=NW)
        # default capture backend cause warning when closed. cv2.CAP_DSHOW backend does not
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cam1 = BarcodeWidget(master=self.face_cam_frame, cap=cap, img_height=self.CAMERA_HEIGHT,
                                  txt_out_widget=self.barcode_textbox)
        self.cam1.pack(anchor=CENTER)

        self.l2 = MyLabel(self.plate_cam_frame, text="Camera 2")
        self.l2.pack(side=TOP, anchor=NW)

        self.cam2 = PlateDetectWidget(master=self.plate_cam_frame,
                                      img_out_widget=self.plate_detect_output_img,
                                      txt_out_widget=self.plate_textbox,
                                      img_height=self.CAMERA_HEIGHT)
        # FIXME: PlateProcess.py predicts this differently
        img = img_from_url(r"https://raw.githubusercontent.com/White-Weasel/QuanLyGuiXe_img/master/img/xemay567.jpg")
        self.cam2.set_img(img, self.CAMERA_HEIGHT)
        self.cam2.pack(side=TOP)

        def random_plate_img():
            # TODO: get img in new thread
            a = random.randint(0, 2000)
            self.cam2.set_img(img_from_url(
                rf"https://raw.githubusercontent.com/White-Weasel/QuanLyGuiXe_img/master/img/xemay{a}.jpg"),
                self.CAMERA_HEIGHT)

        self.b1 = MyButton(self.plate_cam_frame, text='Next random img', height=2, command=partial(random_plate_img))
        self.b1.pack(side=BOTTOM)

        """Entry Control frame"""
        # TODO: do smt with this btn
        self.snap_btn = MyButton(self.entry_control_btns_frame,
                                 text="Chup anh",
                                 height=3, width=15,
                                 state=DISABLED)
        self.snap_btn.pack(side=TOP, pady=25)
        self.enter_btn = MyButton(self.entry_control_btns_frame, text='Gui xe',
                                  height=DEFAULT_BTN_HEIGHT, width=DEFAULT_BTN_WIDTH)
        self.enter_btn.pack(side=TOP, pady=25)
        self.auto_checkbox = tk.Checkbutton(self.entry_control_btns_frame,
                                            text="Tu dong gui",
                                            variable=self.auto_entry,
                                            onvalue=True,
                                            offvalue=False,
                                            command=partial(self.toggle_auto))
        self.auto_checkbox.select()
        self.auto_checkbox.pack(side=TOP)

        self.gate_status_frame = MyFrame(self.gate_control_frame, name='gate status', borderwidth=1)
        self.gate_status_frame.pack(expand=YES, side=TOP, anchor=N)
        self.gate_label = MyLabel(self.gate_status_frame, text="Trang thai cong: ")
        self.gate_label.pack(side=LEFT)
        self.gate_status_label = GateStatusWidget(self.gate_status_frame,
                                                  text="",
                                                  foreground='red',
                                                  font=('Courier', 26),
                                                  backend_url='127.0.0.1:8000')
        self.gate_status_label.pack(side=RIGHT, padx=20)

        def gate_control(action: str):
            data = {'action': action}
            requests.post('http://127.0.0.1:8000/gate_control', json=data)

        self.gate_control_btn_frame = MyFrame(self.gate_control_frame, name='gate control btn')
        self.gate_control_btn_frame.pack(fill=Y, side=TOP, expand=YES, anchor=N)
        self.open_gate_btn = MyButton(self.gate_control_btn_frame, text='Mo cong',
                                      height=DEFAULT_BTN_HEIGHT, width=DEFAULT_BTN_WIDTH,
                                      command=partial(gate_control, 'open'))
        self.open_gate_btn.pack(side=LEFT, anchor=CENTER, padx=10)
        self.close_gate_btn = MyButton(self.gate_control_btn_frame, text='Dong cong',
                                       height=DEFAULT_BTN_HEIGHT, width=DEFAULT_BTN_WIDTH,
                                       command=partial(gate_control, 'close'))
        self.close_gate_btn.pack(side=RIGHT, anchor=CENTER, padx=10)

        self.default_frame_color = []
        for f in get_all_child_frames(self):
            self.default_frame_color.append(f.cget("background"))
        self.pack(fill=BOTH, expand=YES, padx=25, pady=25)

    def snapshot(self):
        self.plate_textbox.insert(INSERT, 'abc')

    def toggle_debug(self):
        """Toggle frame backgroud color, used to check widget size and location"""

        self._debug = not self._debug
        """Toggle help tooltips"""
        for tt in self.tooptip_list:
            if self._debug:
                tt.bind()
            else:
                tt.unbind()

        """Toggle frame bg color"""
        if self._debug:
            for frame in get_all_child_frames(self):
                frame.configure(bg=random_rgb())
        else:
            for frame, color in zip(get_all_child_frames(self), self.default_frame_color):
                frame.configure(bg=color)

    def toggle_auto(self):
        if self.auto_entry.get():
            self.cam2.img_out_widget = self.plate_detect_output_img

            self.plate_textbox.configure(state=DISABLED)
            self.snap_btn.configure(state=DISABLED)
        else:
            self.cam1.output_widget = None
            self.cam2.img_out_widget = None

            self.plate_detect_output_img.configure(image='')

            self.plate_textbox.configure(state=NORMAL)
            self.snap_btn.configure(state=NORMAL)

    def on_closing(self):
        self.stopAllThread()

        # FIXME: only the main thread can call to tkinter funtion. That's why the app can freeze here
        #  The after(200) funtion is only a bandaid fix and can fail if stopAllThread take too long
        self.master.after(200, self.master.destroy)


if __name__ == '__main__':
    root = tk.Tk()

    window = MainFrame(root, name="main frame")
    window.mainloop()
