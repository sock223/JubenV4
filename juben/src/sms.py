import requests, json


class Sms():
    def __init__(self):
        self.headers = {'User-Agent':'Mozilla/5.0',
                        'Content-Type': 'application/json;charset=UTF-8'}
        self.url = '这个...提供不了'

        self.name_phone = {
            "hy" : "18610186119",
            "jxz": "13552005105",
            "lm": "18210957015",
            "lrf": "15101615165",
            "mx": "17316114597",
            "wfr": "13811816748",
            "wzw": "13693297939",
            "ysq": "13717924645"
        }
        self.path_message = {
            '../juben/resources/Message/1.jpg': '【含烟】一个草人，上面缠绕着一束青丝',
            '../juben/resources/Message/2.jpg': '【含烟】一张花笺的碎片，上面是一点、一横',
            '../juben/resources/Message/3.jpg': '【含烟】含烟身着海棠红如意纹缂丝对襟短襦，妃色地联珠对孔雀纹锦半臂，七破缕金间色罗裙，衣饰极为华贵，便是与一般官宦人家的千金相比也毫不逊色。',
            '../juben/resources/Message/4.jpg': '【含烟】一个锦缎香囊，上面绣着一只绕梁飞舞的紫燕，另有几行诗句：春日宴，绿酒一杯歌一遍，再拜陈三愿',
            '../juben/resources/Message/5.jpg': '【静虚子】一枚三寸来长的乌木令牌，上面刻着一片桐叶',
            '../juben/resources/Message/6.jpg': '【静虚子】一本《易镜玄要》，你随手翻了几页，见上面写着：东方甲乙木，南方丙丁火，中央戊己土，西方庚辛金，北方壬癸水。五行错置，乾坤倒乱，阴阳流转，万世不竭。你仔细阅读《易镜玄要》，看到了下面这段话：生魂是活人离体的魂魄，阳气极重。某些得道之士可以使用元神出窍的道术，使自己魂魄离体，化作生魂',
            '../juben/resources/Message/7.jpg': '【静虚子】一张药方，上面写着：生枣仁五钱，麦冬一两，熟地一两，白芍一两，当归五钱，山茱萸五钱，人参一两，茯神五钱，远志二钱，巴戟天二钱，柏子仁三钱，白芥子二钱',
            '../juben/resources/Message/8.jpg': '【梁仁甫】一份礼单，其中珍玩无数-- 碧玉狮子成对，翡翠凤凰成双，特品紫毫百枝，贡墨二十锭，海兽葡萄纹錾金壶一把... 署名方仁杰',
            '../juben/resources/Message/9.jpg': '【梁仁甫】一枚赤金指环，上面刻着一只鳄鱼，仰头甩尾，张口露齿，神态极为凶猛',
            '../juben/resources/Message/10.jpg': '【梁仁甫】一个锦缎香囊，上面绣着一只绕梁飞舞的紫燕，另有几行诗句：一愿郎君千岁，二愿妾身长健，三愿如同梁上燕，岁岁常相见',
            '../juben/resources/Message/11.jpg': '【梁仁甫】一串七宝璎珞，结成柳叶合心的样式，不似男子之物',
            '../juben/resources/Message/12.jpg': '【柳眠】一份案宗：这是多年前的一份案宗，字迹已经有些模糊了，你随手翻看了数页，只见上面记录着，死者名叫柳昀，生前正奉朝廷之命在调查一桩盐枭大案，他已经查明东南盐枭之首--旱地鼍龙，是一个姓方的中年男子',
            '../juben/resources/Message/13.jpg': '【柳眠】柳眠的左臂上纹着一只青色的九尾蝎',
            '../juben/resources/Message/14.jpg': '【柳眠】这是多年前的一张尸格，上面记载着死者柳昀的死状--面孔涨得紫青，双目圆睁两眼翻白，七窍之中流着鲜血，似是中毒而亡',
            '../juben/resources/Message/15.jpg': '【柳眠】十几个包裹严密的纸包，里面放着各色的粉末',
            '../juben/resources/Message/16.jpg': '【妙玄】一张青面獠牙的鬼头面具',
            '../juben/resources/Message/17.jpg': '【妙玄】一个瓷瓶，里面装着小半瓶朱红色的粉末',
            '../juben/resources/Message/18.jpg': '【妙玄】妙玄右手小指的指甲极长',
            '../juben/resources/Message/19.jpg': '【妙玄】妙玄鞋底的磨损程度与常人不同，前掌磨损较重，后跟处却毫无磨损',
            '../juben/resources/Message/20.jpg': '【庭院】在假山后面的山石上，扔着一把刻着海兽葡萄纹的鎏金九曲鸳鸯壶，壶身近柄处有两个小孔',
            '../juben/resources/Message/21.jpg': '【庭院】厨房中飘着一股异香',
            '../juben/resources/Message/22.jpg': '【庭院】大门上贴着两张封条，上面写着：开元十二年七月十五日，广州刺史府封',
            '../juben/resources/Message/23.jpg': '【庭院】一间客房的床榻上，仰卧着一具青年女性的尸骨，颈中插着一根银针。尸骨通体隐隐发青',
            '../juben/resources/Message/24.jpg': '【庭院】青霜阁外俯趴着一具青年女性的尸骨，颈骨黑紫',
            '../juben/resources/Message/25.jpg': '【庭院】青霜阁内的地面上有一个两丈的深坑，坑内插满了粗大的竹刺。在竹刺丛中躺着两具男性的尸骨',
            '../juben/resources/Message/26.jpg': '【庭院】在泻玉池中，飘着一具中年女性的尸骨',
            '../juben/resources/Message/27.jpg': '【庭院】一间客房的桌上趴着一具青年男子的尸骨，手中捏着几片碎纸。尸骨通体发黑',
            '../juben/resources/Message/28.jpg': '【庭院】洞房的梁上吊着一具青年女性的尸骨，穿着一袭大红嫁衣，脚上的绣花鞋掉了一只',
            '../juben/resources/Message/29.jpg': '【武夫人】吕氏的右臂上纹着一只青色的九尾蝎',
            '../juben/resources/Message/30.jpg': '【武夫人】一本泛黄的书册，封面上写着：黎家五毒秘典 几个字',
            '../juben/resources/Message/31.jpg': '【武夫人】一支青玉梅花簪',
            '../juben/resources/Message/32.jpg': '【武夫人】一份药膳的配方',
            '../juben/resources/Message/33.jpg': '【武仲文】三张药方，分别是：白虎散、逍遥丹、安神汤',
            '../juben/resources/Message/34.jpg': '【武仲文】一本世系谱牒：上面记载着各大世家望族的世系，其中太原王氏的始祖王子晋据说在修道多年后，乘鹤飞升而去',
            '../juben/resources/Message/35.jpg': '【武仲文】一枚羊脂玉佩。这是一枚古玉，以最上等的和田白玉制成，温润莹白，触手生温。上面雕刻着一位峨冠仙人，身骑白鹤，手持笙管',
            '../juben/resources/Message/36.jpg': '【武仲文】几张临摹魏碑《龙门十二品》的纸笺，字迹雄健，笔势浑厚，模仿地惟妙惟肖',
            '../juben/resources/Message/37.jpg': '【殷思齐】一张青面獠牙的鬼头面具',
            '../juben/resources/Message/38.jpg': '【殷思齐】殷思齐的腰带上缝了十几个小小的布囊',
            '../juben/resources/Message/39.jpg': '【殷思齐】一个针囊里面放着数十枚银针',
            '../juben/resources/Message/40.jpg': '【殷思齐】一把匕首，青光闪闪，十分锋利',
            'special' : '【柳眠的隐藏事件】一个中年仆妇将你请到了四美堂的一角，悄声对你说道：郎君（指柳眠），婢子是西安夫人柳氏（即柳眠的姑母，梁仁甫的亡妻）的贴身侍女--烟翠。先夫人仙去之前似乎预感到自己有可能不在人世，对婢子说：若是郎君有朝一日回到广州，且未与小娘子（梁嫣）成婚，就将这封遗书交给郎君；若是郎君终与小娘子结为夫妇，就将这遗书烧掉。'
                        '烟翠说完，递给柳眠一张微微泛黄的信笺，柳眠展信观阅，只见上面用姑母娟秀的字迹写着寥寥数行字： 眠儿，你父亲（柳昀）当年死的蹊跷，我心中疑窦难消，暗中查访多年，终于查出，你父亲的死似乎与你的姑丈梁仁甫有关。',
            'special2': '【柳眠的隐藏事件】一个中年仆妇将柳眠请到了四美堂的一角，对他说了些什么。',
            'special3': '【武夫人公共事件】 有人从武夫人处搜到一份药膳，询问武夫人是否愿意按照配方烹饪此药膳。',
            'special4': '【武夫人公共事件】 武夫人按照药膳烹饪后，药膳中飘出了一股异香',
            'special5': '【岐黄】 这是摄魂汤的配方，摄魂汤是一剂治疗离魂症的良药，而离魂症是指人在受到强烈的刺激时，三魂七魄中的二魂六魄离体飞去，躯体里只留存了一魂一魄，因而从此成为疯癫之人',
            'special6': '【梁嫣回答】 三年前，母亲暴病去世，自那以后我便自学了医术，天幸如此，我才能在喝酒时，发现酒中异样。',
            'special7': '【梁嫣回答】 我的贴身侍女含烟',
            'special8': '【梁嫣回答】 我从没给你写过什么绝情书，明明是你给我写了一封绝情信'

        }


    def sendMs(self, name, path):
        url = self.url
        data = json.dumps({"phone": self.name_phone.get(name), "content": self.path_message.get(path), "token": "61d12aebce4c9829fcb2917def8a35e0"})
        r = requests.post(url, data, headers=self.headers)
        print(r.json())
        print(path)


    def sendMsTest(self, phone, message):
        url = self.url
        data = json.dumps({"phone": phone, "content": message, "token": "61d12aebce4c9829fcb2917def8a35e0"})
        r = requests.post(url, data, headers=self.headers)
        print(r.json())

