import PySimpleGUI as sg
import requests
from pathlib import Path
from subprocess import call
import json

ARCH = r'D:/apps/7-Zip/7z'

with open('cache.json', encoding='utf-8') as fp:
    cache = json.load(fp)
url = 'https://github.com/EvgenijLitvinov/mods_manager/archive/refs/tags/v1.0.zip'
etag = requests.get(url, stream=True).headers['ETag']
if not 'etag' in cache or cache['etag'] != etag:
    layout = [[sg.Text('update?')],
            [sg.Button('yes'), sg.Button('no')]]
    window = sg.Window('Hi', layout)
    event, values = window.read()
    print(event, values)
    if event == 'yes':
        print('updating')
        tmparj = Path('tmparj')
        tmparj.write_bytes(requests.get(url, stream=True).content)
        call(f'{ARCH} x -y {tmparj} -ooops', shell=True)
        Path('conf.json').write_bytes(Path('oops', 'conf.json').read_bytes())
        Path('testpsg.exe').write_bytes(Path('oops', 'testpsg.exe').read_bytes())
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
