from enum import Enum

BOT_TOKEN = '1465273002:AAEq-J_XJ2mNUENouApQIPH7URWYXjbnXos'
BOT_ADRESS = '@mrxexams_bot'

DB_NAME = 'database.db'

CURRENT_ACTION = Enum('CURRENT_ACTION', 'IDLE CHOOSING_CATEGORY QUESTION_TEXT QUESTION_ANSWER ATTACHING_FILES TESTING')
ACTION_DATA = Enum('ACTION_DATA', 'CATEGORY_NAME QUESTION_TEXT QUESTION_ANSWER ATTACHMENTS')

FILES_PATH = 'files/'

tables = {
'BIOLOGY':'biology',
'CHEMISTRY':'chemistry',
'PHYSICS':'physics',
'MATH':'math'
}

ALLOWED_USERS = ['marxygen']

CREATE_TABLE_COMMAND = """
CREATE TABLE %s (question text, attached_files_src text, successful_attempts integer,
                   total_attempts integer, hidden integer)
"""
