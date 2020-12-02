import random
import json

def __readfile(count):
    f = None
    with open('misc/words_dictionary.json', 'rb') as file:
        f = json.load(file)

    w =  [random.choice([x for x in list(f.keys())]) for n in range(count)]
    return [(word, f[word]) for word in w]

def getwords(count):
    words = [ (word, translation) for (word, translation) in __readfile(count) ]
    return words
