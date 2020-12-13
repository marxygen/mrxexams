import random
import json

def __readfile(count):
    f = None
    with open(r'C:\Users\Asus\mrxexams\misc\commonwords.json', 'r') as file:
        f = json.load(file)

    w =  [random.choice(f) for x in range(count)]
    return [word for word in w]

def getwords(count):
    words = [ word for word in __readfile(count) ]
    return words
