import os
import json
import PySimpleGUI as sg
from urllib.request import urlopen, Request
from datetime import datetime
from pathlib import Path

with open('conf.json', encoding='utf-8') as fp:
    data = json.load(fp)
GAMEDIR, mods = data
with open(os.path.join(GAMEDIR, 'version.xml')) as px:               # game version
    for _ in range(3):
        VERSION = px.readline()[13:-18]
MODSDIR = os.path.join(GAMEDIR, 'mods', VERSION)
MODSLIST = os.listdir(MODSDIR)

sg.theme('PythonPlus')

def ch(mod):                                        # enable or disable
    if mod['files'][0] + '.wotmod' in MODSLIST:
        return True

def my_color(mod):                                  # mod's color at mods list
    if mod['files'][0] in map(lambda x: x[:-7], MODSLIST):
        if not mod['date']:
            mod['date'] = datetime.fromtimestamp(os.path.getctime(mod['files'][0])).strftime('%d %b %Y')
        return 'white'
    else:
        if not mod['date']:
            mod['date'] = '01 Jan 2023'
        return 'black'

def upd(mod):                                       # Last-Modified
    if not 'url' in mod:
        return False
    res = urlopen(Request(mod['url'], headers={"User-Agent": "Mozilla/5.0"})).info()['Last-Modified']
    if datetime.strptime(res[5:16], '%d %b %Y') > datetime.strptime(mod['date'], '%d %b %Y'):
        return True
    else:
        return False

layout = [[sg.Text('Папка c игрой:')],
          [sg.Input(default_text=GAMEDIR), sg.FolderBrowse()],
          [sg.Text('Версия игры:   '), sg.Text(VERSION)]]
for mod in mods:
    tmp = [sg.Check('', default=ch(mod), key=mod["name"])]                  # checkbutton
    tmp += [sg.Text(mod["name"], text_color=my_color(mod))]                 # mod name
    tmp += [sg.Button('upd', key=mod["name"])] * upd(mod)                   # update button
    layout += [tmp]
layout += [[sg.Button('Применить'), sg.Button('Обновить все')],
           [sg.Button('CLOSE', button_color='red')]]

window = sg.Window('Hello world!', layout)

event, values = window.read()
window.close()

print(event, values)