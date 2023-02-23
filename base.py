import os
import json
import PySimpleGUI as sg

with open('conf.json') as fp:
    data = json.load(fp)
GAMEDIR, mods = data
with open(os.path.join(GAMEDIR, 'version.xml')) as px:               # game version
    for _ in range(3):
        VERSION = px.readline()[13:-18]
MODSDIR = os.path.join(GAMEDIR, 'mods', VERSION)
MODSLIST = os.listdir(MODSDIR)

sg.theme('PythonPlus')

def my_color(ff):
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

layout = [[sg.Text('Папка c игрой:')],
          [sg.Input(default_text=GAMEDIR), sg.FolderBrowse()],
          [sg.Text('Версия игры:   '), sg.Text(VERSION)]]
layout += [[sg.Check('', default=True, key=mod["name"]), sg.Text(mod["name"], text_color=my_color(mod['files'])),\
            sg.Button('upd', key=mod["name"])] for mod in mods]
layout += [[sg.Button('Применить'), sg.Button('Обновить все')]]

window = sg.Window('Hello world!', layout)

event, values = window.read()
window.close()

print(event, values)