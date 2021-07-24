import sys
import mouse
import time
import pyautogui
import numpy as np
import cv2
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QGridLayout, QWidget, QPushButton, QLabel, QTextBrowser, \
    QMessageBox

area_x1 = 0
area_y1 = 0
area_x2 = 1920
area_y2 = 1080


def capture():
    img = pyautogui.screenshot(region=(area_x1, area_y1, area_x2 - area_x1, area_y2 - area_y1))
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return img


class Worker(QThread):
    up = pyqtSignal()
    working = 0

    def run(self):
        time.sleep(3)
        print("start")

        target = cv2.imread("target.png", cv2.IMREAD_GRAYSCALE)

        tcnt = 0
        while self.working == 0:
            tcnt += 1
            print(tcnt)
            img = capture()

            if img is None:
                break

            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 캡처한 이미지를 그레이스케일로

            res = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
            position = np.where(res >= 0.6)  # 유사도 0.6 이상 위치 찾기

            if len(position[0]) != 0:
                pyautogui.click(x=area_x1, y=area_y1, button="right")
                time.sleep(0.3)
                pyautogui.click(x=area_x1, y=area_y1, button="right")

                self.up.emit()

                time.sleep(4)

            time.sleep(0.5)

        print("stop")


class Main(QWidget):
    cnt = 0

    def __init__(self):
        super().__init__()
        self.initUI()

        self.worker = Worker()
        self.worker.up.connect(self.update)

    def update(self):
        self.cnt += 1
        self.fishingCounter.setText("낚시 횟수 : " + str(self.cnt))
        self.print_progress_text("낚시대를 건졌습니다.")

    def select_area(self):
        print("Select Area")
        while True:
            if mouse.is_pressed("left"):
                area_x1, area_y1 = mouse.get_position()
                reply = QMessageBox.question(self, '범위 선택',
                                             '범위의 왼쪽 위로 지정하시겠습니까?(범위 내에 자막이 모두 들어올 수 있어야 함)',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    print(str(area_x1) + "," + str(area_y1))
                    break
                else:
                    continue

        while True:
            if mouse.is_pressed("left"):
                area_x2, area_y2 = mouse.get_position()
                reply = QMessageBox.question(self, '범위 선택',
                                             '범위의 오른쪽 아래로 지정하시겠습니까?(범위 내에 자막이 모두 들어올 수 있어야 함)',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    print(str(area_x2) + "," + str(area_y2))
                    break
                else:
                    continue

    def print_progress_text(self, string):
        tm = time.localtime()
        timestr = str(tm.tm_hour) + "시 " + str(tm.tm_min) + "분 " + str(tm.tm_sec) + "초"

        self.progressText.append("[" + timestr + "] " + string)

    def worker_start(self):
        self.worker.start()
        self.worker.working = True

    def worker_stop(self):
        self.worker.working = False

    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)

        infoLabel1 = QLabel('"설정 -> 음악 및 소리 -> 자막 표시" 을 "켜짐" 으로 바꿔주세요')
        infoLabel1.setStyleSheet("color: red;")

        captureButton = QPushButton("인식 범위 설정")
        captureButton.clicked.connect(self.select_area)

        self.progressText = QTextBrowser()

        startButton = QPushButton("시작")
        startButton.clicked.connect(self.worker_start)
        stopButton = QPushButton("중지")
        startButton.clicked.connect(self.worker_stop)

        self.fishingCounter = QLabel("낚시 횟수 : 0")

        grid.addWidget(infoLabel1, 0, 0, 1, 3)
        grid.addWidget(captureButton, 1, 0)
        grid.addWidget(self.progressText, 2, 0, 3, 3)
        grid.addWidget(startButton, 0, 4)
        grid.addWidget(stopButton, 1, 4)
        grid.addWidget(self.fishingCounter, 2, 4)
        grid.addWidget(QLabel("Auto Fishing\nMade by Hegel\nV1.0\n\n©2020 Hegel"), 4, 4)

        self.setWindowTitle('Auto Fishing')
        self.resize(600, 400)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
