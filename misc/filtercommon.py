import json
import time
import os
from datetime import datetime as dt

def save(words):
    with open(os.path.join('commonwords.json'), 'w', encoding="utf-8") as file:
        json.dump(words, file)

def process():
    print(f'[{dt.now()}] Starting')

    words = None

    with open(os.path.join('commonwords.json'), 'r') as file:
        words = json.load(file)

    size = len(words)

    print(f'[{dt.now()}]Loading complete')
    print('%d words found'%size)

    for (index, word) in enumerate(words):
        try:
            if len(word) < 4:
                words.pop(index)
        except Exception as e:
            print('-'*10)
            print('Exception: %s'%e)
            print('-'*10)
            continue

    save(words)

    print('Contains %s words now'%len(words))
    print('Finished')

if __name__ != '__main__':
    raise Exception('This file is to be called explicitly')

while True:
    try:
        process()
        break
    except Exception as e:
        print('\n\nError occurred: \n%s\n\n'%str(e))
        continue
