import sys, os, requests, telebot
from enum import Enum
from dbrequests import initialize, addquestion, counttables, exportq
from datetime import datetime as dt
from datetime import timedelta
from params import BOT_TOKEN, BOT_ADRESS, ALLOWED_USERS, CURRENT_ACTION, ACTION_DATA, tables, FILES_PATH, DB_NAME, POMODORO_STAGE, MEMTEST_NUMOF_WORDS
from buttons import get_category_choosing_markup, get_words_markup
from threading import Timer
sys.path.append(r'C:\Users\Asus\mrxexams\\')
from misc.getwords import getwords
from misc.parse_cambridge import parse
from Exceptions import StopBot
from dbmerger import merge_db
from doc_manager import create_document
    
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='Markdown')

action = CURRENT_ACTION.IDLE
action_data = dict()
pomodoro_stage = POMODORO_STAGE.NONE
pomodoro_timer = None

memorytest_timer = None
memorytest_message_id = None
memorytest_corr = []
memorytest_words = []
memtest_markup = None

def access_allowed(username):
    return True if username in ALLOWED_USERS else None

def delete_message(chat_id, message_id):
    r = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage?chat_id={chat_id}&message_id={message_id}', allow_redirects=True)
    return r.ok

bot.delete_message = delete_message

def download_file(filename, file_id):
    r = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}', allow_redirects=True)
    file_path = r.json()['result']['file_path']
    r = requests.get(f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}', allow_redirects=True)
    with open(os.path.join(FILES_PATH, filename.lower()), mode='wb+') as f:
        f.write(r.content)

def switch_pomstage(stage, chat_id):
    global pomodoro_stage, bot, pomodoro_timer
    if stage == POMODORO_STAGE.MIN25:
        if pomodoro_timer:
            pomodoro_timer.cancel()
        pomodoro_timer = Timer(25*60, switch_pomstage,args=[POMODORO_STAGE.MIN5, chat_id])
        pomodoro_stage = POMODORO_STAGE.MIN25
        pomodoro_timer.start()
        bot.send_message(chat_id, 'Your pomodoro session has been started.\nUse /pomstop to terminate\nTime remaining: 25 minutes (till %s)'%((dt.now() + timedelta(minutes=25)).time().strftime('%H:%M')))
    elif stage == POMODORO_STAGE.MIN5:
        if pomodoro_timer:
            pomodoro_timer.cancel()
        pomodoro_timer = Timer(5*60, switch_pomstage,args=[POMODORO_STAGE.MIN25, chat_id])
        pomodoro_timer.start()
        pomodoro_stage = POMODORO_STAGE.MIN5
        bot.send_message(chat_id, 'It\'s time to take a 5 minute break! The next session will start at %s'%(dt.now() + timedelta(minutes=5)).time().strftime('%H:%M'))
    else:
        if pomodoro_timer:
            pomodoro_timer.cancel()
            pomodoro_timer = None
        pomodoro_stage = POMODORO_STAGE.NONE

def hide_words(message):
    global memorytest_message_id
    chat_id = message.chat.id
    result = bot.delete_message(chat_id, memorytest_message_id)
    if not result: bot.send_message(chat_id, 'Cannot delete the message')
    bot.send_message(chat_id, 'Time is up.\nSend the words to me in the order they originally were', reply_markup=memtest_markup)
    
    memorytest_message_id = None

def check_words(chat_id):
    global memorytest_corr, memorytest_words, action
    results = ""
    correct = 0

    for (index, word) in enumerate(memorytest_words):
        if word == memorytest_corr[index].capitalize():
            results += '+ %s\n'%word
            correct += 1
        else:
            results += '- %s [%s]\n'%(word, memorytest_corr[index].capitalize())

    results += 'Correct: %d/%d'%(correct, len(memorytest_words))
    results += '\n\nYour memory test has ended. Start one with /memtest'

    bot.send_message(chat_id, results)
    action = CURRENT_ACTION.IDLE
    stop_memtest(None)

@bot.message_handler(commands=['memtest'])
def init_memtest(message):
    global action, memorytest_timer, memorytest_words, memorytest_corr, memorytest_message_id, memtest_markup

    if action != CURRENT_ACTION.IDLE and message:
        bot.reply_to(message, 'You are in the middle of somethind else. Finish it first!')
        return

    words = getwords(MEMTEST_NUMOF_WORDS)

    memtest_markup = get_words_markup(words[::])
    memorytest_words = []

    words_str = ""
    for (word, translation) in words:
        words_str += '*%s* (%s)\n'%(word.capitalize(), translation.capitalize())

    memorytest_corr = [word for word in words]

    action = CURRENT_ACTION.MEMORY_TEST

    if memorytest_timer:
        memorytest_timer.cancel()

    memorytest_timer = Timer(40, hide_words, args=[message])
    memorytest_timer.start()

    memorytest_message_id =  bot.send_message(message.chat.id, '*Memory test*\nMemorize the words below in the order they are presented\n\n%s\nYou have 40 seconds to do this task. This message will disappear and you will be asked to send the words in the correct order using the keyboard or by typing them\nType /memex to stop the test'%words_str, parse_mode='Markdown').message_id

