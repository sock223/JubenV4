from PyQt5.QtWidgets import QApplication, QPushButton, QMessageBox, QLabel, QHBoxLayout, QTextEdit, QMainWindow, QDialog
from PyQt5.QtGui import QPixmap, QFont, QImage
from PyQt5.Qt import QLineEdit
from PyQt5.QtCore import pyqtSlot, QTimer, QUrl
import sys
import jieba
import re
from src import certainlyModel, faceModel as fm, actionModel, sms

import wave
import signal

signal.signal(signal.SIGCHLD, signal.SIG_IGN)
import cv2 as cv
import face_recognition
import os
import time
# import pyaudio
import threading

from NotImportant.test2 import *


# for pyinstaller
# import numpy.random.entropy
# import distutils
# import distutils.dist

class GameImg(QDialog):
    def __init__(self, path, type):
        QDialog.__init__(self)
        hbox = QHBoxLayout(self)
        lbl = QLabel(self)
        pixmap = QPixmap(path)  # 按指定路径找到图片，注意路径必须用双引号包围，不能用单引号
        lbl.setPixmap(pixmap)  # 在label上显示图片
        lbl.setScaledContents(True)  # 让图片自适应label大小
        hbox.addWidget(lbl)
        self.setLayout(hbox)
        self.move(300, 200)
        self.setWindowTitle(type)
        self.show()


class GameVideo(QWidget):
    VIDEO_TYPE_OFFLINE = 0
    VIDEO_TYPE_REAL_TIME = 1

    STATUS_INIT = 0
    STATUS_PLAYING = 1
    STATUS_PAUSE = 2

    video_url = ""

    def __init__(self, video_url="", video_type=VIDEO_TYPE_OFFLINE, auto_play=True):
        QWidget.__init__(self)
        self.video_url = video_url
        self.video_type = video_type  # 0: offline  1: realTime
        self.auto_play = auto_play
        self.status = self.STATUS_INIT  # 0: init 1:playing 2: pause

        # 组件展示
        self.pictureLabel = QLabel()
        init_image = QPixmap("../assets/images/no_video.jpeg").scaled(self.width(), self.height())
        self.pictureLabel.setPixmap(init_image)

        self.playButton = QPushButton()
        self.playButton.setEnabled(True)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.switch_video)

        control_box = QHBoxLayout()
        control_box.setContentsMargins(0, 0, 0, 0)
        control_box.addWidget(self.playButton)

        layout = QVBoxLayout()
        layout.addWidget(self.pictureLabel)
        layout.addLayout(control_box)
        # 调整位置
        self.move(200, 50)
        # 全屏
        # self.showFullScreen()
        self.setLayout(layout)

        # timer 设置
        self.timer = VideoTimer()
        self.timer.timeSignal.signal[str].connect(self.show_video_images)

        # video 初始设置
        self.playCapture = VideoCapture()
        if self.video_url != "":
            self.playCapture.open(self.video_url)
            fps = self.playCapture.get(CAP_PROP_FPS)
            self.timer.set_fps(fps)
            self.playCapture.release()
            if self.auto_play:
                self.switch_video()
            # self.videoWriter = VideoWriter('*.mp4', VideoWriter_fourcc('M', 'J', 'P', 'G'), self.fps, size)

    def reset(self):
        self.timer.stop()
        self.playCapture.release()
        self.status = VideoBox.STATUS_INIT
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def show_video_images(self):
        if self.playCapture.isOpened():
            success, frame = self.playCapture.read()
            if success:
                height, width = frame.shape[:2]
                if frame.ndim == 3:
                    rgb = cvtColor(frame, COLOR_BGR2RGB)
                elif frame.ndim == 2:
                    rgb = cvtColor(frame, COLOR_GRAY2BGR)

                temp_image = QImage(rgb.flatten(), width, height, QImage.Format_RGB888)
                temp_pixmap = QPixmap.fromImage(temp_image)
                self.pictureLabel.setPixmap(temp_pixmap)
            else:
                print("read failed, no frame data")
                success, frame = self.playCapture.read()
                if not success and self.video_type is VideoBox.VIDEO_TYPE_OFFLINE:
                    print("play finished")  # 判断本地文件播放完毕
                    self.reset()
                    self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
                return
        else:
            print("open file or capturing device error, init again")
            self.reset()

    def switch_video(self):
        if self.video_url == "" or self.video_url is None:
            return
        if self.status is VideoBox.STATUS_INIT:
            self.playCapture.open(self.video_url)
            self.timer.start()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        elif self.status is VideoBox.STATUS_PLAYING:
            self.timer.stop()
            if self.video_type is VideoBox.VIDEO_TYPE_REAL_TIME:
                self.playCapture.release()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        elif self.status is VideoBox.STATUS_PAUSE:
            if self.video_type is VideoBox.VIDEO_TYPE_REAL_TIME:
                self.playCapture.open(self.video_url)
            self.timer.start()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

        self.status = (VideoBox.STATUS_PLAYING,
                       VideoBox.STATUS_PAUSE,
                       VideoBox.STATUS_PLAYING)[self.status]


class Communicate(QObject):
    signal = pyqtSignal(str)


class VideoTimer(QThread):

    def __init__(self, frequent=20):
        QThread.__init__(self)
        self.stopped = False
        self.frequent = frequent
        self.timeSignal = Communicate()
        self.mutex = QMutex()

    def run(self):
        with QMutexLocker(self.mutex):
            self.stopped = False
        while True:
            if self.stopped:
                return
            self.timeSignal.signal.emit("1")
            time.sleep(1 / self.frequent)

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True

    def is_stopped(self):
        with QMutexLocker(self.mutex):
            return self.stopped

    def set_fps(self, fps):
        self.frequent = fps


