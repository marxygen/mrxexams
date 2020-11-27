import sqlite3
from params import DB_NAME, tables, CREATE_TABLE_COMMAND, ADD_QUESTION_COMMAND
from datetime import datetime as dt

connection = sqlite3.connect(DB_NAME)
cursor = connection.cursor()

def initialize():
    try:
        _ = [__runcommand(CREATE_TABLE_COMMAND%x, commit=True) for x in list(tables.values()) if not __tablexists(x)]
    except Exception as e:
        print(f'\t[{dt.now()}] Exception occurred:\n\t\t{str(e)}')

def __tablexists(table_name):
    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", [table_name])
    if cursor.fetchone()[0]==1:
    	return True
    else:
    	return None

def __runcommand(command, *, params=[], returnall=False, commit=False, many=False):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    if many is False:
        cursor.execute(command, params)
    else:
        cursor.executemany(command, params)

    if returnall is True:
        return cursor.fetchall()

    if commit is True:
        connection.commit()

    connection.close()

def addquestion(category, text, answer, attachments):
    __runcommand(ADD_QUESTION_COMMAND%category, params=[text, answer, attachments, 0, 0, 0], commit=True)