@bot.message_handler(commands=['memex'])
def stop_memtest(message):
    global memorytest_timer, action

    if not memorytest_timer:
        bot.reply_to(message, 'No memory test in progress.\nStart one with /memtest')
        return

    memorytest_timer.cancel()
    memorytest_timer = None
    action = CURRENT_ACTION.IDLE

    if not message: return
    bot.send_message(message.chat.id, 'The memtest has been stopped.\nStart one with /memtest')

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, f'*Help*\n_/stats_ - Show number of questions by category\n_/addq_ - add a new question (triggers adding question procedure)\n_/saveq_ - Save the question\n_/pomstart_ - Enter Pomodoro session (25-5 minutes)\n_/pomstop_ - Exit Pomodoro session\n_/wipedb_ - Wipe the database\n_/export_ - Export all existing questions as JSON', parse_mode='Markdown')

@bot.message_handler(commands=['pomstart'])
def pomstart(message):
    if pomodoro_stage != POMODORO_STAGE.NONE:
        bot.send_message(message.chat.id, 'You are in the middle of other pomodoro session. \nYou have to terminate it first.\nType /pomstop to do so')
        return
    pomodo_stage = POMODORO_STAGE.MIN25
    switch_pomstage(POMODORO_STAGE.MIN25, message.chat.id)

@bot.message_handler(commands=['pomstop'])
def pomstop(message):
    if pomodoro_stage == POMODORO_STAGE.NONE:
        bot.send_message(message.chat.id, 'There\'s no ongoing pomodoro session to terminate.\nStart one with /pomstart')
        return
    switch_pomstage(POMODORO_STAGE.NONE, message.chat.id)
    bot.send_message(message.chat.id, 'Your pomodoro session has been terminated')

@bot.message_handler(commands=['stop'])
def stop_bot(message):
    if not access_allowed(message.from_user.username):
        bot.reply_to(message, 'Access denied')
        return
    _ = exportq(is_backup=True)
    bot.send_message(message.chat.id, 'Bot has been stopped.\nThe backup has been saved')
    raise StopBot

@bot.message_handler(commands=['expq'])
def export_questions(message):
    intended_cats = message.text[5:].split(' ')
    categories = []
    for cat in intended_cats:
        if cat.lower() == 'all':
            categories = tables.values()
            break
        if cat.lower() in tables.values():
            categories.append(cat.lower())
            
    if not categories:
        bot.reply_to(message, 'No valid category names found. Operation aborted')
        return

    bot.send_message(message.chat.id, f'Creating a document for the following categories: {",".join([category.capitalize() for category in categories])}')
    files = create_document(exportq(), categories)
    if not files:
        bot.send_message(message.chat.id, 'Operation cannot be completed')
        return
    for file in files:
        with open(file, 'rb') as f:
            bot.send_document(message.chat.id, f)
        os.remove(file)

@bot.message_handler(commands=['merge'])
def mergedb(message):
    global action
    action = CURRENT_ACTION.MERGING_DB
    bot.reply_to(message, 'Ok, send me the file')

@bot.message_handler(commands=['export'])
def export_questions(message):
    file = exportq()
    with open(file) as f:
        bot.send_document(message.chat.id, f)
    os.remove(file)

@bot.message_handler(commands=['wipedb'])
def wipedb(message):
    export(message)
    os.remove(DB_NAME)
    bot.send_message(message.chat.id, 'The database has been successfuly wiped')
    initialize()

@bot.message_handler(commands=['stats'])
def stats(message):
    answer = ''
    for table, numof_q in list(counttables().items()):
        answer += f'_{table.capitalize()}_: {numof_q}\n'
    bot.send_message(message.chat.id, '*Number of questions by section*\n'+answer, parse_mode='Markdown')

@bot.message_handler(commands=['addq'])
def add_question(message):
    global action
    if action == CURRENT_ACTION.IDLE:
        action = CURRENT_ACTION.CHOOSING_CATEGORY
        bot.send_message(message.chat.id, '--- *New question* ---\nChoose the _category_', reply_markup=get_category_choosing_markup(), parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text and message.text != '' and not message.text.startswith('/'))