class GameUi(QMainWindow):
    def __init__(self, game):
        # ui
        QMainWindow.__init__(self)
        # super().__init__()
        self.title = '《良辰吉日》'
        self.left = 10
        self.top = 10
        self.width = 1200
        self.height = 800
        self.font = QFont("宋体")
        self.pointsize = self.font.pointSize()
        self.font.setPixelSize(self.pointsize * 90 / 72)
        app.setFont(self.font)

        self.game = game
        self.child1 = None
        self.child2 = None
        self.child3 = None
        self.child4 = None
        self.child5 = None
        self.child6 = None
        self.child7 = None
        self.child8 = None
        self.child9 = None
        self.child10 = None
        self.child11 = None
        self.child12 = None
        self.child13 = None
        self.child14 = None
        self.child15 = None
        self.child16 = None
        self.imgList = [self.child1, self.child2, self.child3, self.child4, self.child5, self.child6, self.child7,
                        self.child8, self.child9, self.child10, self.child11, self.child12, self.child13, self.child14,
                        self.child15, self.child16]
        self.video = None
        self.map1 = None
        self.map2 = None
        self.specialMessage = None

        self.timer_camera1 = QTimer()  # 定义定时器，用于截取图片
        self.timer_camera2 = QTimer()  # 定义定时器，只显示图像

        # 初始化槽函数
        self.capturename = None
        self.timer_camera1.timeout.connect(lambda: self.show_camera(self.capturename, 'picCap'))
        self.timer_camera2.timeout.connect(lambda: self.show_camera(None, 'Play'))

        self.capturedNum = 3

        self.cap = cv.VideoCapture(0)  # 视频流

        self.cameraJustPlay()

        # self.displayTimer = QTimer()
        # self.displayStr = ""
        # self.displayTimer.timeout.connect(lambda :self.myPrint_delay(self.displayStr))

        self.currentVoicePath = None
        self.playVoice = QTimer()
        self.playVoice.timeout.connect(lambda: self.play(self.currentVoicePath))

    def delByName(self, name):
        directory = os.path.normpath('resources/image/img/' + name)
        for curdir, subdirs, files in os.walk(directory):
            # 删掉里面的照片
            for i in files:
                os.remove(curdir + '/' + i)

    def myPrint(self, sent):
        self.textbox2.setText(sent)

    # def myPrint_delay(self,sent):
    #     value = self.textbox2.toPlainText()
    #     if len(value) < len(sent):
    #         s = sent[0:len(value)+1]
    #         self.textbox2.setText(s)
    #     else:
    #         self.displayTimer.stop()

    def textbox2Clear(self):
        self.textbox2.setText("")

    def prestart(self, extra):
        unrecordList = self.game.getUnrecordList()

        # self.displayStr = extra + "请各位玩家依次录入人脸信息\n\n请输入角色名称，之后请看摄像头\n\n录入过程中，请确保身后没有其他玩家\n\n当前没有录入的玩家为:" + ' '.join(unrecordList)
        # self.textbox2Clear()
        # self.displayTimer.start(100)
        self.myPrint(
            extra + "请各位玩家依次录入人脸信息（捕捉图像时可能会有小的延迟卡顿，请等待）\n\n请输入角色名称，之后请看摄像头\n\n录入过程中，请确保身后没有其他玩家\n\n当前没有录入的玩家为:" + ' '.join(
                unrecordList))

    def initUI(self):
        str1 = "进入第1阶段(本阶段每位玩家可搜查2条线索，每位玩家的线索最多被取走2条)：本轮取证区域仅包括八名角色的随身物品，庭院区域在本轮取证中不开放\n" \
               "TIPS：玩家可以打字互动。所包含的功能如下：\n1）玩家可以搜查线索，例如：我想要搜查某个地方 \n2）玩家可以把自己的线索给别人，例如：我把23、24号线索给某人等\n" \
               "3）玩家可以结束本轮搜证进入，例如：进入下一轮搜证。\n4）本阶段，梁仁甫、武夫人、武仲文、柳眠、含烟均有一次调查洞房的机会，并可询问新娘梁嫣问题。"

        # self.textbox2Clear()
        # self.displayTimer.start(100)
        self.myPrint(str1)

        # self.currentVoicePath = 'resources/Sound/stage1.wav'
        # self.playVoice.start(1000)

        self.map1 = GameImg('resources/map/1.jpg', '公共线索：医馆地图')

    def window(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(40, 600)
        self.textbox.resize(750, 50)

        # create textbox2 (background)
        self.textbox2 = QTextEdit(self)
        self.textbox2.move(40, 40)
        self.textbox2.resize(350, 480)

        # Create a button in the window
        self.button = QPushButton('公共线索', self)
        self.button.move(850, 610)
        self.button.setStyleSheet("QPushButton{color:#e8f0de}"
                                  "QPushButton{outline:none}"
                                  "QPushButton{text-align:center}"
                                  "QPushButton{text-decoration:none}"
                                  "QPushButton{padding:.35em 1em .55em}"
                                  "QPushButton{background:#64991e}"
                                  "QPushButton{border:solid 1px #538312}"
                                  "QPushButton:hover{text-decoration:none}"
                                  "QPushButton:hover{background:#538018;}"
                                  "QPushButton{border-radius:15px;}"
                                  )
        self.button.resize(110, 30)

        self.button2 = QPushButton('提问新娘', self)
        self.button2.move(850, 670)
        self.button2.setStyleSheet("QPushButton{color:#e8f0de}"
                                   "QPushButton{outline:none}"
                                   "QPushButton{text-align:center}"
                                   "QPushButton{text-decoration:none}"
                                   "QPushButton{padding:.35em 1em .55em}"
                                   "QPushButton{background:#64991e}"
                                   "QPushButton{border:solid 1px #538312}"
                                   "QPushButton:hover{text-decoration:none}"
                                   "QPushButton:hover{background:#538018;}"
                                   "QPushButton{border-radius:15px;}"
                                   )
        self.button2.resize(110, 30)

        self.button3 = QPushButton('武夫人事件', self)
        self.button3.move(970, 610)
        self.button3.setStyleSheet("QPushButton{color:#e8f0de}"
                                   "QPushButton{outline:none}"
                                   "QPushButton{text-align:center}"
                                   "QPushButton{text-decoration:none}"
                                   "QPushButton{padding:.35em 1em .55em}"
                                   "QPushButton{background:#64991e}"
                                   "QPushButton{border:solid 1px #538312}"
                                   "QPushButton:hover{text-decoration:none}"
                                   "QPushButton:hover{background:#538018;}"
                                   "QPushButton{border-radius:15px;}"
                                   )
        self.button3.resize(110, 30)


        self.label_show_camera = QLabel(self)  # 定义显示视频的Label
        self.label_show_camera.move(480, 40)
        self.label_show_camera.setFixedSize(641, 481)  # 给显示视频的Label设置大小为641x481

        # connect button to function on_click
        self.button.clicked.connect(self.showPublicMessage)
        self.button2.clicked.connect(self.askBride)
        self.button3.clicked.connect(self.cook)
        self.show()

    def closeProgram(self):
        self.close()

    def windowResize(self):
        self.textbox2.move(130, 40)
        self.textbox2.resize(900, 480)
        self.textbox.move(130, 600)
        self.textbox.resize(750, 50)
        self.button.move(900, 610)
        self.button2.move(900, 670)
        self.button3.move(1020, 610)

    def showPublicMessage(self):
        self.map1 = GameImg('resources/map/1.jpg', '公共线索：医馆地图')

    def cook(self):
        if self.game.find_peifang:
            value, ok = QInputDialog.getText(self, "武夫人公共事件", "武夫人是否按照配方烹饪此药膳:", QLineEdit.Normal, "")
            name = self.game.detectFace()
            if name == 'wfr':
                r = self.game.cm.predictCertainly(value)
                if r == 'true':
                    QMessageBox.question(self, 'Message', '药膳中飘出了一股异香',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.game.specialEventforWFR2()
                else:
                    print('不烹饪')
            else:
                QMessageBox.question(self, 'Message', '只能由武夫人触发此事件',
                                     QMessageBox.Ok, QMessageBox.Ok)
        else:
            QMessageBox.question(self, 'Message', '尚未触发',
                                 QMessageBox.Ok, QMessageBox.Ok)
    def askBride(self):
        if self.game.getCurrentStage() == 1 or self.game.getCurrentStage() == 2:
            name = self.game.detectFace()

            # 已经进去过了
            if name in ['lrf', 'wfr', 'wzw', 'lm', 'hy'] and self.game.enter_chamber[name] and not self.game.asked[
                name]:
                # 第三个参数表示显示类型，可选，有正常（QLineEdit.Normal）、密碼（ QLineEdit. Password）、不显示（ QLineEdit. NoEcho）三种情况
                value, ok = QInputDialog.getText(self, "提出你的问题", "请输入想问新娘的问题:", QLineEdit.Normal, "")

                if '有毒' in value or '不喝' in value or '没喝' in value or '没中毒' in value or ('酒' in value and '毒' in value):
                    self.game.asked[name] = True
                    QMessageBox.question(self, 'Message', '三年前，母亲暴病去世，自那以后我便自学了医术，天幸如此，我才能在喝酒时，发现酒中异样。',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.game.specialEventforanswer1(name)

                elif ('谁' in value and '倒' in value) or '倒酒' in value or (
                        '谁' in value and '给' in value and '酒' in value) or ('到' in value and '酒' in value):
                    self.game.asked[name] = True
                    QMessageBox.question(self, 'Message', '我的贴身侍女含烟',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.game.specialEventforanswer2(name)

                elif name == 'lm' and ('绝情' in value or '恩断义绝' in value or '断绝' in value or '绝交' in value):
                    self.game.asked[name] = True
                    QMessageBox.question(self, 'Message', '我从没给你写过什么绝情书，明明是你给我写了一封绝情信',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.game.specialEventforanswer3(name)


                else:
                    QMessageBox.question(self, 'Message', '你问的这个问题，我不清楚。',
                                         QMessageBox.Ok, QMessageBox.Ok)
            else:
                QMessageBox.question(self, 'Message', '请先进入洞房调查，或您已问过一个问题了，无法继续询问。',
                                     QMessageBox.Ok, QMessageBox.Ok)
        else:
            QMessageBox.question(self, 'Message', "新娘现在懒得理你们！",
                                 QMessageBox.Ok, QMessageBox.Ok)

    def show_camera(self, name, method):
        # print('name:',name,'method:',method)
        # 30毫秒一针
        flag, self.image = self.cap.read()  # 从视频流中读取
        # print("self.image",self.image)
        if self.image is not None:
            show = cv.resize(self.image, (640, 480))  # 把读到的帧的大小重新设置为 640x480
            show = cv.cvtColor(show, cv.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
            showImage = QImage(show.data, show.shape[1], show.shape[0],
                               QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
            self.label_show_camera.setPixmap(QPixmap.fromImage(showImage))  # 往显示视频的Label里 显示QImage
            if method == 'picCap' and name is not None:
                print('name:', name, 'method:', method)
                return self.picCap(name, self.image)
            elif method == 'predict':
                pass

    def open_camera_picCap(self, name):
        if self.timer_camera2.isActive():
            self.timer_camera2.stop()
        time.sleep(0.1)
        self.capturename = name
        # self.timer_camera1.timeout.connect(lambda: self.show_camera(name, 'picCap'))
        # 初始化 已录制张数
        self.capturedNum = 0
        self.timer_camera1.start(100)

    def cameraJustPlay(self):
        if self.timer_camera1.isActive():
            self.timer_camera1.stop()
        time.sleep(0.1)
        self.capturename = None
        self.timer_camera2.start(30)

    def close_camera(self):
        self.timer_camera1.stop()  # 关闭定时器
        self.timer_camera2.stop()  # 关闭定时器
        self.cap.release()  # 释放视频流
        self.label_show_camera.clear()  # 清空视频显示区域

    def picCap(self, name, image):
        print("picCap:", name)
        self.savePath = 'resources/image/img/'
        print("请将脸放入摄像头范围，稍微动一动")
        if self.capturedNum <= 1:
            faces = face_recognition.face_locations(image)
            print(faces)
            if len(faces) == 1:
                self.capturedNum += 1
                cv.imwrite(self.savePath + '/' + name + '/' + str(self.capturedNum) + '.jpg',
                           image)
                time.sleep(0.5)
        elif self.capturedNum == 2:
            faces = face_recognition.face_locations(image)
            print(faces)
            if len(faces) == 1:

                self.capturedNum += 1
                cv.imwrite(self.savePath + '/' + name + '/' + str(self.capturedNum) + '.jpg',
                           image)
                # self.close_camera()
                words = 'false'
                directory = os.path.normpath('resources/image/img/' + name)
                for curdir2, subdirs2, files2 in os.walk(directory):
                    if len(files2) > 2:
                        self.game.recordFace[name] = True
                        words = 'done'
                    else:
                        self.game.recordFace[name] = False
                        words = 'false'
                if words == 'false':
                    QMessageBox.question(self, 'Message', '录入失败',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.prestart('')
                    self.cameraJustPlay()
                elif words == 'done':
                    unrecordList = self.game.getUnrecordList()
                    if len(unrecordList) > 0:
                        QMessageBox.question(self, 'Message', '录入成功',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.prestart('')
                        self.cameraJustPlay()
                    else:
                        # self.displayTimer.timeout.connect(lambda: self.myPrint("人脸模型计算中..."))
                        # self.displayTimer.start(100)
                        self.myPrint("人脸模型计算中...")
                        self.game.fr.trainModel()
                        self.game.nextStage()
                        self.close_camera()
                        self.windowResize()
                        QMessageBox.question(self, 'Message', '计算完毕，准备工作完毕',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        str1 = "时维大唐开元十一年，圣天子李隆基宽和仁厚，勤政爱民，在其治下，九州清河海晏，宇内升平，中华已渐显盛世气象\n" \
                               "在岭南广州城外的白云山上，花木掩映之中，曲径通幽之处，有一座精巧的宅院。宅院的主人，是巢国公武攸绪的长孙武仲文。\n" \
                               "昔年，大周女皇武氏族裔也曾列土封疆，煊赫天下，然而移世易，武姓一族或因开罪女皇而削爵贬黜（如武则天之族兄武惟良，被贬为蝮姓），或因中宗复位而惨遭屠戮，传至今日，只有巢国公武攸绪一脉还保有爵位\n" \
                               "今日，是九月初三，往日清净的武府鼓乐喧天，宾客盈门，只因当家的少主武仲文要在午时迎娶岭南首富的千金梁嫣。我们的故事，便在此时拉开了序幕" \
                               "\n-----------所有玩家阅读背景故事，读到'拜堂前，请不要翻开下一页'，便可开启第一幕微型剧目-----------\n微型剧目完成后，请告诉我是否触发之后的剧情？"
                        self.myPrint(str1)
                        # self.displayStr = "请问是否开始游戏？"
                        # self.textbox2Clear()
                        # self.displayTimer.start(100)
        else:
            pass

    def keyPressEvent(self, event):
        if str(event.key()) == '16777220':  # 回车
            self.on_click()

    @pyqtSlot()
    def on_click(self):
        self.clearScreen()
        textboxValue = self.textbox.text()

        stage = self.game.getCurrentStage()

        if stage == -1:

            QMessageBox.question(self, 'Message', '录入过程中，请确保摄像头范围没有其他玩家',
                                 QMessageBox.Ok, QMessageBox.Ok)

            name = self.game.findName(textboxValue)
            if name == 'vague':
                self.myPrint("抱歉，无法识别您输入的角色名称,请重新输入")
                self.textbox.setText('')
                return

            # 判断采集是否成功 成功截图数是否够。

            directory = os.path.normpath('resources/image/img/' + name)
            for curdir, subdirs, files in os.walk(directory):
                if len(files) > 1:
                    # exist
                    reply = QMessageBox.question(self, 'Message', '已经录入过您的人脸信息，是否重新录入\n\n录入过程中，请确保摄像头范围内没有其他玩家',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    if reply == QMessageBox.Yes:
                        # 删掉之前的照片
                        self.delByName(name)
                        self.open_camera_picCap(name)
                    else:
                        self.prestart('')
                else:
                    # 删掉之前的照片
                    self.delByName(name)
                    self.open_camera_picCap(name)

        elif stage == 0:
            r = self.game.cm.predictCertainly(textboxValue)
            if r == 'true':
                self.initUI()
                self.game.nextStage()
            else:
                if r == 'vague':
                    if self.game.am.predictAction(textboxValue) == 'start':
                        self.initUI()
                        self.game.nextStage()
                if self.game.getStartTimes() == 0 or self.game.getStartTimes() == 1:
                    str1 = "时维大唐开元十一年，圣天子李隆基宽和仁厚，勤政爱民，在其治下，九州清河海晏，宇内升平，中华已渐显盛世气象\n" \
                           "在岭南广州城外的白云山上，花木掩映之中，曲径通幽之处，有一座精巧的宅院。宅院的主人，是巢国公武攸绪的长孙武仲文。\n" \
                           "昔年，大周女皇武氏族裔也曾列土封疆，煊赫天下，然而移世易，武姓一族或因开罪女皇而削爵贬黜（如武则天之族兄武惟良，被贬为蝮姓），或因中宗复位而惨遭屠戮，传至今日，只有巢国公武攸绪一脉还保有爵位\n" \
                           "今日，是九月初三，往日清净的武府鼓乐喧天，宾客盈门，只因当家的少主武仲文要在午时迎娶岭南首富的千金梁嫣。我们的故事，便在此时拉开了序幕" \
                           "\n-----------所有玩家阅读背景故事，读到'拜堂前，请不要翻开下一页'，便可开启第一幕微型剧目-----------\n微型剧目完成后，请告诉我是否触发之后的剧情？"
                    self.myPrint(str1)
                    self.game.increaseStartTimes()

                elif self.game.getStartTimes() >= 2:
                    # self.myPrint('不等了，不等了，我们还是开始吧！\n')
                    self.initUI()
                    self.game.nextStage()

        elif stage <= 2 and stage > 0:
            name = self.game.detectFace()

            # 发动 岐黄 技能
            if name=='wfr' and '岐黄' in textboxValue and stage == 2:
                n = self.game.findNum2(textboxValue)
                if len(n) == 0:
                    QMessageBox.question(self, 'Message',
                                         '请以 岐黄+序号 的方式发动技能',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.myPrint("当前为第" + str(
                        self.game.getCurrentStage()) + "阶段搜证\n" + "请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                    self.textbox.setText('')
                    return
                p = '../juben/resources/Message/' + n[0] + '.jpg'
                if p in self.game.nameDict[name]:
                    if n[0] == '7':
                        QMessageBox.question(self, 'Message', '这是摄魂汤的配方，摄魂汤是一剂治疗离魂症的良药，而离魂症是指人在受到强烈的刺激时，三魂七魄中的二魂六魄离体飞去，躯体里只留存了一魂一魄，因而从此成为疯癫之人',
                                         QMessageBox.Ok, QMessageBox.Ok)
                        self.game.specialEventforQIHUANG()
                        self.myPrint("当前为第" + str(
                            self.game.getCurrentStage()) + "阶段搜证\n" + "请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    else:
                        QMessageBox.question(self, 'Message', '无法鉴定。',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第" + str(
                            self.game.getCurrentStage()) + "阶段搜证\n" + "请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                else:
                    QMessageBox.question(self, 'Message', '你没有那条线索!',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.myPrint("当前为第" + str(
                        self.game.getCurrentStage()) + "阶段搜证\n" + "请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                    self.textbox.setText('')
                    return


            # 如果是赠与的动作，那么就赠与
            if self.game.giveMethod(name, textboxValue) == 'noMessage':
                QMessageBox.question(self, 'Message', '你没有那条线索!',
                                     QMessageBox.Ok, QMessageBox.Ok)
                self.myPrint("当前为第" + str(
                    self.game.getCurrentStage()) + "阶段搜证\n" + "请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                self.textbox.setText('')
                return
            elif self.game.giveMethod(name, textboxValue):
                QMessageBox.question(self, 'Message', '已经转交!',
                                     QMessageBox.Ok, QMessageBox.Ok)
                self.myPrint("当前为第" + str(
                    self.game.getCurrentStage()) + "阶段搜证\n" + "请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                self.textbox.setText('')
                return

            text, searchDict = self.game.predictAction(textboxValue)
            print(text, searchDict)
            if text == 'own':
                self.myPrint('你好' + self.game.getChineseName(name))
                ownlist = self.game.ownMessage(name)
                if len(ownlist) > 0 and type(ownlist) is list:
                    for i in range(len(ownlist)):
                        p = self.game.findNum2(ownlist[i])
                        if len(p) > 0:
                            self.imgList[i] = GameImg(ownlist[i], p[0])
                    self.myPrint("当前为第" + str(
                        self.game.getCurrentStage()) + "阶段搜证\n" + '显示多条线索有重叠情况，请自行拖动一下\n请告诉我还想做些什么?\n\n' + self.game.getLeftMessage())
                else:
                    QMessageBox.question(self, 'Message', '您尚未拥有线索',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.myPrint("当前为第" + str(
                        self.game.getCurrentStage()) + "阶段搜证\n" + '想做些什么请直接告诉我\n\n' + self.game.getLeftMessage())

            elif text == 'searchNoNum':
                # self.myPrint('请告诉我你想要搜查的线索数量\n')
                searchDict['num'] = [1]
                if name == searchDict.get('place'):
                    QMessageBox.question(self, 'Message', '无法搜查自己的线索，天啦撸，你是凶手吧？竟然想搜自己！',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.myPrint("当前为第" + str(
                        self.game.getCurrentStage()) + "阶段搜证\n" + "请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                else:
                    self.myPrint('你好' + self.game.getChineseName(name))
                    words, searchList = self.game.doSearch(searchDict, name)
                    s = ''
                    if len(searchList) > 0:
                        s = '千万别忘记离开时关掉自己的线索，以免被别的玩家看到\n\n'
                        for i in range(len(searchList)):
                            p = self.game.findNum2(searchList[i])
                            self.imgList[i] = GameImg(searchList[i],
                                                      p[0])
                    if words is not None:
                        QMessageBox.question(self, 'Message', words,
                                             QMessageBox.Ok, QMessageBox.Ok)
                    self.myPrint("当前为第" + str(self.game.getCurrentStage()) + "阶段搜证\n" + s + self.game.getLeftMessage())


            elif text == 'search':
                # 判断是否为深入调查
                if name == searchDict.get('place'):
                    QMessageBox.question(self, 'Message', '无法搜查自己的线索，天啦撸，你是凶手吧？竟然想搜自己！',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.myPrint("当前为第" + str(
                        self.game.getCurrentStage()) + "阶段搜证\n" + "请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                else:
                    self.myPrint('你好' + self.game.getChineseName(name))
                    words, searchList = self.game.doSearch(searchDict, name)
                    s = ''
                    if len(searchList) > 0:
                        s = '显示多条线索有重叠情况，请自行拖动一下\n\n另外千万别忘记离开时关掉自己的线索，以免被别的玩家看到\n\n'
                        for i in range(len(searchList)):
                            p = self.game.findNum2(searchList[i])
                            self.imgList[i] = GameImg(searchList[i], p[0])
                    if words is not None:
                        QMessageBox.question(self, 'Message', words,
                                             QMessageBox.Ok, QMessageBox.Ok)
                    self.myPrint("当前为第" + str(self.game.getCurrentStage()) + "阶段搜证\n" + s + self.game.getLeftMessage())
            elif text == 'vague':
                self.myPrint(
                    '抱歉，没能识别您说的话，请换种方式试试\n' + self.game.getLeftMessage())

            elif text == 'searchNoPerson':
                QMessageBox.question(self, 'Message', '如果想要搜查，请试试：搜查+人名',
                                     QMessageBox.Ok, QMessageBox.Ok)
                self.myPrint("当前为第" + str(self.game.getCurrentStage()) + "阶段搜证\n" + self.game.getLeftMessage())

            elif text == 'next':

                if stage < 2:
                    reply = QMessageBox.question(self, 'Message', '确认进入下个阶段？若进入下个阶段，所有玩家此轮搜查结束，可搜查的线索数也会更新',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                else:
                    reply = QMessageBox.question(self, 'Message', '下个阶段为结案阶段，结案阶段无法继续搜查，且无法返回，请问是否进入结案阶段？',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                if reply == QMessageBox.Yes:
                    self.game.nextStage()
                    if self.game.getCurrentStage() == 2:
                        self.game.resetEnable()
                        str1 = '进入第2阶段(本阶段每位玩家可搜查3条线索)：请各位玩家翻开下一页，阅读亥时发生的事，当所有玩家阅读完亥时剧本后，开始第二幕微型剧目' \
                               'TIPS：1）若误操作进入此阶段，请输入"返回上一阶段"\n2）玩家可以搜查线索，例如：我想要搜查某个地方 \n3）玩家可以把自己的线索给别人，例如：我把23、24号线索给某人等\n' \
                               '4）玩家可以结束本轮搜证，进入投票阶段。例如：进入下一轮。\n5）本轮每位玩家可以搜查3条线索。\n6）请玩家注意《易镜玄要》以及武府的风水格局\n7）武夫人可输入 岐黄+线索编号 来使用岐黄技能。\n'
                        self.myPrint(str1)
                        # self.currentVoicePath = 'resources/Sound/stage2.wav'
                        # self.playVoice.start(1000)
                    elif self.game.getCurrentStage() == 3:
                        self.game.resetEnable()
                        self.myPrint('进入结案阶段：请讨论后回答给梁嫣杯中下毒的凶手是谁？')
                        # self.currentVoicePath = 'resources/Sound/stage3.wav'
                        # self.playVoice.start(1000)
                else:
                    self.myPrint('没想好就再等等吧。想做什么可以直接跟我说\n\n' + self.game.getLeftMessage())
            elif text == 'previous':
                reply = QMessageBox.question(self, 'Message', '确认返回上个阶段？',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                if reply == QMessageBox.Yes:
                    if self.game.getEnable():
                        self.game.previousStage()
                        QMessageBox.question(self, 'Message', '所有玩家已经返回上一阶段',
                                             QMessageBox.Ok, QMessageBox.Ok)

                        self.myPrint("请告诉我想要做的事情，当前为第" + str(
                            self.game.getCurrentStage()) + "阶段搜证 \n\n" + self.game.getLeftMessage())
                    else:
                        QMessageBox.question(self, 'Message',
                                             '本轮已有玩家搜查，无法返回，看来你们只能硬着头皮继续搜了',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint(self.game.getLeftMessage())
                else:
                    self.myPrint('既然不进行下一阶段，那么还想做些什么可以跟我讲\n\n' + self.game.getLeftMessage())


        elif stage == 3:
            if len(self.game.answerList) == 0:
                self.game.answerList.append(textboxValue)
                self.myPrint('请讨论后回答玩家中有几个鬼魂')
            elif len(self.game.answerList) == 1:
                self.game.answerList.append(textboxValue)
                self.myPrint('请讨论后回答玩家各自死因是什么，凶手是谁')
            elif len(self.game.answerList) == 2:
                self.game.answerList.append(textboxValue)
                self.myPrint('请讨论后回答玩家的鬼魂为何被困在武府中')
            elif len(self.game.answerList) == 3:
                self.game.answerList.append(textboxValue)
                self.myPrint('请各位自行复盘，因为我也没看故事真相。。 那么是否进入复盘阶段？')
                self.game.nextStage()
                print(self.game.answerList)


        elif stage == 4:
            r = self.game.cm.predictCertainly(textboxValue)
            if r == 'true':
                words = self.game.review()
                self.myPrint(words)
                # self.currentVoicePath = 'resources/Sound/review.wav'
                # self.playVoice.start(1000)
            else:
                self.myPrint("准备好进入复盘阶段请告诉我")

        self.textbox.setText('')


    def clearScreen(self):
        self.textbox2.setText('')


class GameLogic():
    def __init__(self):

        # params
        jieba.load_userdict("src/myWords.txt")

        self.recordFace = {'hy': True,
                           'jxz': True,
                           'lm': False,
                           'lrf': True,
                           'wfr': True,
                           'wzw': True,
                           'mx': True,
                           'ysq': True
                           }

        self.startTimes = 0

        self.MeanDict = {0: 'clear',
                         1: 'vague'}

        # 初始阶段
        self.currentMessage = {'hy': 1, 'jxz': 5, 'lrf': 8, 'lm': 12, 'mx': 16, 'ty': 20, 'wfr': 29, 'wzw': 33,
                               'ysq': 37}

        # 获得的线索列表
        self.hy = []
        self.jxz = []
        self.lm = []
        self.lrf = []
        self.wfr = []
        self.wzw = []
        self.mx = []
        self.ysq = []
        self.nameDict = {'hy': self.hy,
                         'jxz': self.jxz,
                         'lm': self.lm,
                         'lrf': self.lrf,
                         'wfr': self.wfr,
                         'wzw': self.wzw,
                         'mx': self.mx,
                         'ysq': self.ysq
                         }

        # 匹配几条线索的 正则
        self.xs = re.compile(r'.*([0-9]+).*?线索')
        # # 游戏存档
        # self.dictSave = {}
        # 当前状态是否可以退回
        self.enable = True

        self.nameMap = {'hy': '含烟',
                        'jxz': '静虚子',
                        'lm': '柳眠',
                        'lrf': '梁仁甫',
                        'wfr': '武夫人',
                        'wzw': '武仲文',
                        'mx': '妙玄',
                        'ysq': '殷思齐'
                        }

        self.messageLeft1 = {'hy': 2, 'jxz': 2, 'lm': 2, 'lrf': 2, 'wfr': 2, 'wzw': 2, 'mx': 2, 'ysq': 2}
        self.messageLeft2 = {'hy': 3, 'jxz': 3, 'lm': 3, 'lrf': 3, 'wfr': 3, 'wzw': 3, 'mx': 3, 'ysq': 3}

        self.maxMessage1 = {'hy': 2,
                            'jxz': 6,
                            'lm': 13,
                            'lrf': 9,
                            'wfr': 30,
                            'wzw': 34,
                            'mx': 17,
                            'ysq': 38,
                            'ty': 0}

        self.maxMessage2 = {'hy': 4,
                            'jxz': 7,
                            'lm': 15,
                            'lrf': 11,
                            'wfr': 32,
                            'wzw': 36,
                            'mx': 19,
                            'ysq': 40,
                            'ty': 28}
        self.enter_chamber = {
            'lrf': False,
            'wfr': False,
            'wzw': False,
            'lm': False,
            'hy': False
        }
        self.asked = {
            'lrf': False,
            'wfr': False,
            'wzw': False,
            'lm': False,
            'hy': False
        }

        self.voted = {'hy': 0, 'jxz': 0, 'lm': 0, 'lrf': 0, 'wfr': 0, 'wzw': 0, 'mx': 0, 'ysq': 0}
        self.doVote = {'hy': None, 'jxz': None, 'lm': None, 'lrf': None, 'wfr': None, 'wzw': None, 'mx': None,
                       'ysq': None}

        self.currentStage = -1

        self.is_special = False

        self.find_peifang = False
        # model
        # 初始化模型
        self.fr = fm.FaceRecognition()
        self.cm = certainlyModel.CertainlyModel()
        self.am = actionModel.ActionModel()
        self.sm = sms.Sms()

        self.giveDict = ['给', '交', '赠与']

        self.answerList = []


    def specialEventforLM(self):
        self.sm.sendMs('lm', 'special')
        self.sm.sendMs('hy', 'special2')
        self.sm.sendMs('jxz', 'special2')
        self.sm.sendMs('lrf', 'special2')
        self.sm.sendMs('wfr', 'special2')
        self.sm.sendMs('wzw', 'special2')
        self.sm.sendMs('mx', 'special2')
        self.sm.sendMs('ysq', 'special2')

    def specialEventforWFR(self):
        self.sm.sendMs('lm', 'special3')
        self.sm.sendMs('hy', 'special3')
        self.sm.sendMs('jxz', 'special3')
        self.sm.sendMs('lrf', 'special3')
        self.sm.sendMs('wfr', 'special3')
        self.sm.sendMs('wzw', 'special3')
        self.sm.sendMs('mx', 'special3')
        self.sm.sendMs('ysq', 'special3')

    def specialEventforWFR2(self):
        self.sm.sendMs('lm', 'special4')
        self.sm.sendMs('hy', 'special4')
        self.sm.sendMs('jxz', 'special4')
        self.sm.sendMs('lrf', 'special4')
        self.sm.sendMs('wfr', 'special4')
        self.sm.sendMs('wzw', 'special4')
        self.sm.sendMs('mx', 'special4')
        self.sm.sendMs('ysq', 'special4')

    def specialEventforQIHUANG(self):
        self.sm.sendMs('wfr', 'special5')

    def specialEventforanswer1(self,name):
        self.sm.sendMs(name, 'special6')

    def specialEventforanswer2(self,name):
        self.sm.sendMs(name, 'special7')

    def specialEventforanswer3(self,name):
        self.sm.sendMs(name, 'special8')

    def getStartTimes(self):
        return self.startTimes

    def increaseStartTimes(self):
        self.startTimes += 1

    def getUnrecordList(self):
        return [self.nameMap[k] for k, v in self.recordFace.items() if not v]

    def resetEnable(self):
        self.enable = True

    def getEnable(self):
        return self.enable

    def getCurrentStage(self):
        return self.currentStage

    def nextStage(self):
        self.currentStage += 1
        if self.currentStage == 2 and not self.is_special:
            self.specialEventforLM()
            self.is_special = True

    def previousStage(self):
        self.currentStage -= 1

    def findPlace(self, sent):
        if '烟' in sent or '含' in sent:
            return 'hy'
        elif '虚' in sent or '静' in sent:
            return 'jxz'
        elif '梁' in sent or '仁' in sent:
            return 'lrf'
        elif '柳' in sent or '眠' in sent:
            return 'lm'
        elif '妙' in sent or '玄' in sent:
            return 'mx'
        elif '夫人' in sent:
            return 'wfr'
        elif '仲' in sent or '文' in sent:
            return 'wzw'
        elif '殷' in sent or '思齐' in sent:
            return 'ysq'
        elif '庭' in sent or '院' in sent:
            return 'ty'
        elif '洞房' in sent or '酒' in sent or '杯' in sent:
            return 'df'
        else:
            return 'vague'

    def findName(self, sent):
        if '烟' in sent or '含' in sent:
            return 'hy'
        elif '虚' in sent or '静' in sent:
            return 'jxz'
        elif '梁' in sent or '仁' in sent:
            return 'lrf'
        elif '柳' in sent or '眠' in sent:
            return 'lm'
        elif '妙' in sent or '玄' in sent:
            return 'mx'
        elif '夫人' in sent:
            return 'wfr'
        elif '仲' in sent or '文' in sent:
            return 'wzw'
        elif '殷' in sent or '思齐' in sent:
            return 'ysq'
        else:
            return 'vague'

    def getChineseName(self, name):
        return self.nameMap.get(name)

    # 用于找调查的线索数量，单个数字
    def findNum(self, sent):
        sent = sent.replace('一', '1')
        sent = sent.replace('壹', '1')

        sent = sent.replace('二', '2')
        sent = sent.replace('两', '2')
        sent = sent.replace('贰', '2')

        sent = sent.replace('三', '3')
        sent = sent.replace('仨', '3')
        sent = sent.replace('叁', '3')

        sent = sent.replace('四', '4')
        sent = sent.replace('肆', '4')

        sent = sent.replace('五', '5')
        sent = sent.replace('伍', '5')

        sent = sent.replace('六', '6')
        sent = sent.replace('陆', '6')

        sent = sent.replace('七', '7')
        sent = sent.replace('柒', '7')

        sent = sent.replace('八', '8')
        sent = sent.replace('捌', '8')

        sent = sent.replace('九', '9')
        sent = sent.replace('玖', '9')

        sent = sent.replace('零', '0')

        sent = sent + "线索"
        return self.xs.findall(sent)

    # 用于找线索号码
    def findNum2(self, sent):
        sent = sent.replace('一', '1')
        sent = sent.replace('壹', '1')

        sent = sent.replace('二', '2')
        sent = sent.replace('两', '2')
        sent = sent.replace('贰', '2')

        sent = sent.replace('三', '3')
        sent = sent.replace('仨', '3')
        sent = sent.replace('叁', '3')

        sent = sent.replace('四', '4')
        sent = sent.replace('肆', '4')

        sent = sent.replace('五', '5')
        sent = sent.replace('伍', '5')

        sent = sent.replace('六', '6')
        sent = sent.replace('陆', '6')

        sent = sent.replace('七', '7')
        sent = sent.replace('柒', '7')

        sent = sent.replace('八', '8')
        sent = sent.replace('捌', '8')

        sent = sent.replace('九', '9')
        sent = sent.replace('玖', '9')

        sent = sent.replace('零', '0')
        self.xs2 = re.compile(r'[0-9]+')

        return self.xs2.findall(sent)

    # 用于给卡片（赠与卡片）
    def giveMethod(self, giveName, sent):
        givenName = None
        nums = None
        for i in self.giveDict:
            if i in sent:
                arr = sent.split(i)
                for j in arr:
                    # 这半句话找到了赠与的人
                    if self.findName(j) != 'vague':
                        givenName = self.findName(j)
                    # 这半句话找到了 交易的卡片号
                    if len(self.findNum2(j)) > 0:
                        nums = self.findNum2(j)
                if givenName is not None and nums is not None:
                    # return name,nums
                    for n in nums:
                        path = '../juben/resources/Message/' + n + '.jpg'
                        # 如果给的人有该条线索
                        if path in self.nameDict[giveName]:
                            # 将该卡片从给的人的线索中移出
                            self.nameDict[giveName].remove(path)
                            # 加入被给的人的线索中
                            self.nameDict[givenName].append(path)
                            self.sm.sendMs(givenName, path)
                        else:
                            return "noMessage"
                    # 完成了给的操作
                    return True
                else:
                    givenName = None
                    nums = None
        # 虽然有给，但是意义不明
        return False

    def findKillerList(self):
        killerList = []
        voteNum = 0
        for key, value in self.voted.items():
            if value > voteNum:
                killerList = []
                killerList.append(key)
                voteNum = value
            elif value == voteNum:
                killerList.append(key)
            else:
                continue
        return killerList

    def getLeftMessage(self):
        if self.getCurrentStage() == 0:
            return "所有玩家阅读背景故事，读到'拜堂前，请不要翻开下一页'，并完成第一幕微型剧目，可告诉我'进行下一阶段'"
        if self.getCurrentStage() == 1:
            words = "当前剩余线索:\n" + " 含烟：%d 条\n 静虚子：%d 条\n 梁仁甫：%d 条\n 柳眠：%d 条\n 妙玄：%d 条\n 武夫人：%d 条\n 武仲文：%d 条\n 殷思齐：%d 条\n" % (
                (self.maxMessage1['hy'] - self.currentMessage['hy'] + 1),
                (self.maxMessage1['jxz'] - self.currentMessage['jxz'] + 1),
                (self.maxMessage1['lrf'] - self.currentMessage['lrf'] + 1),
                (self.maxMessage1['lm'] - self.currentMessage['lm'] + 1),
                (self.maxMessage1['mx'] - self.currentMessage['mx'] + 1),
                (self.maxMessage1['wfr'] - self.currentMessage['wfr'] + 1),
                (self.maxMessage1['wzw'] - self.currentMessage['wzw'] + 1),
                (self.maxMessage1['ysq'] - self.currentMessage['ysq'] + 1))
            words += "\nTIPS：玩家可以打字互动。所包含的功能如下：\n1）玩家可以搜查线索，例如：我想要搜查某个地方 \n2）玩家可以把自己的线索给别人，例如：我把23、24号线索给某人等\n" \
                     "3）玩家可以结束本轮搜证。例如：进入下一轮。\n4）第一轮搜证每位玩家可以搜查2条线索"
            return words
        elif self.getCurrentStage() == 2:
            words = "当前剩余线索:\n" + "  含烟：%d 条\n 静虚子：%d 条\n 梁仁甫：%d 条\n 柳眠：%d 条\n 妙玄：%d 条\n 武夫人：%d 条\n 武仲文：%d 条\n 殷思齐：%d 条\n 庭院：%d 条\n" % (
                (self.maxMessage2['hy'] - self.currentMessage['hy'] + 1),
                (self.maxMessage2['jxz'] - self.currentMessage['jxz'] + 1),
                (self.maxMessage2['lrf'] - self.currentMessage['lrf'] + 1),
                (self.maxMessage2['lm'] - self.currentMessage['lm'] + 1),
                (self.maxMessage2['mx'] - self.currentMessage['mx'] + 1),
                (self.maxMessage2['wfr'] - self.currentMessage['wfr'] + 1),
                (self.maxMessage2['wzw'] - self.currentMessage['wzw'] + 1),
                (self.maxMessage2['ysq'] - self.currentMessage['ysq'] + 1),
                (self.maxMessage2['ty'] - self.currentMessage['ty'] + 1))
            words += "\nTIPS：玩家可以打字互动。所包含的功能如下：\n1）玩家可以搜查线索，例如：我想要搜查某个地方 \n2）玩家可以把自己的线索给别人，例如：我把23、24号线索给某人等\n" \
                     "3）玩家可以结束本轮搜证。例如：进入下一轮。\n4）第二轮每位玩家可以搜查3条线索。\n6）请玩家注意《易镜玄要》以及武府的风水格局\n7）武夫人可输入 岐黄+线索编号 来使用岐黄技能。\n"
            return words

    def ownMessage(self, name):
        ownList = []
        if len(self.nameDict[name]) == 0:
            return "您尚未拥有线索"
        else:
            for i in self.nameDict[name]:
                if i.endswith(".jpg"):
                    ownList.append(i)
            return ownList

    def doSearch(self, searchDict, name):

        searchList = []
        if self.currentStage == 1:
            maxMessage, messageLeft, currentMessage = self.maxMessage1, self.messageLeft1, self.currentMessage
        elif self.currentStage == 2:
            maxMessage, messageLeft, currentMessage = self.maxMessage2, self.messageLeft2, self.currentMessage
        else:
            return '当前回合无法搜查', searchList

        # 获取对应人的信息
        place = searchDict['place']

        if place == 'df':
            if name in ['lrf', 'wfr', 'wzw', 'lm', 'hy'] and not self.enter_chamber[name]:
                if name in ['lrf', 'hy']:
                    self.enter_chamber[name] = True
                    return '您调查了两杯酒，但两杯酒看起来均毫无异状。现在您可以向新娘提出一个问题。', searchList
                elif name in ['wfr', 'lm']:
                    self.enter_chamber[name] = True
                    return '您调查了两杯酒，新娘梁嫣杯中被下了落雁沙剧毒，新郎武仲文杯中无毒。现在您可以向新娘提出一个问题。', searchList
                elif name == 'wzw':
                    self.enter_chamber[name] = True
                    return '您调查了两杯酒，新娘梁嫣杯中被人下了毒，新郎武仲文杯中无毒。现在您可以向新娘提出一个问题。', searchList

            else:
                return '您无法进入洞房搜查', searchList

        num = searchDict['num'][0]  # 正则返回的是列表
        try:
            num = int(num)
        except Exception as e:
            print('抱歉请使用阿拉伯数字')
            return "抱歉请使用阿拉伯数字", searchList

        # 每一个地方只有2个线索
        if num > 2:
            num = 2

        ml = messageLeft[name]
        cm = currentMessage[place]
        mm = maxMessage[place]
        extra_message = None
        # 搜查数量剩余1条，想要2条就只给1条就行了
        while ml > 0 and num > 0:  # 可以进行搜查
            # 如果还有剩余线索 正常搜查
            if mm >= cm:
                messagePicPath = '../juben/resources/Message/' + '%d' % cm + '.jpg'
                searchList.append(messagePicPath)

                # 搜查到的是武夫人的 触发可以烹饪剧情
                if cm == 32:
                    self.find_peifang = True

                # 搜查过了，不能返回了
                self.enable = False
                # 剩余搜查的线索-1
                num = num - 1
                ml = ml - 1
                # 当前线索+1
                cm = cm + 1
                # 将该条线索记录至当前玩家的已搜查列表
                self.nameDict[name].append(messagePicPath)
                self.sm.sendMs(name, messagePicPath)
                time.sleep(0.2)
                if num == 0:
                    break
            else:
                break
        else:
            extra_message = "您可搜查的线索数量已经不足\n"

        if self.currentStage == 1:
            self.messageLeft1[name], self.currentMessage[place] = ml, cm
        else:
            self.messageLeft2[name], self.currentMessage[place] = ml, cm

        words = extra_message

        return words, searchList

    def detectFace(self):
        # 做声音的检查，现在没有声音，
        name = self.fr.predictFace(6)
        if name == 'vague':
            return self.detectFace()
        print('你好', self.nameMap[name])
        return name

    def predictAction(self, sent):
        if self.am.predictAction(sent) == 'next':
            return "next", None

        elif self.am.predictAction(sent) == 'own':
            return 'own', None

        elif self.am.predictAction(sent) == 'search':
            searchDict = {'place': 'vague', 'num': []}
            num = self.findNum(sent)
            place = self.findPlace(sent)
            searchDict['num'] = num
            searchDict['place'] = place
            if searchDict['place'] == 'vague' and searchDict['num'] == []:
                return 'searchNoPerson', None

            elif searchDict['place'] != 'vague' and searchDict['num'] == []:
                return 'searchNoNum', searchDict

            elif searchDict['place'] == 'vague' and searchDict['num'] != []:
                return 'searchNoPerson', searchDict
            else:
                return 'search', searchDict
        elif self.am.predictAction(sent) == 'previous':
            return "previous", None
        else:
            return "vague", None

    def review(self):
        word = "暂时没弄复盘 请自己复盘吧。"

        return word

    def vote(self, votedName, doName):
        print("请玩家投票")
        if votedName != 'vague' and doName != 'vague' and self.doVote.get(doName) is None:
            self.enable = False
            self.voted[votedName] += 1
            self.doVote[doName] = True
        return [self.nameMap.get(key) for key, value in self.doVote.items() if value is None]


if __name__ == '__main__':
    app = QApplication(sys.argv)

    game = GameLogic()
    ex = GameUi(game)

    ex.window()
    ex.prestart('')
    # ex.open_camera()

    # game.showImg()
    sys.exit(app.exec_())
