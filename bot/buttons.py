from telebot import types
from params import tables

CATEGORY_CHOOSING_MARKUP = types.ReplyKeyboardMarkup()
for x in tables.values():
    CATEGORY_CHOOSING_MARKUP.row(types.KeyboardButton(x.capitalize()))

def get_words_markup(words):
    words_markup = types.ReplyKeyboardMarkup()
    for x in tables.values():
        words_markup.row(types.KeyboardButton(x.capitalize()))

    return words_markup
