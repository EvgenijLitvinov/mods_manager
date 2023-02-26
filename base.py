import os
import json
import PySimpleGUI as sg
from urllib.request import urlopen, Request
import time

with open('conf.json', encoding='utf-8') as fp:
    data = json.load(fp)
GAMEDIR, mods = data
with open(os.path.join(GAMEDIR, 'version.xml')) as px:               # game version
    for _ in range(3):
        VERSION = px.readline()[13:-18]
MODSDIR = os.path.join(GAMEDIR, 'mods', VERSION)
MODSLIST = os.listdir(MODSDIR)

sg.theme('PythonPlus')

def my_color(ff):                   # mod's color at mods list
    count = 0
    for f in ff:
        for m in MODSLIST:
            if f in m:
                count += 1
                break
    if count == len(ff):
        return 'white'
    else:
        return 'black'

def ch(mod):                                        # enable or disable
    if mod['files'][0] + '.wotmod' in MODSLIST:
        return True

def upd(mod):                                       # Last-Modified
    if not mod.get('url'):
        return False
    res = urlopen(Request(mod['url'], headers={"User-Agent": "Mozilla/5.0"})).info()['Last-Modified']
    if time.strptime(res, '%a, %d %b %Y %H:%M:%S %Z') > time.strptime(mod['date'], '%a, %d %b %Y %H:%M:%S %Z'):
        return True

layout = [[sg.Text('Папка c игрой:')],
          [sg.Input(default_text=GAMEDIR), sg.FolderBrowse()],
          [sg.Text('Версия игры:   '), sg.Text(VERSION)]]
for mod in mods:
    tmp = [sg.Check('', default=ch(mod), key=mod["name"])]
    tmp += [sg.Text(mod["name"], text_color=my_color(mod['files']))]
    if upd(mod):
        tmp += [sg.Button('upd', key=mod["name"])]
    layout += [tmp]
layout += [[sg.Button('Применить'), sg.Button('Обновить все')],
           [sg.Button('CLOSE', button_color='red')]]

window = sg.Window('Hello world!', layout)

event, values = window.read()
window.close()

print(event, values)