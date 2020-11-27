from telebot import types
from params import tables

CATEGORY_CHOOSING_MARKUP = types.ReplyKeyboardMarkup()
for x in tables.values():
    CATEGORY_CHOOSING_MARKUP.row(types.KeyboardButton(x.capitalize()))
