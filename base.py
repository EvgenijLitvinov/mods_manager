#import os
import json
import PySimpleGUI as sg
from urllib.request import urlopen, Request, urlretrieve
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from subprocess import call
from shutil import rmtree

with open('conf.json', encoding='utf-8') as fp:
    data = json.load(fp)
GAMEDIR, ARCH, mods = data                                  # ARCH - path to 7z
with open(Path(GAMEDIR, 'version.xml')) as px:              # game version
    for _ in range(3):
        VERSION = px.readline()[13:-18]
MODSDIR = Path(GAMEDIR, 'mods', VERSION)

sg.theme('PythonPlus')

def my_color(mod):                                  # mod's color at mods list
    if real_f.exists():
        if not mod['date']:
            mod['date'] = datetime.fromtimestamp(Path.stat(real_f).st_ctime).strftime('%d %b %Y')
        return 'white'
    else:
        if not mod['date']:
            mod['date'] = '01 Jan 2023'
        return 'black'

def upd(mod):                                       # Last-Modified
    url = mod['url']
    if 'cls' in mod:
        soup = BeautifulSoup(requests.get(url, stream=True).content, 'lxml')
        s = soup.find('a', mod['cls'])['href']
        url = s[s.find('https') : s.find('&')]
        mod['url0'] = url
    res = requests.get(url, stream=True).headers['last-modified']
    if datetime.strptime(res[5:16], '%d %b %Y') > datetime.strptime(mod['date'], '%d %b %Y'):
        mod['flag'] = True
        return True
    else:
        return False
# ------------------------------- download & install mod -------------------    
def inst(mod):
    sg.popup_ok(f'Installing {mod["name"]}', background_color='red', no_titlebar=True)
    if 'url0' in mod:
        url = mod['url0']
    else:
        url = mod['url']
    tmparj = Path('tmparj')
    tmparj.write_bytes(requests.get(url, stream=True).content)
    if not 'pathes' in mod:
        call(f'{ARCH} x -y {tmparj} -i!mods -o{GAMEDIR}', shell=True)
    else:
        call(f'{ARCH} x -y {tmparj} -ooops > nul', shell=True)
        for p in mod['pathes']:
            p = Path('oops', p)
            if p.is_dir():
                call(f'xcopy /y /e {p} {Path(MODSDIR, p.parts[-1])} > nul', shell=True)
            else:
                Path(MODSDIR, p.parts[-1]).write_bytes(p.read_bytes())
        rmtree('oops')
    tmparj.unlink()
    mod['flag'] = False
    mod['date'] = datetime.now().strftime('%d %b %Y')
# -------------------------------------------------------------------------------
layout = [[sg.Text('Папка c игрой:')],
          [sg.Input(default_text=GAMEDIR), sg.FolderBrowse()],
          [sg.Text('Версия игры:   '), sg.Text(VERSION)]]
for mod in mods:
    real_f = Path('}|{ek@')
    for file in MODSDIR.glob(f"{mod['files'][0]}*"):
        real_f = file
    tmp = [sg.Check('', default=real_f.suffix == '.wotmod', key=mod["name"])]     # checkbutton
    tmp += [sg.Text(mod["name"], text_color=my_color(mod))]                     # mod name
    tmp += [sg.Button('upd', key=mod["name"])] * upd(mod)                       # update button
    layout += [tmp]
layout += [[sg.Button('Применить'), sg.Button('Обновить все')],
           [sg.CloseButton('CLOSE', button_color='red')]]

window = sg.Window('Hello world!', layout)

while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED:
        break
    if event == 'Применить':
        continue
    if event == 'Обновить все':
        for mod in mods:
            if mod['flag']:
                inst(mod)
                pos = mods.index(mod)
                window[mod["name"]+str(pos)].update(visible=False)
        continue
    for mod in mods:
        if mod['name'] == event[:-1]:
            inst(mod)
            window[event].update(visible=False)

data = GAMEDIR, ARCH, mods
with open('conf.json', 'w', encoding='utf-8') as fp:
    data = json.dump(data, fp, ensure_ascii=False, indent=4)

window.close()
