import PySimpleGUI as sg
from pathlib import Path
import sys, os, signal


print('going on')
os.kill(int(sys.argv[1]), signal.SIGTERM)
try:
    Path('start.py').write_bytes(Path('_start.py').read_bytes())
except FileNotFoundError:
    pass

layout = [[sg.Text('old text')],
           [sg.Button('ok')]]
window = sg.Window('main window', layout)
event, values = window.read()
print(event, values)
window.close()
