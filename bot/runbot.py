from enum import Enum
import telebot
from dbrequests import initialize
from datetime import datetime as dt
import requests
import os

from params import BOT_TOKEN, BOT_ADRESS, ALLOWED_USERS, CURRENT_ACTION, ACTION_DATA, tables, FILES_PATH
from buttons import CATEGORY_CHOOSING_MARKUP

bot = telebot.TeleBot(BOT_TOKEN, 'Markdown')

action = CURRENT_ACTION.IDLE
action_data = dict()

def access_allowed(username):
    return True if username in ALLOWED_USERS else None

def download_file(filename, file_id):
    r = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}', allow_redirects=True)
    file_path = r.json()['result']['file_path']
    r = requests.get(f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}', allow_redirects=True)
    with open(os.path.join(FILES_PATH, filename.lower()), mode='wb+') as f:
        f.write(r.content)

@bot.message_handler(commands=['addq'])
def add_question(message):
    global action
    if action == CURRENT_ACTION.IDLE:
        action = CURRENT_ACTION.CHOOSING_CATEGORY
        bot.send_message(message.chat.id, '--- *New question* ---\nChoose the _category_', reply_markup=CATEGORY_CHOOSING_MARKUP, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text and message.text != '' and not message.text.startswith('/'))
def handle_message(message):
    global action, action_data
    if action == CURRENT_ACTION.CHOOSING_CATEGORY:
        if message.text.lower() in tables.values():
            action_data[ACTION_DATA.CATEGORY_NAME] = message.text
            action = CURRENT_ACTION.QUESTION_TEXT
            bot.send_message(message.chat.id, '--- *Adding question #2* ---\nSend me the text of the question', parse_mode='Markdown')
        else:
            bot.reply_to(message, 'You are in the middle of adding a question.\n Current step: *Choosing the category*\nPlease press the corresponding button.\n*If you wish to exit the adding question mode, type /discard*', parse_mode='Markdown')
    elif action == CURRENT_ACTION.QUESTION_TEXT:
        action_data[ACTION_DATA.QUESTION_TEXT] = message.text
        action = CURRENT_ACTION.ATTACHING_FILES
        bot.send_message(message.chat.id, '--- *Adding question #3* ---\nIf you want to attach any files to this question, send them to me *AS DOCUMENTS*. \nIf not, type /saveq', parse_mode='Markdown')

@bot.message_handler(content_types=['document', 'photo'])
def attach_files(message):
    global action, action_data
    if action == CURRENT_ACTION.ATTACHING_FILES:
        if message.document:
            download_file(message.document.file_name, message.document.file_id)
            action_data[ACTION_DATA.ATTACHMENTS] = action_data[ACTION_DATA.ATTACHMENTS].append(message.document.file_name) if ACTION_DATA.ATTACHMENTS in action_data else [message.document.file_name]
            save_question(message)
        else:
            bot.reply_to(message, 'I see you want to add files to your question, but you didn\'t attach any documents.\nPlease send the files *as documents*', parse_mode='Markdown')
    else:
        bot.reply_to(message, 'I don\'t know why you are sending files to me.')

@bot.message_handler(commands=['saveq'])
def save_question(message):
    global action, action_data
    bot.send_message(message.chat.id, '*Your question has been successfuly added to the database*\nHere\'s what I added:\n\n\t*Category:* %s\n\t*Text*: %s\n\n\nNumber of attachments: %d'%(action_data[ACTION_DATA.CATEGORY_NAME], action_data[ACTION_DATA.QUESTION_TEXT], len(action_data[ACTION_DATA.ATTACHMENTS])), parse_mode='Markdown')

    if len(action_data[ACTION_DATA.ATTACHMENTS]) == 0:
        bot.send_message(message.chat.id, 'No attachments')
        action = CURRENT_ACTION.IDLE
        action_data = dict()
        return

    for file in action_data[ACTION_DATA.ATTACHMENTS]:
        with open(os.path.join(FILES_PATH, file.lower()), 'rb') as f:
            bot.send_document(message.chat.id, f)

    action = CURRENT_ACTION.IDLE
    action_data = dict()

@bot.message_handler(commands=['discard'])
def discard_action(message):
    global action, action_data
    action = CURRENT_ACTION.IDLE
    action_data = dict()
    bot.send_message(message.chat.id, 'All changes discarded')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.send_message(message.chat.id, f'Hey, {message.from_user.username}\nThis bot is solely for use by specific people. \nYou have access to this bot: {access_allowed(message.from_user.username)}')

if __name__ == '__main__':
    print('[%s] Initializing...'%dt.now())
    initialize()
    print('[%s] Bot started at %s'%(dt.now(), BOT_ADRESS))
    bot.polling()
