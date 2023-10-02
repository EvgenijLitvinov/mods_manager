import PySimpleGUI as sg
import requests
from pathlib import Path
from subprocess import call
import json

ARCH = r'D:/apps/7-Zip/7z'

with open('cache.json', encoding='utf-8') as fp:
    cache = json.load(fp)
url = 'https://github.com/EvgenijLitvinov/mods_manager/releases'
etag = requests.get(url, stream=True).headers['ETag']
if not 'etag' in cache or cache['etag'] != etag:
    layout = [[sg.Text('update?')],
            [sg.Button('yes'), sg.Button('no')]]
    window = sg.Window('Hi', layout)
    event, values = window.read()
    print(event, values)
    if event == 'yes':
        print('updating')
        url = 'https://github.com/EvgenijLitvinov/mods_manager/releases/download/v1.0/conf.json'
        Path('conf.json').write_bytes(requests.get(url, stream=True).content)
        url = 'https://github.com/EvgenijLitvinov/mods_manager/releases/download/v1.0/testpsg.exe'
        Path('testpsg.exe').write_bytes(requests.get(url, stream=True).content)
    window.close()


print('going on')

layout = [[sg.Text('old text')],
           [sg.Button('ok')]]
window = sg.Window('main window', layout)
event, values = window.read()
print(event, values)
window.close()

cache['etag'] = etag
with open('cache.json', 'w', encoding='utf-8') as fp:
    json.dump(cache, fp, ensure_ascii=False, indent=4)
