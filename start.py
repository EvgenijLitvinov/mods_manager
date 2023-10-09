import requests
from pathlib import Path
from subprocess import call
import json
import os

print('start!')
try:
    with open('cache.json', encoding='utf-8') as fp:
        cache = json.load(fp)
except FileNotFoundError:
    cache = {}

url = 'https://github.com/EvgenijLitvinov/mods_manager/releases/download/v1.0/'
flag = False
for s in ['start.py', 'testpsg.exe', 'conf.json']:
    etag = requests.get(url+s, stream=True).headers['ETag']
    if not s in cache or cache[s] != etag:
        flag = True
        print('updating', s)
        if s == 'start.py':
            Path('_start.py').write_bytes(requests.get(url+s, stream=True).content)
        else:
            Path(s).write_bytes(requests.get(url+s, stream=True).content)
        cache[s] = etag

if flag:
    with open('cache.json', 'w', encoding='utf-8') as fp:
        json.dump(cache, fp, ensure_ascii=False, indent=4)

call(f'testpsg.exe {os.getpid()}', shell=True)
