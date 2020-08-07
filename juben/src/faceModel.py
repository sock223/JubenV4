import cv2 as cv
import time
import os
import numpy as np
import sklearn.preprocessing as sp
import face_recognition
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler



class FaceRecognition():
    def __init__(self):
        self.savePath = 'resources/image/img/'



    def delByName(self,name):
        directory = os.path.normpath('resources/image/img/' + name)
        for curdir, subdirs, files in os.walk(directory):
            #删掉里面的照片
            for i in files:
                os.remove(curdir+'/'+i)


    def search_faces(self,directory):
        directory = os.path.normpath(directory)
        faces = {}
        for curdir, subdirs, files in os.walk(directory):
            for jpeg in (file for file in files
                         if file.endswith('.jpg')):
                path = os.path.join(curdir, jpeg)
                label = path.split(os.path.sep)[-2]
                if label not in faces:
                    faces[label] = []
                faces[label].append(path)
        return faces

#方法3
    def trainModel(self):
        self.faceLib = []
        self.labels = []
        #for subdirs in os.listdir('resources/image/img'):
        for subdirs in ['hy','jxz','lm','lrf','wfr','wzw','mx','ysq']:
            #sun lin chen
            self.faceLib.append(face_recognition.face_encodings(face_recognition.load_image_file('resources/image/img/'+subdirs+'/1.jpg'))[0])
            self.labels.append(subdirs)
        self.faceLib = np.array(self.faceLib)
        self.labels = np.array(self.labels)
        print(self.faceLib)

    def predictFace(self,sec):
        vc = cv.VideoCapture(0)  # 视频流
        for i in range(10):
            frame = vc.read()[1]
            cv.waitKey(33)
        #只进行sec秒检测
        t_end = time.time() + sec
        while time.time() < t_end:
            frame = vc.read()[1]
            face_location = face_recognition.face_locations(frame)
            print("fl:",face_location)
            face_encoding = face_recognition.face_encodings(frame,face_location)
            print('fe:',face_encoding)
            #[f t f f f f]  compare_face做了 np.linalg.norm(face_encodings - face_to_compare, axis=1)
            if len(face_location) == 1 and len(face_encoding) == 1:
                match = face_recognition.compare_faces(self.faceLib,face_encoding, tolerance=0.35)
                print("match",match)
                print('lebel[match]',self.labels[match])
                if len(self.labels[match])>0:
                    return self.labels[match][0]
                else:
                    return 'vague'
        else:
            return 'vague'


if __name__ == '__main__':
    fr = FaceRecognition()
    # while True:
    #     k = input("输入你的姓名: /detective du hai host liu professor   输入q退出")
    #     if k == 'q':
    #         break
    #     else:
    #         fr.picCap(k,20)

    fr.trainModel()
    fr.predictFace(6)
