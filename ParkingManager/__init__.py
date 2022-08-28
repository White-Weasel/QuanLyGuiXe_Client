import datetime
import tkinter
from functools import partial
import utls
from MyTkinter import *
import random
from ImageProcessor import img_from_url
import requests
import logging

logging.basicConfig(filename='parking.log',
                    filemode='a',
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.DEBUG)

COLORS = ["red", "orange", "yellow", "green", "blue", "violet", "black", ]
DEFAULT_BTN_HEIGHT = 3
DEFAULT_BTN_WIDTH = 15
DEFAULT_IMG_HEIGHT = 100
BACKEND_URL = '127.0.0.1:8000'
DEFAULT_FONT = 'TkTextFont 11'
DEFAULT_BIG_FONT = 'TkTextFont 14'
from .Parking import ParkingInfo


# TODO: click result img to choose which barcode/plate to use
def random_rgb():
    r = random.randint(0, 250)
    g = random.randint(0, 250)
    b = random.randint(0, 250)

    return from_rgb((r, g, b))


def print_api_output(widget, text):
    widget.configure(text=text, fg='blue')


def print_backend_err(widget, text):
    widget.configure(text=text, fg='red')


class GUI(tkinter.Tk, metaclass=utls.Singleton):
    """Import this in main script"""

    def __init__(self, *args, **kwargs):
        super(GUI, self).__init__(*args, **kwargs)
        logging.info('\n\n')
        logging.info('Initializing app')
        random.seed(datetime.datetime.now().timestamp())

        """Key event example"""

        def handle_keypress(event: tk.Event):
            if event.keycode == 27:
                # self.on_closing()
                pass

        self.title("Quan ly gui tra xe")
        # self.geometry('1000x700+250+30')
        self.geometry("")
        self.minsize(1000, 700)
        self.bind("<Key>", handle_keypress)

        self.mainFrame = MainFrame(self)

        def search():
            SearchWindow(name='search info')

        def report():
            ReportWindow(name='report')

        def err():
            raise TypeError('tpe err')

        menubar = Menu(self)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Search", command=search)
        filemenu.add_command(label="Report", command=report)
        filemenu.add_command(label="Err", command=err)

        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        viewmenu = Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Debug mode", command=partial(self.mainFrame.toggle_debug))
        menubar.add_cascade(label="View", menu=viewmenu)

        self.config(menu=menubar)
        self.after(10, self.mainFrame.home)
        self.mainloop()


