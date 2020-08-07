import jieba
# 因为样本更趋向于多项分布 所以用朴素贝叶斯
import sklearn.datasets as sd
import sklearn.feature_extraction.text as ft
import sklearn.naive_bayes as nb
import numpy as np
import os
class ActionModel():
    def __init__(self):
        self.go2trainAction()


    def go2trainAction(self):
        trainAction_data = []

        trainAction = sd.load_files('resources/Action/',
                                    encoding='utf8', shuffle=True,
                                    random_state=8)
        for i in trainAction.data:
            trainAction_data.append(" ".join(jieba.cut(i)))
        # train_data = train.data
        #print(trainAction_data)

        trainAction_y = trainAction.target
        #print(trainAction_y)

        self.categoriesAction = np.array(trainAction.target_names)

        #print(np.array(trainAction_data).shape)
        #print(np.array(trainAction_y).shape)
        #print(self.categoriesAction)

        # 构建TFIDF矩阵 使用1-gram 这边的词是根据空格划分的，前面jieba已经拆成空格了
        self.cvAction = ft.CountVectorizer(ngram_range=(1,1))

        # # input to fit_transform() should be an iterable with strings
        # ngrams = self.cvAction.fit_transform(trainAction_data)
        #
        # # needs to happen after fit_transform()
        # vocab = self.cvAction.vocabulary_
        #
        # count_values = ngrams.toarray().sum(axis=0)
        #
        # # output n-grams
        # for ng_count, ng_text in sorted([(count_values[i], k) for k, i in vocab.items()], reverse=True):
        #     print(ng_count, ng_text)

        bowAction = self.cvAction.fit_transform(trainAction_data)
        #print(bowAction.shape)

        self.ttAction = ft.TfidfTransformer()
        tfidfAction = self.ttAction.fit_transform(bowAction)

        # 模型训练  使用MultinomialNB 是因为tfidf
        # 矩阵中样本的分布更匹配多项分布
        self.Actionmodel = nb.MultinomialNB()
        #print(trainAction_y.shape)
        self.Actionmodel.fit(tfidfAction, trainAction_y)


    def predictAction(self, sent):
        list = []
        list.append(' '.join(jieba.cut(sent)))
        bow = self.cvAction.transform(list)
        tfidf = self.ttAction.transform(bow)
        res = self.Actionmodel.predict(tfidf)

        # 计算置信概率
        probs = self.Actionmodel.predict_proba(tfidf)
        print(probs)
        resList = self.getMeansByStd(probs)

        if resList[0]:
            #print(sent, '->', self.categoriesAction[res])
            return self.categoriesAction[res][0]
        else:
            return 'vague'

    def getMeansByStd(self, probs):
        resList = []
        for i in probs:
            resList.append(np.std(i) > 0.1)
            #print(np.std(i))
        return resList
