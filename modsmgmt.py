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
import logging as lg

# ------------------ checking for updates -----------------------------------
lg.basicConfig(level=lg.DEBUG, filename='python.log', datefmt='%d.%m.%Y %H:%M:%S',
               format='%(asctime)s %(levelname)s %(message)s')
lg.info('-' * 51)

url = 'https://github.com/EvgenijLitvinov/mods_manager/releases/download/v1.0/mysetup.exe'
flag = False
cache = {}
try:
    res = requests.get(url, stream=True)
    lg.info(f"etag's request status-code: {res.status_code}")
    etag = res.headers['ETag']
except:
    lg.exception('etag not received')
try:
    with open('cache.json', encoding='utf-8') as fp:
        cache = json.load(fp)
except FileNotFoundError:
    flag = True
    cache['ETag'] = etag
    lg.info('ceating cache.json')
except:
    lg.exception('uncaught exception')
    lg.info("creating cache['ETag'] = '~'")
    cache['ETag'] = '~'
if cache['ETag'] != etag:
    lg.info('updating')
    window = sg.Window('Updating!', [[sg.Text('..............UPDATING...............')]])
    event, values = window.read()
    window.close()
    Path('mysetup.exe').write_bytes(requests.get(url, stream=True).content)
    cache['ETag'] = etag
    try:
        with open('cache.json', 'w', encoding='utf-8') as fp:
            json.dump(cache, fp, ensure_ascii=False, indent=4)
    except:
        lg.exception('cache is not saved to file')
    call('mysetup.exe', shell=True)
# ---------------- search for the 7z and Tanki on computer ------------------------
if not '_7z' in cache:
    flag = True
    with OpenKey(HKLM, r'Software\Microsoft\Windows\CurrentVersion\Uninstall\7-Zip') as hh:
        cache['_7z'] = EnumValue(hh, 3)[1] + '7z'
    with OpenKey(HKCU, 'Volatile Environment') as hh:
        appdata = EnumValue(hh, 6)[1]
    file = Path(appdata, r'Lesta\GameCenter\user_info.xml')
    root = ET.parse(file).getroot()
    for elem in root.iter('instance'):
        if elem.attrib['id'] == 'WOT_RU':
            res = elem.attrib['game_tag']
    with OpenKey(HKCU, fr'Software\Microsoft\Windows\CurrentVersion\Uninstall\LGC-{res}') as hh:
        cache['Tanki'] = EnumValue(hh, 2)[1]
    lg.info(f"7z found: {cache['_7z']}")
    lg.info(f"Tanki found: {cache['Tanki']}")

root = ET.parse(Path(cache['Tanki'], 'version.xml')).getroot()
VERSION = root.find('version').text[3:-7]                   # game version
MODSDIR = Path(cache['Tanki'], 'mods', VERSION)
lg.info(f'VERSION: {VERSION}')
lg.info(f'MODSDIR: {MODSDIR}')
try:
    with open('conf.json', encoding='utf-8') as fp:
        mods = json.load(fp)
except:
    lg.exception('mods is not loaded from file')

sg.theme('PythonPlus')

def foo(mod):                                               # for rendering
    url = mod['url']
    if mod['name'] == 'Боевые раны':
        try:
            res = requests.get(url, stream=True)
            soup = BeautifulSoup(res.content, 'lxml')
            s = soup.find('a', 'down_new')['href']
            mod['dwn'] = url = s[s.find('https') : s.find('&')]
        except:
            lg.exception('failed to install "Боевые раны"')
            lg.info(f'status_code: {res.status_code}')
            return False, 'red', False
    for file in mod['files']:
        real_f = tuple(MODSDIR.glob(f'{file}*'))
        if not real_f:
            return False, 'black', True                     # check, color, upd
    check = real_f[0].suffix == '.wotmod'
    try:
        res = requests.get(url, stream=True)
        last_m = res.headers['last-modified']
    except:
        lg.exception(f"Could not check mod date ({mod['name']})")
        lg.info(f'status_code: {res.status_code}')
        return False, 'red', False
    create_f = dt.fromtimestamp(Path.stat(real_f[0]).st_ctime)
    upd = dt.strptime(last_m[5:16], '%d %b %Y') > create_f
    return check, 'white', upd                              # check, color, upd

def mod_version(mod):                                       # version of mod
    if mod['name'] == 'xvm':
        try:
            res = requests.get(mod['v_url'])
            return res.text.strip()
        except:
            lg.exception(f"mod version not found ({mod['name']})")
            lg.info(f'status_code: {res.status_code}')
            return '❌'
    try:
        res = requests.get(mod['v_url'], stream=True)
        soup = BeautifulSoup(res.content, 'lxml')
    except:
        lg.exception(f"mod version not found ({mod['name']})")
        lg.info(f'status_code: {res.status_code}')
        return '❌'
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
    try:
        res = requests.get(url, stream=True)
        tmparj.write_bytes(res.content)
    except:
        lg.exception(f"failed to download {mod['name']}")
        lg.info(f'status_code: {res.status_code}')
        return
    if not 'pathes' in mod:
        call(f'{cache["_7z"]} x -y {tmparj} -i!mods -o{cache["Tanki"]}', shell=True)
    else:
        call(f'{cache["_7z"]} x -y {tmparj} -ooops > nul', shell=True)
        for p in mod['pathes']:
            p = tuple(Path('oops').glob(f'{p}*'))[0]
            if p.is_dir():
                call(f'xcopy /y /e {p} {Path(cache["Tanki"], p.parts[-1])} > nul', shell=True)
            else:
                Path(MODSDIR, p.parts[-1]).write_bytes(p.read_bytes())
        rmtree('oops')
    tmparj.unlink()
# -------------------------------------------------------------------------------
layout = [[sg.Text('Папка c игрой:')],
          [sg.Input(default_text=cache['Tanki']), sg.FolderBrowse()],
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

if flag:
    try:
        with open('cache.json', 'w', encoding='utf-8') as fp:
            json.dump(cache, fp, ensure_ascii=False, indent=4)
    except:
        lg.exception('cache is not saved to file')

window.close()
