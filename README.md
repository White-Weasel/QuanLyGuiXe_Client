# Hỗ trợ quản lý gửi trả xe bằng công nghệ thị giác máy tính

<!-- 
### Table of Contents

- [Real-time Auto License Plate Recognition with Jetson Nano](#real-time-auto-license-plate-recognition-with-jetson-nano)
    - [Table of Contents](#table-of-contents)
  - [Pipeline](#pipeline)
  - [Setting up your Jetson](./doc/jetson-setup.md)
  - [Vienamese Plate Dataset](./doc/dataset.md)
  - [License PLate Detection](./doc/plate-detect.md)
  - [License Plate Recognition](./doc/plate-ocr.md)
  - [Trained Models](#trained-models)
  - [Reference](#reference)
-->
## Cài đặt:

* Tải file [Parking.Manager.Portable.exe](https://github.com/White-Weasel/QuanLyGuiXe_Client/releases/download/v0.01-beta/Parking.Manager.Portable.exe) từ trang [Releases](https://github.com/White-Weasel/QuanLyGuiXe_Client/releases)

## Set up project

- Cài đặt Python từ [trang chủ của Python](https://www.python.org/)

- Clone project về bằng lệnh:
`git clone https://github.com/White-Weasel/QuanLyGuiXe_Client.git`

- Cài đặt các package cần thiết bằng lệnh:
`pip install -r requirements.txt`
- Khởi động chương trình: `py main.py`

## Vienamese Plate Dataset
Dataset được project sử dụng:

* [Vienamese Plate Dataset](https://github.com/winter2897/Real-time-Auto-License-Plate-Recognition-with-Jetson-Nano/blob/main/doc/dataset.md)

* [License PLate Detection Dataset](https://drive.google.com/file/d/1KLK-DWgT3VoQH4fcTxAt2eB3sm7DGWAf/view?usp=sharing "plate dataset")

* [License Plate Recognition Dataset](https://drive.google.com/file/d/1Mdtfn39Jt53u9Y81jhoM-7pdQT7B_dF6/view?usp=sharing "ocr dataset")
          
## Huấn luyện yolov4 nhận diện chữ trên biển số bằng google colab:

* [Colab book link](https://colab.research.google.com/drive/1eHyKucynn30R5argUfVgyRcBoe7V5B0B)

<!--
* [License Plate Recognition](./doc/plate-ocr.md)

## Trained Models

 **1. License PLate Detection:**

|Network         |FPS |num_class|Model| 
|----------------|----|---------|-----|
|SSD-Mobilenet-v1|40  |1        |[link](https://drive.google.com/file/d/1eBO1UzZkp4pa5b966Un1oBwccdtt5ID_/view?usp=sharing)|
|YoloV4          |None|1        |[link](https://drive.google.com/file/d/1eG0ccO0HvberUiesS380zQNTJM3eHn_m/view?usp=sharing)|
|YoloV4-tiny     |None|1        |[link](https://drive.google.com/file/d/1ZLno2-e7yXnJs0wo9tVXq7bvqT-9Jawm/view?usp=sharing)|
|Wpod            |10  |1        |[link](https://drive.google.com/file/d/1pUHHPu31QQittRnKIXRmhAe1j-diCv1N/view?usp=sharing)|

**2. License Plate Recognition:**

|Network         |FPS |num_class|Model| 
|----------------|----|---------|-----|
|SSD-Mobilenet-v1|40  |36       |[link](https://drive.google.com/file/d/1wTTWONFUXRBtSKA-Cq3snL21KXCB80PS/view?usp=sharing)|
|SVM             |None|36       |[link](https://drive.google.com/file/d/1rmQi7NwKAeunvmB8dF_SUi2JVEmRop4g/view?usp=sharing)|

-->
## Reference

```
[1] https://github.com/winter2897/Real-time-Auto-License-Plate-Recognition-with-Jetson-Nano
```
