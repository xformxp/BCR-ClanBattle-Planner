# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from tkinter import *
from tkinter.filedialog import *
import itertools
from collections import defaultdict
import _pcr_data_202204 as _pcr_data
import re
import requests
import json
from lxml import etree
from typing import List, Tuple

def loadFile() -> str:
    filename = askopenfilename(filetypes=[("Text file", "*.txt", "TEXT")], defaultextension="*.txt")
    # print(filename)
    if filename is None or filename[0] == '':
        return None
    return filename


class CharaList:
    def __init__(self):
        self.chara_id = dict()
        self.curr_chars = []
        for ch in _pcr_data.CHARA_NAME:
            for alias in _pcr_data.CHARA_NAME[ch]:
                self.chara_id[alias] = ch
            self.curr_chars.append(ch)

    def getCharaId(self, name):
        return self.chara_id[str.lower(name)]

    def getCharaList(self):
        return self.curr_chars

    def getCharaName(self, chara_id, jpn=0):
        return _pcr_data.CHARA_NAME[chara_id][jpn]

chara = CharaList()

class Spider:
    def __init__(self):
        headers = {
            'x-requested-with': 'XMLHttpRequest',
        }
        charas = requests.get("https://www.caimogu.cc/gzlj/data/icon?date=", headers = headers).json()
        self.chara = dict()
        for iconmap in charas["data"]:
            for icon in iconmap:
                self.chara[icon["id"]] = icon["iconValue"]
        #with open('icon.out', 'w', encoding='utf-8') as f:
        #    f.write(json.dumps(self.chara, indent = 4, ensure_ascii = False))
        homework = requests.get("https://www.caimogu.cc/gzlj/data?date=", headers = headers).json()
        self.data = homework["data"]
        #with open('f.out', 'w', encoding='utf-8') as f:
        #    f.write(json.dumps(self.data, indent = 4, ensure_ascii = False))
        print("Data fetched from caimogu")
    
    def write_homework(self, stage):
        with open("作业.txt", "w", encoding = "utf-8") as f:
            for boss in self.data:
                if boss["stage"] == stage:
                    homeworks = boss["homework"]
                    for hw in homeworks:
                        if hw['auto'] < 2:
                            charas = [self.chara[hw['unit'][x]] for x in range(5)]
                            f.write(f"{hw['sn']} {' '.join(charas)} {hw['damage']}\n")
    
    def print(self):
        with open("f.out", "wb") as f:
            f.write(json.dumps(self.data, indent = 4, ensure_ascii = False).encode("utf-8"))

class Window:
    def __init__(self, title, geometry):
        self.stage = 1
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
        self.gen_choice = Button(self.F1, text = '作业网生成作业', command = self.genChoice)
        self.f_choice = Button(self.F1, text='Open', command=self.loadChoice)
        self.F1.pack(pady=10)
        self.F2.pack(ipadx=20, ipady=20)
        self.l_party.grid(row=0, column=2, pady=5)
        self.f_party.grid(row=0, column=1)
        self.gen_choice.grid(row=1, column=0, padx=5, pady=5)
        self.l_choice.grid(row=1, column=2, pady=5)
        self.f_choice.grid(row=1, column=1)
        self.l_stage = Button(self.F1, text=f"{self.stage}阶段（切换）", command = self.changeStage)
        self.l_stage.grid(row=0, column=0, pady=5)
        def trunc(var: StringVar):
            c = var.get()[-3:]
            var.set(c)
        self.boss_choice = StringVar(value = "111")
        self.boss_choice.trace_add("write", lambda x,y,z,c=self.boss_choice:trunc(c))
        self.JPN = IntVar(value=0)
        Label(self.F1, text="选择boss：").grid(row=2, column=0, pady=5)
        Entry(self.F1, textvariable=self.boss_choice, width=3).grid(row=2, column=1, pady=5)
        Checkbutton(self.F1, text="谜语人模式", variable=self.JPN).grid(row=2, column=2, pady=5)
        button = Button(self.F1, text="计算", command=self.calc)
        button.grid(row=3, column=0, columnspan=3, pady=5)
        self.result = Label(self.F2, text="", font=('TkDefaultFont', 12))
        self.result.pack()
    
    def genChoice(self):
        spider = Spider()
        spider.write_homework(self.stage)
    
    def changeStage(self):
        self.stage = 1 + self.stage % 4
        self.l_stage.config(text=f"{self.stage}阶段（切换）")

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
        self.choice = defaultdict(list)
        with open(self.choice_file, "r", encoding="utf-8") as f:
            choices = f.read().strip().split('\n')
            for choice in choices:
                c = choice.split()
                c[6] = re.sub("[wW]", "", c[6])
                if len(c) != 7 or not c[6].isdigit():
                    self.writeResult("作业文件格式错误")
                    return
                self.choice[c[0][2]].append({"name": c[0], "team": list(map(chara.getCharaId, c[1:6])), "dmg": int(c[6])})
        res = []
        output = []
        boss_choices = ''.join(sorted(self.boss_choice.get()))
        for perm in itertools.product(*[self.choice[boss_choices[i]] for i in range(3)]):
            if(perm[2]["name"] > perm[1]["name"] and perm[1]["name"] > perm[0]["name"]):
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

    def checkAvailability(self, perm: Tuple[dict, dict, dict]) -> Tuple[bool, int]:
        #print(perm[0], perm[1], perm[2])
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
