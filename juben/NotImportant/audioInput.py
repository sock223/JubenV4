#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pyaudio import PyAudio, paInt16
import wave


#模型训练
import os
import numpy as np
import scipy.io.wavfile as wf
#import python_speech_features as sf
#import hmmlearn.hmm as hl
import time


class Recoder:
    NUM_SAMPLES = 2000      #pyaudio内置缓冲大小
    SAMPLING_RATE = 8000    #取样频率
    LEVEL = 2000         #声音保存的阈值
    COUNT_NUM = 5     #NUM_SAMPLES个取样之内出现COUNT_NUM个大于LEVEL的取样则记录声音
    SAVE_LENGTH = 5        #声音记录的最小长度：SAVE_LENGTH * NUM_SAMPLES 个取样
    TIME_COUNT = 10     #录音时间，单位s
    COMMAND_LEVEL = 1000
    LOWER_NUM = 8
    START = False

    Voice_String = []

    def savewav(self,filename):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(self.SAMPLING_RATE)
        wf.writeframes(np.array(self.Voice_String).tostring())
        wf.close()

    def weakup(self):
        self.TRANS = True

    def recordVoice(self):

        pa = PyAudio()
        stream = pa.open(format=paInt16, channels=1, rate=self.SAMPLING_RATE, input=True,
                         frames_per_buffer=self.NUM_SAMPLES)
        self.Voice_String = []
        save_buffer = []
        leftTime = self.LOWER_NUM
        while True:
            # 读入NUM_SAMPLES个取样
            string_audio_data = stream.read(self.NUM_SAMPLES)
            # 将读入的数据转换为数组
            audio_data = np.fromstring(string_audio_data, dtype=np.short)
            # 计算大于LEVEL的取样的个数
            large_sample_count = np.sum( audio_data > self.LEVEL )
            print(np.max(audio_data))

            if np.max(audio_data)>self.COMMAND_LEVEL:
                self.START = True

            if self.START:
                # 将要保存的数据存放到save_buffer中
                save_buffer.append(string_audio_data)
                if np.max(audio_data)<self.COMMAND_LEVEL:
                    leftTime -= 1
                else:
                    leftTime = self.LOWER_NUM

                if leftTime <= 0:
                    self.Voice_String = save_buffer
                    save_buffer = []
                    self.savewav('voice.wav')
                    print("Recode a piece of  voice successfully!")
                    stream.stop_stream()
                    stream.close()
                    pa.terminate()
                    return self.Voice_String


    def combine(self):
        # 从目录中读取语音
        wf = wave.open('stage1-1.wav', 'rb')
        data = wf.readframes(self.SAMPLING_RATE*self.NUM_SAMPLES)
        wf2 = wave.open('stage1-2.wav','rb')
        data2 = wf2.readframes(self.SAMPLING_RATE*self.NUM_SAMPLES)
        wf3 = wave.open('stage1-3.wav', 'rb')
        data3 = wf3.readframes(self.SAMPLING_RATE * self.NUM_SAMPLES)
        # wf4 = wave.open('4.wav', 'rb')
        # data4 = wf4.readframes(self.SAMPLING_RATE * self.NUM_SAMPLES)
        # wf5 = wave.open('5.wav', 'rb')
        # data5 = wf5.readframes(self.SAMPLING_RATE * self.NUM_SAMPLES)
        # wf6 = wave.open('6.wav', 'rb')
        # data6 = wf6.readframes(self.SAMPLING_RATE * self.NUM_SAMPLES)







        wf7 = wave.open('combine.wav', 'wb')
        wf7.setnchannels(1)
        wf7.setsampwidth(2)
        wf7.setframerate(self.SAMPLING_RATE)
        wf7.writeframes(data+data2+data3)
        wf7.close()


# class VoiceModel:
#     def __init__(self):
#         self.models = {}
#     @staticmethod
#     def search_Trainfiles(directory):
#         # 目的
#         # 读取dict内容，返回一个字典
#         # {'apple':[url1,url2,url3],'banana':[..]}
#
#         # 把dict的目录改为当前平台所能识别的目录
#         directory = os.path.normpath(directory)
#         objects = {}
#         for curdir, subdirs, files in os.walk(directory):
#             for file in files:
#                 if file[-4:] == '.wav':
#                     label = curdir.split(os.path.sep)[-1]  # apple 文件目录名
#                     if label not in objects:
#                         objects[label] = []
#                     path = os.path.join(curdir, file)
#                     objects[label].append(path)
#         return objects
#
#     def trainWeakupModel(self):
#         train_x, train_y = [], []
#         # 整理训练集 为每一个类别训练HMM模型
#         train_samples = self.search_Trainfiles('Sound')
#         for label, filenames in train_samples.items():
#             mfccs = np.array([])
#             for filename in filenames:
#                 sample_rate, sigs = wf.read(filename)
#                 mfcc = sf.mfcc(sigs, sample_rate)
#                 # axis在垂直方向追加样本
#                 if len(mfccs) == 0:
#                     mfccs = mfcc
#                 else:
#                     mfccs = np.append(mfccs, mfcc, axis=0)
#
#             # 构建一个trainx 样本竖着堆叠，输出一个label（apple） （每个mfcc样本输出一个apple）
#             train_x.append(mfccs)
#             train_y.append(label)
#
#         # 基于HMM模型训练样本
#         # models = {'apple':modelObject}
#         for mfccs, label in zip(train_x, train_y):
#             model = hl.GaussianHMM(n_components=4, covariance_type='diag', n_iter=1000)
#             self.models[label] = model.fit(mfccs)
#
#     def testModel(self):
#
#
#         sample_rate, sigs = wf.read('voice.wav')
#
#         mfcc = sf.mfcc(sigs, sample_rate)
#
#         pred_test_y = []
#         best_score, best_label = None, None
#         for label, model in self.models.items():
#             score = model.score(mfcc)
#             print(label, score)
#             if (best_score is None) or (best_score < score):
#                 best_score = score
#                 best_label = label
#         pred_test_y.append(best_label)
#
#         print(pred_test_y)


if __name__ == "__main__":
    r = Recoder()
    r.recordVoice()
    #r.combine()
