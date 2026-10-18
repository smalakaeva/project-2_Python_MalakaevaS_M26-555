import prompt

def engine():
    print('''
project

Первая попытка запустить проект!

***
<command> exit - выйти из программы
<command> help - справочная информация
Введите команду: help

<command> exit - выйти из программы
<command> help - справочная информация
 ''')
    command = prompt.string('Введите команду: _ ')
    print(command)

