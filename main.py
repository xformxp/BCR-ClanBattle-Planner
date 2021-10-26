# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from tkinter import *
from tkinter.filedialog import *
import itertools
import _pcr_data
import re
from typing import List


def loadFile() -> str:
    filename = askopenfilename(filetypes=[("Text file", "*.txt", "TEXT")], defaultextension="*.txt")
    # print(filename)
    if filename is None or filename[0] == '':
        return None
    return filename


class CharaList:
    def __init__(self):
        self.chara_id = dict()
        for ch in _pcr_data.CHARA_NAME:
            for alias in _pcr_data.CHARA_NAME[ch]:
                self.chara_id[alias] = ch
        char_list = ['羊驼', '布丁', '空花', '黑骑', '狗拳', '佩可', '流夏', '望', '狼', '哈哈剑', '茉莉', '裁缝', '猫拳',
                     '炸弹人', '熊锤', '猫剑', '智', '水猫剑', '病娇', '水吃', '铃铛', '姬塔', '剑圣', '姐姐', '克', '兔子',
                     '忍', '奶牛', '黄骑', '毛二力', '扇子', '子龙', '伊利亚', '咲恋', '环奈', '中二', '万圣忍', '水子龙',
                     '可可罗', '水白', '松鼠', '深月', '妹法', '姐法', '狼布丁', '亚里沙', '妹弓', '暴击弓', 'tp弓', '魅魔',
                     '女仆', '美里', '普黑', '初音', '大眼', '水女仆', '水黑', '香菜', '千歌', '狐狸', 'ue', '雪', 'xcw', '瓜眼',
					 '七七香', '圣千', '圣锤', '春田', '春猫', '春剑', '情姐', '情病', '511', '霞', '步未', '拉姆', '蕾姆', 'emt',
                     '安', '古雷亚', '江花', '忍扇', '水暴', '水电', '水狼', '水狐', '生菜', 'nnk', '华哥', '瓜炸', 'mcw', '万圣兔',
                     #'露娜', '嘉夜', '圣克', '春黑', '春妈', '魔驴', '高达', '卵用', '凛', 'uni', '切噜'
                     ]
        self.curr_chars = []
        for ch in char_list:
            self.curr_chars.append(self.chara_id[ch])

    def getCharaId(self, name):
        return self.chara_id[str.lower(name)]

    def getCharaList(self):
        return self.curr_chars

    def getCharaName(self, chara_id, jpn=0):
        return _pcr_data.CHARA_NAME[chara_id][jpn]


chara = CharaList()


class Window:
    def __init__(self, title, geometry):
        self.window = Tk()
        self.window.title(title)
        self.window.geometry(geometry)
        self.box_file = None
        self.choice_file = None
        self.box = None
        self.choice = None
        self.F1 = Frame(self.window)
        self.F2 = Frame(self.window)
        self.l_party = Label(self.F1, text=f"Box文件（列出你缺的box）: {self.box_file}")
        self.f_party = Button(self.F1, text='Open', command=self.loadParty)
        self.l_choice = Label(self.F1, text=f"作业文件: {self.choice_file}")
        self.f_choice = Button(self.F1, text='Open', command=self.loadChoice)
        self.F1.pack(pady=10)
        self.F2.pack(ipadx=20, ipady=20)
        self.l_party.grid(row=0, column=1, pady=5)
        self.f_party.grid(row=0, column=0)
        self.l_choice.grid(row=1, column=1, pady=5)
        self.f_choice.grid(row=1, column=0)
        self.JPN = IntVar(value=1)
        Checkbutton(self.F1, text="谜语人模式", variable=self.JPN).grid(row=2, column=0, columnspan=2, pady=5)
        button = Button(self.F1, text="计算", command=self.calc)
        button.grid(row=3, column=0, columnspan=2, pady=5)
        self.result = Label(self.F2, text="", font=('TkDefaultFont', 12))
        self.result.pack()

    def loadParty(self):
        self.box_file = loadFile()
        self.l_party.config(text=f"Box文件: {self.box_file}")

    def loadChoice(self):
        self.choice_file = loadFile()
        self.l_choice.config(text=f"作业文件: {self.choice_file}")

    def writeResult(self, s):
        self.result.config(text=s)

    def calc(self):
        if self.box_file is None or self.choice_file is None:
            self.writeResult("文件为空")
            return
        with open(self.box_file, "r", encoding="utf-8") as f:
            box_read = f.read().split()
            filtered_box = []
            for ch in box_read:
                filtered_box.append(chara.getCharaId(ch))
            self.box = set(chara.getCharaList()) - set(filtered_box)
        self.choice = []
        with open(self.choice_file, "r", encoding="utf-8") as f:
            choices = f.read().strip().split('\n')
            for choice in choices:
                c = choice.split()
                c[6] = re.sub("[wW]", "", c[6])
                if len(c) != 7 or not c[6].isdigit():
                    self.writeResult("作业文件格式错误")
                    return
                self.choice.append({"name": c[0], "team": list(map(chara.getCharaId, c[1:6])), "dmg": int(c[6])})
        res = []
        output = []
        for perm in itertools.combinations(self.choice, 3):
            avail, dmg = self.checkAvailability(perm)
            if avail:
                res.append((dmg, perm))
        res.sort(key=lambda x: x[0], reverse=True)
        if len(res) == 0:
            self.writeResult('没有可用分刀')
            return
        res = res[:100]
        for i, r in enumerate(res):
            output.append(f"PLAN {i + 1} TOTAL={r[0]}\n" +
                          '\n'.join([f"{x['name']}"
                                     f"({', '.join(map(lambda k: chara.getCharaName(k, self.JPN.get()), x['team']))}), "
                                     f"{x['dmg']}" for x in r[1]]))
        with open("result.out", "w", encoding="utf-8") as f:
            f.write('\n\n'.join(output))
        self.writeResult('\n\n'.join(output[:5]))

    def checkAvailability(self, perm: (dict, dict, dict)) -> (bool, int):
        box_copy = self.box
        team = [x["team"] for x in perm]
        for i, j, k in itertools.product(itertools.combinations(team[0], 4),
                                         itertools.combinations(team[1], 4),
                                         itertools.combinations(team[2], 4)):
            s = set(i) | set(j) | set(k)
            if len(s) == 12 and len(self.box & s) == 12:
                return True, sum([x["dmg"] for x in perm])
        return False, 0

    def mainloop(self):
        self.window.mainloop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    window = Window('分刀', '800x600')
    window.mainloop()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
