#! -*- coding:utf-8 -*-

#因为样本更趋向于多项分布 所以用朴素贝叶斯
from src import actionModel as am

# 测试
test_data = [
    '深入调查线索E',
    '深入调查',
    '看看我的线索',
    '让我看看我的线索',
    '调查漫画家',
    '调查',
    '搜索林教授',
    '开始投票吧',
    '投票',
    '再给我看看以前的线索',
    '看看林夺的线索',
    '看林夺的线索'
]

test_data7 = [
    '看看林夺',
    '章乔的线索1条',
    '调查E',
    '看看线索',
    '查罗宇飞',
    '本轮结束',
    '深入调查',
    'E',
    '我的线索',
    '有的线索',
    '已经有的线索',
    '我想看吴有为的线索',
    '我想看孙云业的线索',
    '查陈兴元',
    '搜查林夺',
    '返回上一阶段',
    '下一阶段'
]

test_data2 = [
    '跳到下一轮',
    '下一轮搜证',
    '下一轮',
    '下一轮开始',
    '下个阶段',
    '开始',
    '上一阶段',
    '搜查结束',
    '下一阶段'

]


test_data3 = [
    '我投给jack，我觉得他是凶手',
    '投给lily',
    '选sam吧'
]



test_data4 = [
    '调查',
    '我要搜老板娘',
    '搜查',
    '调查',
    '搜索',
    '查'
]

test_data5 = [
    '是的',
    '好',
    '好了',
    '开始',
    '确定',
    '确认',
    '同意',
    '不',
    '别',
    '没',
    '不开始'
]

test_data6 = [
    '返回',
    '退回',
    '回到上一阶段',
    '上一阶段',
    '上个阶段',
    '退',
    '回到上个阶段',
    '回到上一阶段',
    '下一回合'
]


def findName(sent):
    if '姝' in sent:
        return 'ms'
    elif '锦' in sent:
        return 'sj'
    elif '彦' in sent:
        return 'my'
    elif '秀' in sent or '绣' in sent:
        return 'sx'
    elif '杜' in sent or '磊' in sent:
        return 'dxl'
    elif '翟' in sent:
        return 'zg'
    elif '韩' in sent or '凝' in sent:
        return 'hsn'
    else:
        return 'vague'

import re
def findNum(sent):
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

    xs = re.compile(r'[0-9]+')
    return xs.findall(sent)

# words = input("输入:")
#
# def giveMethod(sent):
#     giveDict = ['给', '交', '赠与']
#     name = None
#     nums = None
#     for i in giveDict:
#         if i in sent:
#             arr = sent.split(i)
#             for j in arr:
#                 # 这半句话找到了赠与的人
#                 if findName(j) != 'vague':
#                     name = findName(j)
#                 # 这半句话找到了 交易的卡片号
#                 if len(findNum(j)) > 0:
#                     nums = findNum(j)
#             if name is not None and nums is not None:
#                 return print("将",nums,"给",name)
#             else:
#                 name = None
#                 nums = None
#     # 遍历了所有表示给的字，之后，没有在语句中存在，说明不是赠与的意思
#     return print("不是给的意思")
#
# giveMethod(words)

b = am.ActionModel()
for i in test_data:
    print(i,'->',b.predictAction(i))
