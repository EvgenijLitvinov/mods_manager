#import os
import json
import PySimpleGUI as sg
#from urllib.request import urlopen, Request, urlretrieve
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

def foo(mod):                                               # for rendering
    url = mod['url']                                        # Last-Modified
    if mod['name'] == 'Боевые раны':
        soup = BeautifulSoup(requests.get(url, stream=True).content, 'lxml')
        s = soup.find('a', 'down_new')['href']
        url = s[s.find('https') : s.find('&')]
        mod['dwn'] = url
    for file in mod['files']:
        real_f = tuple(MODSDIR.glob(f'{file}*'))
        if not real_f:
            return False, 'black', True                     # check, color, upd
    check = real_f[0].suffix == '.wotmod'
    last_m = requests.get(url, stream=True).headers['last-modified']
    create_f = datetime.fromtimestamp(Path.stat(real_f[0]).st_ctime).strftime('%d %b %Y')
    upd = datetime.strptime(last_m[5:16], '%d %b %Y') > create_f
    return check, 'white', upd                              # check, color, upd

def mod_version(mod):                               # version of mod
    if mod['name'] == 'xvm':
        return requests.get(mod['v_url']).text.strip()
    soup = BeautifulSoup(requests.get(mod['v_url'], stream=True).content, 'lxml')
    if mod['v_url'][:16] == 'https://wotspeak':
        return soup.find('label', 'patch').text
    return soup.find('div', 'heading-mat').text.strip().split(' ')[-1]      # wotsite.net

# ------------------------------- download & install mod -------------------    
def inst(mod):
    sg.popup_ok(f'Installing {mod["name"]}', background_color='red', no_titlebar=True)
    url = mod['url']
    if 'dwn' in mod:
        url = mod['dwn']
    tmparj = Path('tmparj')
    tmparj.write_bytes(requests.get(url, stream=True).content)
    if not 'pathes' in mod:
        call(f'{ARCH} x -y {tmparj} -i!mods -o{GAMEDIR}', shell=True)
    else:
        call(f'{ARCH} x -y {tmparj} -ooops > nul', shell=True)
        for p in mod['pathes']:
            p = Path('oops', p)
            if p.is_dir():
                call(f'xcopy /y /e {p} {Path(GAMEDIR, p.parts[-1])} > nul', shell=True)
            else:
                Path(MODSDIR, p.parts[-1]).write_bytes(p.read_bytes())
        rmtree('oops')
    tmparj.unlink()
# -------------------------------------------------------------------------------
layout = [[sg.Text('Папка c игрой:')],
          [sg.Input(default_text=GAMEDIR), sg.FolderBrowse()],
          [sg.Text('Версия игры:   '), sg.Text(VERSION)]]
for mod in mods:
    check, color, upd = foo(mod)
    tmp = [sg.Check('', default=check, key=mod["name"])]                            # checkbutton
    tmp += [sg.Text(mod["name"], text_color=color)]                                 # mod name
    tmp += upd * [sg.Button('upd', key=mod["name"]), sg.Text(mod_version(mod))]     # update button
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
        print(event)
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

"""
data = GAMEDIR, ARCH, mods
with open('conf.json', 'w', encoding='utf-8') as fp:
    data = json.dump(data, fp, ensure_ascii=False, indent=4)
"""

window.close()
