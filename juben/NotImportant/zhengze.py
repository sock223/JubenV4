import re







xs = re.compile(r'([0-9一两三仨二壹四肆]+).*?线索')
print(xs.findall('ad一二啊你不行啊987两三四五12一3线索456a4d三f线索a'))



#\u767e\u5343\u96f6 百千万
print(re.findall(r'([0-9一两三仨二壹四肆]+).*?线索',"ad一二啊你不行啊987两三四五123线索456a4df线索a"))
print(re.findall('线索',"ad一f12234567a4df线索a"))


xs = re.compile(r'\d{6}')
print(xs.findall('ad一二啊你不行啊987两三四五12123212312311一3线索456a4d三f线索a'))



xs_feitanlan = re.compile(r'a.*?a')
xs_tanlan = re.compile(r'a.*a')
print(xs_feitanlan.findall('3a123adadffa1'))
print(xs_tanlan.findall('3a123adadffa1'))



import re
def myFunc(sent):
    xs = re.compile(r'([a-z\-0-9]*) *([A-Z0-9]*) *(.*?) *(\d{4}-\d{2}-\d{2})')
    r = xs.findall(sent)
    try:
        d = {'uuid':r[0][0],'code':r[0][1],'title':r[0][2],'date':r[0][3]}
        return d
    except Exception as e:
        print(e)

print(myFunc('acb8af4a-02fb-4aa5-71ae-c3589jfabc0     AC009C    关于公司为全资子公司San Jose  USA, L.L.C.申请融资提供担保的公告    2018-02-29'))