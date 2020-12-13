import json
import time
from parse_cambridge import parse
import os
from datetime import datetime as dt

def save(words, path):
    with open(os.path.join(path), 'w', encoding="utf-8") as file:
        json.dump(words, file)

def process_words_dictionary():
    print(f'[{dt.now()}] Starting')

    words = None

    with open(os.path.join('words_dictionary.json'), 'r') as file:
        words = json.load(file)

    size = len(words)

    print(f'[{dt.now()}]Loading complete')
    print('%d words found'%size)

    i = 0
    for (word, translation) in list( words.items() ):
        try:
            i += 1

            if not translation in [' ', '', '1', '0', 1, 0]:
                print('- Skipping %s'%word)
                continue

            if len(word) < 3:
                del words[word]
                print('- Dropped \'%s\''%word)
                size -= 1
                continue

            translation = str(parse(word).replace('\n',' '))

            if translation in ['', ' ']:
                print('- Dropped \'%s\' (no translation)'%word)
                del words[word]
                continue

            words[word] = str(translation)
            print('+ %s - %s'%(word, translation))
            time.sleep(2)

            if i >= 20:
                save(words, 'words_dictionary.json')
                i = 0
                print('\n\nFile saved\n\n')
        except Exception as e:
            print('-'*10)
            print('Exception: %s'%e)
            print('-'*10)
            continue

    print('Finished')
    print('The list now contains %d words'%size)

def process_common():
    print(f'[{dt.now()}] Starting')

    words = None
    formatted = dict()

    with open(os.path.join('commonwords.json'), 'r') as file:
        words = json.load(file)

    size = len(words)
    print(f'[{dt.now()}] Loading complete')
    print('%d words found'%size)

    if type(words) == dict:
        print('A dictionary found. The file has already been processed.\nTerminating...')
        return

    i = 0
    for word in words:
        try:
            i += 1

            translation = str(parse(word).replace('\n',' '))

            if translation in ['', ' ']:
                print('- Dropped \'%s\' (no translation)'%word) 
                continue

            formatted[word] = str(translation)
            print('+ %s - %s'%(word, translation))
            time.sleep(2)

        except Exception as e:
            print('-'*10)
            print('Exception: %s'%e)
            print('-'*10)
            continue
    
    save(formatted, 'commonwords.json')
    print('Finished')

if __name__ != '__main__':
    raise Exception('This file is to be called explicitly')

while True:
    file = input('> ')
    try:
        if file == 'wd':
            process()
        elif file == 'common':
            process_common()
        break
    except Exception as e:
        print('\n\nError occurred: \n%s\n\n'%str(e))
        continue
