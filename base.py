import PySimpleGUI as sg

sg.theme('PythonPlus')

mods = ['xvm', 'Jimbo', 'lebwa', 'BattleHits', 'analiz broni']
ver = '1.19.1.0'
layout = [[sg.Text('Папка с игрой:')],
          [sg.Input(), sg.FolderBrowse()],
          [sg.Text('Версия игры:   '), sg.Text(ver)]]
layout += [[sg.Check(f'   {i}', default=True, key=i), sg.Button('upd', key=i)] for i in mods]

window = sg.Window('Hello world!', layout)

event, values = window.read()
window.close()

print(event, values)
