import sys
import threading
from inputs import get_gamepad
import cv2, imutils
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGridLayout, QLCDNumber
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage, QIcon, QFont

class VideoCapture(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Advanced Video Capture System")
        self.setWindowIcon(QIcon('camera_icon.png'))
        self.resize(1200, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #333333;
                color: #ffffff;
            }
            QLabel, QLCDNumber {
                font: bold 14px;
            }
            QPushButton {
                background-color: #0055ff;
                color: #ffffff;
                font: bold 14px;
                padding: 6px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #0077ff;
            }
            """)

        self.setupWidgets()
        self.setupLayout()

    def setupWidgets(self):
        self.video_label = QLabel("Original Feed")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.ml_video_label = QLabel("Processed Feed")
        self.ml_video_label.setAlignment(Qt.AlignCenter)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.system_status_led = QLabel()
        self.system_status_led.setFixedSize(20, 20)
        self.update_system_status_led(False)

        self.ph_lcd = QLCDNumber()
        self.temp_lcd = QLCDNumber()
        self.water_pressure_lcd = QLCDNumber()
        self.water_level_lcd = QLCDNumber()

        self.start_button.clicked.connect(self.start_video)
        self.stop_button.clicked.connect(self.stop_video)

    def setupLayout(self):
        layout = QGridLayout()
        layout.addWidget(self.video_label, 0, 0, 1, 3)
        layout.addWidget(self.ml_video_label, 0, 3, 1, 3)
        layout.addWidget(self.start_button, 1, 0)
        layout.addWidget(self.stop_button, 1, 1)
        layout.addWidget(self.system_status_led, 1, 2, 1, 1, Qt.AlignCenter)

        sensors_info = [("pH Value:", self.ph_lcd), ("Temperature (C):", self.temp_lcd),
                        ("Water Pressure (KPa):", self.water_pressure_lcd), ("Water Level:", self.water_level_lcd)]
        for i, (label, widget) in enumerate(sensors_info):
            layout.addWidget(QLabel(label), 2 + i, 0)
            layout.addWidget(widget, 2 + i, 1, 1, 2)

        self.setLayout(layout)

    def update_system_status_led(self, status):
        color = "green" if status else "red"
        self.system_status_led.setStyleSheet(f"QLabel {{ background-color: {color}; border-radius: 10px; }}")

    def start_video(self):
        self.video = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(33)

    def stop_video(self):
        self.timer.stop()
        self.video.release()

    def update_frames(self):
        ret, frame = self.video.read()
        if ret:
            original_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            q_img_original = QImage(original_frame.data, original_frame.shape[1], original_frame.shape[0], QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_img_original))

            processed_frame = self.process_frame_with_ml_model(frame)
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            q_img_ml = QImage(processed_frame.data, processed_frame.shape[1], processed_frame.shape[0], QImage.Format_RGB888)
            self.ml_video_label.setPixmap(QPixmap.fromImage(q_img_ml))

    # def recieve_serial_sensor(self):
    #     self.timeout += 1
    #     # print (self.timeout)
    #     serial_thread = threading.Timer(0.1, self.recieve_serial_sensor)
    #     if ser.is_open == True:
    #         serial_thread.start()
    #         if ser.in_waiting:
    #             eol = b'\n'
    #             leneol = len(eol)
    #             line = bytearray()
    #             while True:
    #                 c = ser.read(1)
    #                 if c:
    #                     line += c
    #                     if line[-leneol:] == eol:
    #                         break
    #                 else:
    #                     break
    #                 # print (line)
    #                 # print (type(line))
    #             line = line.rstrip()
    #             message = line.decode("utf-8")
    #             sensors = []
    #             j=0
    #             for i in range(0,len(message)):
    #                 if message[i] == '/':
    #                     sensors.append(message[j:i])
    #                     j = i
    #             self.ph_lcd.display(sensors[0])
    #             print (sensors[0])
    #             self.temp_lcd.display(sensors[1])
    #             print (sensors[1])
    #             # self.water_pressure_lcd.display(sensors[2])
    #             # print (sensors[2])
    #             # self.water_level_lcd.display(sensors[3])
    #             # print (sensors[3])
    #             self.timeout = 0
    def process_frame_with_ml_model(self, frame):
        # Placeholder for ML model processing
        return frame

    def check_systems_ready(self):
        # Placeholder for system readiness checks
        return True

class XboxController(object):
    MAX_TRIG_VAL = 400
    MAX_JOY_VAL = 200

    def __init__(self):

        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        self.read()

    def read(self):  # return the buttons/triggers that you care about in this methode
        # if abs(self.RightJoystickX)<20 and abs(self.RightJoystickY)>20:
        #     self.surgecontrol()
        #     return self.RightJoystickY
        # if abs(self.RightJoystickX)>20 and abs(self.RightJoystickY)<20:
        #     self.swaycontrol()
        #     return self.RightJoystickX
        print("Called")
        self.surgecontrol()
        # x = int(self.LeftJoystickX)
        # y = int(self.LeftJoystickY)
        # a = self.A
        # b = self.X # b=1, x=2
        # l2 = self.LeftTrigger
        # r2 = self.RightTrigger
        # l3 = self.LeftThumb
        # r3 = self.RightThumb
        # r1 = self.RightBumper
        # l1 = self.LeftBumper

        # return [left,right, r1]

    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL  # normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL  # normalize between 0 and 1
                elif event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.A = event.state
                elif event.code == 'BTN_NORTH':
                    self.Y = event.state  # previously switched with X
                elif event.code == 'BTN_WEST':
                    self.X = event.state  # previously switched with Y
                elif event.code == 'BTN_EAST':
                    self.B = event.state
                elif event.code == 'BTN_THUMBL':
                    self.LeftThumb = event.state
                elif event.code == 'BTN_THUMBR':
                    self.RightThumb = event.state
                elif event.code == 'BTN_SELECT':
                    self.Back = event.state
                elif event.code == 'BTN_START':
                    self.Start = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY1':
                    self.LeftDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY2':
                    self.RightDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY3':
                    self.UpDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY4':
                    self.DownDPad = event.state

    def surgecontrol(self):
        fthruster1 = 1500
        fthruster2 = 1500
        lthruster = 1500
        rthruster = 1500
        dthruster1 = 1500
        dthruster2 = 1500
        val = self.RightJoystickY
        fthruster1 = 1500 - val
        fthruster2 = 1500 - val
        ser.write((str(int(fthruster1)) + str(int(fthruster2)) + str(int(lthruster)) + str(int(rthruster)) + str(
            int(dthruster1)) + str(int(dthruster2)) + '/').encode('UTF-8'))
        # print(((str(fthruster1) + str(fthruster2) + str(lthruster) + str(rthruster) + str(dthruster1) + str(dthruster2) + '/').encode('UTF-8')))

    def swaycontrol(self):
        fthruster1 = 1500
        fthruster2 = 1500
        lthruster = 1500
        rthruster = 1500
        dthruster1 = 1500
        dthruster2 = 1500
        val = self.RightJoystickX
        rthruster = 1500 + val
        lthruster = 1500 + val
        ser.write((str(int(fthruster1)) + str(int(fthruster2)) + str(int(lthruster)) + str(int(rthruster)) + str(
            int(dthruster1)) + str(int(dthruster2)) + '/').encode('UTF-8'))

    def heavecontrol(self):
        fthruster1 = 1500
        fthruster2 = 1500
        lthruster = 1500
        rthruster = 1500
        dthruster1 = 1500
        dthruster2 = 1500
        val = self.LeftJoystickY
        dthruster1 = 1500 + val
        dthruster2 = 1500 + val
        ser.write((str(int(fthruster1)) + str(int(fthruster2)) + str(int(lthruster)) + str(int(rthruster)) + str(
            int(dthruster1)) + str(int(dthruster2)) + '/').encode('UTF-8'))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoCapture()
    window.show()
    sys.exit(app.exec_())