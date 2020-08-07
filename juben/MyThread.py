import sys
from PyQt5.QtCore import Qt, QThread,pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,QHBoxLayout
class MyThread(QThread):#线程类
    my_signal = pyqtSignal(str)  #自定义信号对象。参数str就代表这个信号可以传一个字符串
    def __init__(self):
        super(MyThread, self).__init__()
        self.count = 0
        self.is_on = True


    def run(self): #线程执行函数
        while self.is_on :
            print(self.count)
            self.count += 1
            self.my_signal.emit(str(self.count))  #释放自定义的信号
            #通过自定义信号把str(self.count)传递给槽函数

            self.sleep(1)  #本线程睡眠n秒【是QThread函数】
