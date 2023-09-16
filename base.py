import json
import PySimpleGUI as sg
import requests
from datetime import datetime as dt
from pathlib import Path
from bs4 import BeautifulSoup
from subprocess import call
from shutil import rmtree
import xml.etree.ElementTree as ET
from winreg import OpenKey, EnumValue, HKEY_CURRENT_USER as HKCU, HKEY_LOCAL_MACHINE as HKLM


with OpenKey(HKLM, r'Software\Microsoft\Windows\CurrentVersion\Uninstall\7-Zip') as hh:
    ARCH = Path(EnumValue(hh, 3)[1], '7z')                  # path to 7z
with OpenKey(HKCU, 'Volatile Environment') as hh:
    appdata = EnumValue(hh, 6)[1]
file = Path(appdata, r'Lesta\GameCenter\user_info.xml')
root = ET.parse(file).getroot()                             # find Tanki on computer
for elem in root.iter('instance'):
    if elem.attrib['id'] == 'WOT_RU':
        res = elem.attrib['game_tag']
with OpenKey(HKCU, fr'Software\Microsoft\Windows\CurrentVersion\Uninstall\LGC-{res}') as hh:
    GAMEDIR = EnumValue(hh, 2)[1]
root = ET.parse(Path(GAMEDIR, 'version.xml')).getroot()     # game version
VERSION = root.find('version').text[3:-7]
MODSDIR = Path(GAMEDIR, 'mods', VERSION)
with open('conf.json', encoding='utf-8') as fp:
    data = json.load(fp)
mods = data

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
    create_f = dt.fromtimestamp(Path.stat(real_f[0]).st_ctime)
    upd = dt.strptime(last_m[5:16], '%d %b %Y') > create_f
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
#    return
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
            p = tuple(Path('oops').glob(f'{p}*'))[0]
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
    tmp = [sg.Check('', default=check, disabled=color=='black', key=f'_{mod["name"]}')]                            # checkbutton
    tmp += [sg.Text(mod["name"], text_color=color)]                                       # mod name
    tmp += [sg.Button(f'upd ### v.{mod_version(mod)}', key=mod["name"], visible=upd)]     # update button
    layout += [tmp]
layout += [[sg.Button('Обновить иконки'), sg.Button('Clean XVM')],
            [sg.Button('Применить'), sg.Button('Обновить все')],
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
            if window[mod["name"]].visible:
                inst(mod)
                window[mod["name"]].update(visible=False)
                window[f'_{mod["name"]}'].update(disabled=False)
        continue
    for mod in mods:
        if mod['name'] == event:
            inst(mod)
            window[event].update(visible=False)
            window[f'_{event}'].update(disabled=False)

"""
data = GAMEDIR, ARCH, mods
with open('conf.json', 'w', encoding='utf-8') as fp:
    data = json.dump(data, fp, ensure_ascii=False, indent=4)
"""

window.close()
