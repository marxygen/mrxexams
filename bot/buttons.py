from telebot import types
from params import tables
import random

def get_category_choosing_markup():
    CATEGORY_CHOOSING_MARKUP = types.ReplyKeyboardMarkup()
    for x in tables.values():
        CATEGORY_CHOOSING_MARKUP.row(types.KeyboardButton(x.capitalize()))
    return CATEGORY_CHOOSING_MARKUP

def get_words_markup(words):
    words_markup = types.ReplyKeyboardMarkup()
    for x in range(len(words)):
        word = random.choice(words)
        words_markup.row(types.KeyboardButton(word[0].capitalize()))
        words.remove(word)
    return words_markup