# noinspection PyAttributeOutsideInit
class MainFrame(MyFrame, metaclass=utls.Singleton):
    def __init__(self, master: tk.Tk, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        master.protocol('WM_DELETE_WINDOW', self.on_closing)

        # noinspection PyUnusedLocal
        def test_des(event=None):
            print("destroying")

        self.bind("<Destroy>", test_des)

        self._debug = False
        self.CAMERA_HEIGHT = 250
        self.OUTPUT_HEIGHT = 100
        self.auto_entry = tk.BooleanVar()
        self.barcode_read = tkinter.BooleanVar()
        self.cur_barcode = ''

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

        self.img_detect_result_frame = MyFrame(self.right_frame, name='gate control')
        self.img_detect_result_frame.pack(fill=BOTH, expand=1, side=BOTTOM)

        self.txt_detect_result_frame = MyFrame(self.entry_control_frame, name='detect results')
        self.txt_detect_result_frame.pack(side=LEFT, fill=BOTH, pady=10)

        self.entry_control_btns_frame = MyFrame(self.entry_control_frame, name='entry control btns')
        self.entry_control_btns_frame.pack(side=RIGHT, fill=BOTH, expand=YES)

        """
        Result frames
        """
        # self.plate_num_result_frame = MyFrame(self.txt_result_frame, name='plate_num')
        # self.plate_num_result_frame.pack(side=TOP, fill=X, expand=YES)
        self.l3 = MyLabel(self.txt_detect_result_frame, text="Bien so: ", font=DEFAULT_FONT)
        self.l3.grid(row=1, column=1)
        self.plate_textbox = MyEntry(self.txt_detect_result_frame, state=DISABLED, font=DEFAULT_BIG_FONT)
        self.plate_textbox.grid(row=1, column=2)

        # self.barcode_detect_result_frame = MyFrame(self.txt_result_frame, name='barcode')
        # self.barcode_detect_result_frame.pack(fill=X, side=BOTTOM)
        # self.l4 = MyLabel(self.txt_detect_result_frame, text="Ma ve: ", font=DEFAULT_FONT)
        # self.l4.grid(row=2, column=1)
        # self.barcode_textbox = MyEntry(self.txt_detect_result_frame, state=DISABLED, font=DEFAULT_BIG_FONT)
        # self.barcode_textbox.grid(row=2, column=2)
        # self.barcode_checkbox = tk.Checkbutton(self.txt_detect_result_frame,
        #                                        variable=self.barcode_read,
        #                                        onvalue=True,
        #                                        offvalue=False,
        #                                        state=DISABLED,
        #                                        height=3)
        # self.barcode_checkbox.grid(row=2, column=2, sticky=W)

        self.out_label = MyLabel(self.txt_detect_result_frame, text='Hello!', font=DEFAULT_BIG_FONT, fg='blue')
        self.out_label.grid(row=3, column=1, columnspan=2, pady=20)

        """self.img_result_frame = MyFrame(self.txt_detect_result_frame, name='img_result_frame')
        self.img_result_frame.pack(fill=BOTH, pady=7, side=TOP)"""

        self.l5 = MyLabel(self.img_detect_result_frame, text='Anh bien so: ', font=DEFAULT_FONT)
        self.l5.grid(row=1, column=1, sticky=W)
        self.plate_images_frame = MyFrame(self.img_detect_result_frame, height=DEFAULT_IMG_HEIGHT)
        self.plate_images_frame.grid(row=1, column=2)

        self.l6 = MyLabel(self.img_detect_result_frame, text='Anh khuon mat: ', font=DEFAULT_FONT)
        self.l6.grid(row=2, column=1, sticky=W)
        self.face_images_frame = MyFrame(self.img_detect_result_frame, height=DEFAULT_IMG_HEIGHT)
        self.face_images_frame.grid(row=2, column=2)

        """Cam frames widgets"""
        self.l1 = MyLabel(self.face_cam_frame, text="Camera 1", font=DEFAULT_FONT)
        self.l1.pack(anchor=NW)
        # default capture backend cause warning when closed. cv2.CAP_DSHOW backend does not
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.main_cam = VideoFeed(master=self.face_cam_frame, cap=cap, img_height=self.CAMERA_HEIGHT,
                                  onBarcodeDetected=self.onBarcodeDetected)
        self.main_cam.pack(anchor=CENTER)

        self.l2 = MyLabel(self.plate_cam_frame, text="Camera 2", font=DEFAULT_FONT)
        self.l2.pack(side=TOP, anchor=NW)

        # FIXME: PlateProcess.py predicts this differently
        self.plate_cam = PlateDetectWidget(master=self.plate_cam_frame,
                                           img_height=self.CAMERA_HEIGHT)

        self.plate_cam.pack(side=TOP)

        self.b1 = MyButton(self.plate_cam_frame, text='Xe tiep theo', height=2,
                           command=partial(self.set_random_plate_img),
                           font=DEFAULT_FONT)
        self.b1.pack(side=BOTTOM)

        """Entry Control frame"""
        self.snap_btn = MyButton(self.entry_control_btns_frame,
                                 text="Chup anh",
                                 height=3, width=15,
                                 command=self.snap, font=DEFAULT_FONT)
        self.snap_btn.pack(side=TOP, pady=5)

        self.clear_btn = MyButton(self.entry_control_btns_frame,
                                  text='Clear',
                                  height=DEFAULT_BTN_HEIGHT, width=DEFAULT_BTN_WIDTH,
                                  command=self.clear_parking_info, font=DEFAULT_FONT)
        self.clear_btn.pack(side=TOP, pady=5)

        self.enter_btn = MyButton(self.entry_control_btns_frame, text='Gui xe',
                                  height=DEFAULT_BTN_HEIGHT, width=DEFAULT_BTN_WIDTH, font=DEFAULT_FONT,
                                  command=self.vehicle_entry)
        self.enter_btn.pack(side=TOP, pady=5)
        self.out_btn = MyButton(self.entry_control_btns_frame, text='Tra xe',
                                height=DEFAULT_BTN_HEIGHT, width=DEFAULT_BTN_WIDTH, font=DEFAULT_FONT,
                                command=self.vehicle_out)
        self.out_btn.pack(side=TOP, pady=5)

        self.auto_checkbox = tk.Checkbutton(self.entry_control_btns_frame,
                                            text="Tu dong gui",
                                            variable=self.auto_entry,
                                            onvalue=True,
                                            offvalue=False,
                                            command=partial(self.toggle_auto))
        self.auto_checkbox.select()
        self.auto_checkbox.pack(side=TOP)

        """
        self.gate_status_frame = MyFrame(self.img_detect_result_frame, name='gate status', borderwidth=1)
        self.gate_status_frame.pack(expand=YES, side=TOP, anchor=N)
        self.gate_label = MyLabel(self.gate_status_frame, text="Trang thai cong: ", font=DEFAULT_FONT)
        self.gate_label.pack(side=LEFT)
        self.gate_status_label = GateStatusWidget(self.gate_status_frame,
                                                  text="",
                                                  foreground='red',
                                                  font=('Courier', 26),
                                                  backend_url=BACKEND_URL)
        self.gate_status_label.pack(side=RIGHT, padx=20)

        def gate_control(action: str):
            data = {'action': action}
            requests.post('http://127.0.0.1:8000/gate_control', json=data)

        self.gate_control_btn_frame = MyFrame(self.img_detect_result_frame, name='gate control btn')
        self.gate_control_btn_frame.pack(fill=Y, side=TOP, expand=YES, anchor=N)
        self.open_gate_btn = MyButton(self.gate_control_btn_frame, text='Mo cong',
                                      height=DEFAULT_BTN_HEIGHT, width=DEFAULT_BTN_WIDTH,
                                      command=partial(gate_control, 'open'))
        self.open_gate_btn.pack(side=LEFT, anchor=CENTER, padx=10)
        self.close_gate_btn = MyButton(self.gate_control_btn_frame, text='Dong cong',
                                       height=DEFAULT_BTN_HEIGHT, width=DEFAULT_BTN_WIDTH,
                                       command=partial(gate_control, 'close'))
        self.close_gate_btn.pack(side=RIGHT, anchor=CENTER, padx=10)
        """

        self.set_random_plate_img(567)
        self.default_frame_color = []
        for f in get_all_child_frames(self):
            self.default_frame_color.append(f.cget("background"))
        self.pack(fill=BOTH, expand=YES, padx=25, pady=25)

    def set_random_plate_img(self, i: int = None):
        self.clear_parking_info()

        def thread_target():
            if i is None:
                a = random.randint(0, 2000)
            else:
                a = i
            self.plate_cam.set_img(img_from_url(
                rf"https://raw.githubusercontent.com/White-Weasel/QuanLyGuiXe_img/master/img/xemay{a}.jpg"),
                self.CAMERA_HEIGHT)
            print(f'random img {a}')
            logging.info(f'random img {a}')
            return

        t = threading.Thread(target=thread_target)
        t.start()

    def onBarcodeDetected(self):
        # TODO: change it to selected barcode
        if self.main_cam.barcodes[0].info != self.cur_barcode:
            utls.beep_beep()
            self.barcode_read.set(True)
            self.snap()

    def snap(self):
        self.clear_parking_info()
        if len(self.main_cam.barcodes) > 0:
            self.cur_barcode = self.main_cam.barcodes[0].info
        else:
            self.cur_barcode = None
        plate = self.plate_cam.plate_list[0]
        print_to_text_widget(self.plate_textbox, plate[:2] + '-' + plate[2:4] + '-' + plate[4:])

        for pimg in self.plate_cam.plate_imgs:
            i = ImageViewer(self.plate_images_frame, height=DEFAULT_IMG_HEIGHT)
            i.set_img(pimg)
            i.pack(side=LEFT)

        face_imgs = [img_crop(self.main_cam.frame, f.box, True) for f in self.main_cam.faces]
        for fimg in face_imgs:
            i = ImageViewer(self.face_images_frame, height=DEFAULT_IMG_HEIGHT)
            i.set_img(fimg)
            i.pack(side=LEFT)

    def parking_info(self) -> ParkingInfo:
        # TODO: use selected info
        plate = self.plate_textbox.get()
        if len(plate) < 1:
            plate = None
        else:
            plate = plate.replace('-', '')

        try:
            ticket = int(self.cur_barcode)
        except Exception as e:
            ticket = None
        result = ParkingInfo(ticket=ticket, plate=plate)
        print(result)
        return result

    def clear_parking_info(self):
        self.cur_barcode = ''
        for txtw in self.all_text_widget():
            print_to_text_widget(txtw, '')
        for i in self.plate_images_frame.img_list:
            i.destroy()
        for i in self.face_images_frame.img_list:
            i.destroy()

    def vehicle_entry(self):
        """Send data to server. Process data and show result"""

        def thread_target():
            data = self.parking_info()
            result = data.entry()
            if result.status_code / 100 == 2:
                res = result.json()
                logging.info(f"Get vehicle {data.plate} inside with ticket {res['ticket']}")
                if res['result']:
                    print_api_output(self.out_label, f"Gui xe thanh cong!\nBien so:{data.plate}")
                else:
                    print_api_output(self.out_label, f"Gui xe khong thanh cong")
            elif result.status_code / 100 == 5:
                try:
                    res = result.json()
                    print_backend_err(self.out_label, res['err'])
                except requests.exceptions.JSONDecodeError:
                    print_backend_err(self.out_label, f"Loi {result.status_code}: {str(result.content)}")
            elif result.status_code == 422:
                print_backend_err(self.out_label, "Thong tin khong hop le")
            else:
                print(f'error: {result.content}')
                logging.info(f'error: {result.content}')
            self.clear_parking_info()

        t = threading.Thread(target=thread_target)
        t.start()

    def vehicle_out(self):
        """Send data to server. Process data and show result"""

        def thread_target():
            data = self.parking_info()
            result = data.out()

            if result.status_code / 100 == 2:
                res = result.json()
                logging.info(f"Get vehicle {data.plate} out with ticket {data.ticket}")
                if res['result']:
                    print_api_output(self.out_label,
                                     f"Tra xe thanh cong!\nBien so:{data.plate}\nGia gui xe:{res['cost']}")
                else:
                    print_backend_err(self.out_label, f"Tra xe khong thanh cong")
            elif result.status_code / 100 == 5:
                try:
                    res = result.json()
                    print_backend_err(self.out_label, res['err'])
                except requests.exceptions.JSONDecodeError:
                    print_backend_err(self.out_label, f"Loi {result.status_code}: {str(result.content)}")
            elif result.status_code == 422:
                print_backend_err(self.out_label, "Thong tin khong hop le")
            else:
                print(f'error: {result.content}')
                logging.info(f'error: {result.content}')
            self.clear_parking_info()

        t = threading.Thread(target=thread_target)
        t.start()

    def snapshot(self):
        self.plate_textbox.insert(INSERT, 'abc')

    def toggle_debug(self):
        """Toggle frame backgroud color, used to check widget size and location"""

        self._debug = not self._debug
        """Toggle help tooltips"""
        for f in get_all_child_frames(self):
            if self._debug:
                f.toolTip.bind()
            else:
                f.toolTip.unbind()

        """Toggle frame bg color"""
        if self._debug:
            for frame in get_all_child_frames(self):
                frame.configure(bg=random_rgb())
        else:
            for frame, color in zip(get_all_child_frames(self), self.default_frame_color):
                frame.configure(bg=color)

    def toggle_auto(self):
        if self.auto_entry.get():
            self.plate_textbox.configure(state=DISABLED)
            self.snap_btn.configure(state=DISABLED)
        else:
            self.plate_textbox.configure(state=NORMAL)
            self.snap_btn.configure(state=NORMAL)

    def on_closing(self):
        self.stopAllThread()
        logging.info('Closing')
        print('closing main')
        # FIXME: only the main thread can call to tkinter funtion.
        #  That's why the app can freeze here if we use join().
        #  The after(200) funtion is only a bandaid fix and might fail if self.stopAllThread() take too long
        self.master.after(200, self.master.destroy)


class SearchWindow(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        super(SearchWindow, self).__init__(*args, **kwargs)
        self.title('Tim kiem xe')
        self.geometry("")
        self.minsize(600, 250)
        self._debug = False

        menubar = Menu(self)
        viewmenu = Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Debug mode", command=partial(self.toggle_debug))
        menubar.add_cascade(label="View", menu=viewmenu)
        self.config(menu=menubar)

        """Initialize frames"""
        self.mainframe = MyFrame(self, name='main search frame')
        self.mainframe.pack(fill=BOTH, expand=YES)
        self.result_frame = MyFrame(self.mainframe, name='search result frame')
        self.result_frame.pack(side=LEFT, expand=YES, fill=BOTH, padx=5, pady=5)
        self.input_frame = MyFrame(self.mainframe, name='search input frame')
        self.input_frame.pack(side=RIGHT, fill=BOTH, padx=5, pady=5)

        self.l1 = MyLabel(self.input_frame, text='Bien so: ', font=DEFAULT_FONT)
        self.l1.grid(row=1, column=1, sticky=W, padx=10)
        self.plate_txtbox = MyEntry(self.input_frame, font=DEFAULT_FONT)
        self.plate_txtbox.grid(row=1, column=2, sticky=W)

        self.search_btn = MyButton(self.input_frame,
                                   text='Tim kiem xe',
                                   height=DEFAULT_BTN_HEIGHT,
                                   command=self.search, font=DEFAULT_FONT)
        self.search_btn.grid(row=3, column=1, columnspan=2, pady=10)

        self.default_frame_color = []
        for f in get_all_child_frames(self.mainframe):
            self.default_frame_color.append(f.cget("background"))

    def toggle_debug(self):
        """Toggle frame backgroud color, used to check widget size and location"""

        self._debug = not self._debug
        """Toggle help tooltips"""
        for f in get_all_child_frames(self.mainframe):
            if self._debug:
                f.toolTip.bind()
            else:
                f.toolTip.unbind()

        """Toggle frame bg color"""
        if self._debug:
            for frame in get_all_child_frames(self.mainframe):
                frame.configure(bg=random_rgb())
        else:
            for frame, color in zip(get_all_child_frames(self.mainframe), self.default_frame_color):
                frame.configure(bg=color)

    def get_info(self):
        plate = self.plate_txtbox.get()
        info = ParkingInfo(plate=plate)
        return info

    def clear_result(self):
        for c in self.result_frame.winfo_children():
            c.destroy()

    def search(self):
        self.clear_result()

        info = self.get_info()
        result = info.search()

        if result.status_code / 100 == 2:
            result = result.json()
            self.show_result(result['data'])
        elif result.status_code / 100 == 5:
            out_label = MyLabel(self.result_frame, font=DEFAULT_FONT)
            out_label.pack(side=TOP, anchor=N, expand=YES)
            try:
                result = result.json()
                print_backend_err(out_label, result['err'])
            except requests.exceptions.JSONDecodeError:
                print_backend_err(out_label, result.content)

    def show_result(self, result: list[dict]):
        """
        Print search result if status code is 200
        :param result:
        :return:
        """
        if len(result) < 1:
            out_label = MyLabel(self.result_frame, font=DEFAULT_FONT)
            out_label.pack(side=TOP, anchor=N, expand=YES)
            print_api_output(out_label, 'Khong co thong tin gui xe tuong ung')
        else:
            c = 0
            for key in result[0].keys():
                title_label = MyLabel(self.result_frame, text=key, borderwidth=1, relief="solid", font=DEFAULT_BIG_FONT)
                title_label.grid(row=0, column=c, sticky="nsew", padx=2)
                c += 1

        r = 0
        for info in result:
            c = 0
            r += 1
            for value in info.values():
                value_label = MyLabel(self.result_frame, text=str(value), font=DEFAULT_FONT)
                value_label.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
                c += 1


class ReportWindow(Toplevel):
    def __init__(self, *args, **kwargs):
        super(ReportWindow, self).__init__(*args, **kwargs)

        self.title('Bao cao')
        self.geometry("")
        self.minsize(600, 250)
        self._debug = False

        menubar = Menu(self)
        viewmenu = Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Debug mode", command=partial(self.toggle_debug))
        menubar.add_cascade(label="View", menu=viewmenu)
        self.config(menu=menubar)

        """Initicalize frames"""
        self.mainFrame = MyFrame(self)
        self.mainFrame.pack(fill=BOTH, expand=YES)

        self.result_frame = MyFrame(self.mainFrame, borderwidth=1, relief='solid')
        self.result_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=5, pady=5)
        self.input_frame = MyFrame(self.mainFrame)
        self.input_frame.pack(side=RIGHT, fill=BOTH, pady=5, padx=5)

        """widget inistialize"""
        self.vehicle_inside_btn = MyButton(self.input_frame, text='Xe trong bai',
                                           font=DEFAULT_FONT, height=DEFAULT_BTN_HEIGHT,
                                           command=self.vehicle_inside)
        self.vehicle_inside_btn.pack(pady=5)

        self.default_frame_color = []
        for f in get_all_child_frames(self.mainFrame):
            self.default_frame_color.append(f.cget("background"))

    def toggle_debug(self):
        """Toggle frame backgroud color, used to check widget size and location"""

        self._debug = not self._debug
        """Toggle help tooltips"""
        for f in get_all_child_frames(self.mainFrame):
            if self._debug:
                f.toolTip.bind()
            else:
                f.toolTip.unbind()

        """Toggle frame bg color"""
        if self._debug:
            for frame in get_all_child_frames(self.mainFrame):
                frame.configure(bg=random_rgb())
        else:
            for frame, color in zip(get_all_child_frames(self.mainFrame), self.default_frame_color):
                frame.configure(bg=color)

    def clear_result(self):
        for c in self.result_frame.winfo_children():
            c.destroy()

    def vehicle_inside(self):
        self.clear_result()

        info = ParkingInfo(inside=True)
        result = info.search()
        if result.status_code / 100 == 2:
            result = result.json()
            self.show_result(result['data'])
        elif result.status_code / 100 == 5:
            out_label = MyLabel(self.result_frame, font=DEFAULT_FONT)
            out_label.pack(side=TOP, anchor=N, expand=YES)
            try:
                result = result.json()
                print_backend_err(out_label, result['err'])
            except requests.exceptions.JSONDecodeError:
                print_backend_err(out_label, result.content)

    def show_result(self, result: list[dict]):
        """
        Print search result if status code is 200
        :param result:
        :return:
        """
        if len(result) < 1:
            out_label = MyLabel(self.result_frame, font=DEFAULT_FONT)
            out_label.pack(side=TOP, anchor=N, expand=YES)
            print_api_output(out_label, 'Khong co thong tin gui xe tuong ung')
        else:
            c = 0
            for key in result[0].keys():
                title_label = MyLabel(self.result_frame, text=key, borderwidth=1, relief="solid", font=DEFAULT_BIG_FONT)
                title_label.grid(row=0, column=c, sticky="nsew", padx=2)
                c += 1

        r = 0
        for info in result:
            c = 0
            r += 1
            for value in info.values():
                value_label = MyLabel(self.result_frame, text=str(value), font=DEFAULT_FONT)
                value_label.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
                c += 1


if __name__ == '__main__':
    window = GUI()