def handle_message(message):
    global action, action_data, memorytest_words
    if action == CURRENT_ACTION.CHOOSING_CATEGORY:
        if message.text.lower() in tables.values():
            action_data[ACTION_DATA.CATEGORY_NAME] = message.text
            action = CURRENT_ACTION.QUESTION_TEXT
            bot.send_message(message.chat.id, '--- *Adding question #2* ---\nSend me the text of the question', parse_mode='Markdown')
        else:
            bot.reply_to(message, 'You are in the middle of adding a question.\n Current step: *Choosing the category*\nPlease press the corresponding button.\n*If you wish to exit the adding question mode, type /discard*', parse_mode='Markdown')
    elif action == CURRENT_ACTION.QUESTION_TEXT:
        action_data[ACTION_DATA.QUESTION_TEXT] = message.text
        action = CURRENT_ACTION.QUESTION_ANSWER
        bot.send_message(message.chat.id, '--- *Adding question #3* ---\nSend me the answer to this question', parse_mode='Markdown')
    elif action == CURRENT_ACTION.QUESTION_ANSWER:
        action_data[ACTION_DATA.QUESTION_ANSWER] = message.text
        action = CURRENT_ACTION.ATTACHING_FILES
        action_data[ACTION_DATA.ATTACHMENTS] = list()
        bot.send_message(message.chat.id, '--- *Adding question #4* ---\nIf you want to attach any files to this question, send them to me *AS DOCUMENTS*. \nIf not, type /saveq', parse_mode='Markdown')
    elif action == CURRENT_ACTION.MEMORY_TEST:
        memorytest_words.append(message.text)
        if len(memorytest_words) == MEMTEST_NUMOF_WORDS:
            check_words(message.chat.id)

@bot.message_handler(content_types=['document', 'photo'])
def attach_files(message):
    global action, action_data
    if action == CURRENT_ACTION.ATTACHING_FILES:
        if message.document:
            download_file(message.document.file_name, message.document.file_id)
            action_data[ACTION_DATA.ATTACHMENTS].append(message.document.file_name)
            bot.reply_to(message, 'The attachment has been processed. You can proceed to the next step now.')
        else:
            bot.reply_to(message, 'I see you want to add files to your question, but you didn\'t attach any documents.\nPlease send the files *as documents*', parse_mode='Markdown')
    elif action == CURRENT_ACTION.MERGING_DB:
        name = str(dt.now())[:10]
        download_file(name, message.document.file_id)
        action = CURRENT_ACTION.IDLE
        bot.send_message(message.chat.id, 'Processing started.\nAllow some time to complete. You will receive the message once it\'s done')
        success = merge_db(name)
        if success:
            bot.send_message(message.chat.id, "Processing complete.\nUse /stats to check")
        else:
            bot.reply_to(message, 'Couldn\'t execute the operation. Check if the file is in JSON and try again')
    else:
        bot.reply_to(message, 'I don\'t know why you are sending files to me.')

@bot.message_handler(commands=['saveq'])
def save_question(message):
    global action, action_data
    if not action == CURRENT_ACTION.ATTACHING_FILES:
        bot.reply_to(message, 'You don\'t have any questions to save yet')
        return

    try:
        addquestion(action_data[ACTION_DATA.CATEGORY_NAME], action_data[ACTION_DATA.QUESTION_TEXT], action_data[ACTION_DATA.QUESTION_ANSWER], str(action_data[ACTION_DATA.ATTACHMENTS]))
    except Exception as e:
        bot.send_message(message.chat.id, '*Something went wrong:*\n%s'%str(e), parse_mode='Markdown')
        return

    bot.send_message(message.chat.id, '*Your question has been successfuly added to the database*\nHere\'s what I added:\n\n\t*Category:* %s\n\t*Text*: %s\n\t*Answer*: %s\n\n\tNumber of attachments: %d'%(action_data[ACTION_DATA.CATEGORY_NAME], action_data[ACTION_DATA.QUESTION_TEXT], action_data[ACTION_DATA.QUESTION_ANSWER], len(action_data[ACTION_DATA.ATTACHMENTS])), parse_mode='Markdown')

    if len(action_data[ACTION_DATA.ATTACHMENTS]) == 0:
        bot.send_message(message.chat.id, 'No attachments')
        action = CURRENT_ACTION.IDLE
        action_data = dict()
        return

    if len(action_data[ACTION_DATA.ATTACHMENTS]) != 0:
        for file in action_data[ACTION_DATA.ATTACHMENTS]:
            with open(os.path.join(FILES_PATH, file.lower()), 'rb') as f:
                if file.lower()[-3:] in ['jpg', 'png']:
                    bot.send_photo(message.chat.id, f)
                else:
                    bot.send_document(message.chat.id, f)

    action = CURRENT_ACTION.IDLE
    action_data = dict()

@bot.message_handler(commands=['discard'])
def discard_action(message):
    global action, action_data
    action = CURRENT_ACTION.IDLE
    action_data = dict()
    bot.send_message(message.chat.id, 'All changes discarded')

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.send_message(message.chat.id, f'Hey, {message.from_user.username}\nThis bot is solely for use by specific people. \nYou have access to this bot: {access_allowed(message.from_user.username)}')

if __name__ == '__main__': 
    print('[%s] Initializing...'%dt.now())
    initialize()
    print('[%s] Bot started at %s'%(dt.now(), BOT_ADRESS))
    bot.polling()
