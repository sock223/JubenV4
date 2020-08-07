import jieba
# 因为样本更趋向于多项分布 所以用朴素贝叶斯
import sklearn.datasets as sd
import sklearn.feature_extraction.text as ft
import sklearn.naive_bayes as nb
import numpy as np
import re

class CertainlyModel():
    def __init__(self):
        self.nagative = ['不', '没', '无', '别']
        self.positive = ['好', '行', '妥', '哦', '嗯', '恩', '是']
        self.go2trainCertainly()

    def go2trainCertainly(self):
        trainCertainly_data = []

        trainCertainly = sd.load_files('resources/Certainly/',
                                       encoding='utf8', shuffle=True,
                                       random_state=8)

        for i in trainCertainly.data:
            trainCertainly_data.append(" ".join(jieba.cut(i)))
        # train_data = train.data
        #print(trainCertainly_data)

        trainCertainly_y = trainCertainly.target
        #print(trainCertainly.target)

        self.categoriesCertainly = np.array(trainCertainly.target_names)
        #print(np.array(trainCertainly_data).shape)
        #print(np.array(trainCertainly_y).shape)
        #print(self.categoriesCertainly)

        # 构建TFIDF矩阵
        self.cvCertainly = ft.CountVectorizer(ngram_range=(1,1))
        bowCertainly = self.cvCertainly.fit_transform(trainCertainly_data)
        #print(bowCertainly.shape)

        self.ttCertainly = ft.TfidfTransformer()
        tfidfCertainly = self.ttCertainly.fit_transform(bowCertainly)

        # 模型训练  使用MultinomialNB 是因为tfidf
        # 矩阵中样本的分布更匹配多项分布
        self.Certainlymodel = nb.MultinomialNB()
        #print(trainCertainly_y.shape)
        self.Certainlymodel.fit(tfidfCertainly, trainCertainly_y)


    def predictCertainly(self, sent):

        list = []
        pred_res = []
        sents = re.split('。|！|，|\.|,', sent)
        for i in sents:
            list.append(" ".join(jieba.cut(i)))
        #print("data:")
        #print(list)

        test_bow = self.cvCertainly.transform(list)

        test_tfidf = self.ttCertainly.transform(test_bow)
        pred_test_y = self.Certainlymodel.predict(test_tfidf)

        # 计算置信概率
        probs = self.Certainlymodel.predict_proba(test_tfidf)
        #print(probs)
        resList = self.getMeansByStd(probs)

        #存放子句中false个数是否为奇数的数组
        falseNum = []


        #如果能够判断出来语义的话，将语义肯定或否定加到预测的结果中

        #若每个子句中 否定词都是偶数，并且出现了肯定词，那么意思为肯定
        for s, index, i in zip(sents, pred_test_y, range(len(resList))):
            if resList[i]:
                #将预测到的结果添加进入预测的结果list
                pred_res.append(self.categoriesCertainly[index])
                if self.categoriesCertainly[index] == 'true':
                    #如果判断结果是true的话，说明这个子句是肯定的，那么否定词的个数是偶数，加0
                    falseNum.append(0)
                else:
                    falseNum.append(1)
            else:
                r = self.CertainlyLevel2(s)
                falseNum.append(r)

        falseNum = np.array(falseNum)
        #true :奇数
        falseNum = falseNum%2

        if falseNum.all(axis=0):
            #都为奇数(已经将预测的结果包含进去了，如果预测是false会放1)，表示每个子句都是否定
            #print(sents, '->', 'false')
            return 'false'
        elif falseNum.any(axis=0) == False:
            #一个奇数都没有(已经将预测的结果包含进去了，如果预测是false会放1)，表示每个子句都是肯定，那么判断是否有肯定词
            #没预测到结果那么找 表示肯定的关键词，因为没有否定的关键词或否定的关键词是偶数
            #所以进来要么是肯定，要么是动作
            if self.CertainlyLevel3(sent) or len(pred_res)>0:   #预测结果大于0是以为预测到了肯定值，否定值的话会置1进入上面的条件
                #print(sent, '->', 'true')
                return 'true'
            else:
                #如果没有肯定词，那么可能是动作 （每段话都是肯定，）
                #print(sent, '->', 'vague')
                return 'vague'
        else:
            #这个既有肯定词又有否定词在不同的子句中，不知道是什么意思 ！！！与上方判断的的意义不一样，凑巧写法一样
            #print(sent, '->', 'trueAndFalse')
            return 'trueAndFalse'

    def getMeansByStd(self, probs):
        resList = []
        for i in probs:
            resList.append(np.std(i) > 0.1)
            #print(np.std(i))
        return resList

    # 一个子句中否定词的个数
    def CertainlyLevel2(self, sent):
        num = 0
        for i in self.nagative:
            num += sent.count(i)
        return num

    def CertainlyLevel3(self, sent):
        num = 0
        for i in self.positive:
            num += sent.count(i)
        return num