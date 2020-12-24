import sqlite3
from params import (DB_NAME, tables, CREATE_TABLE_COMMAND, ADD_QUESTION_COMMAND, NUMBEROF_ENTRIES,
 FILES_PATH, GET_ALL_ENTRIES_IN, BACKUPS_PATH)
from datetime import datetime as dt
import os
import json

def initialize():
    try:
        _ = [__runcommand(CREATE_TABLE_COMMAND%x, commit=True) for x in list(tables.values()) if not __tablexists(x)]
    except Exception as e:
        print(f'\t[{dt.now()}] Exception occurred:\n\t\t{str(e)}')

def __tablexists(table_name):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", [table_name])
    if cursor.fetchone()[0]==1:
        connection.close()
        return True
    else:
        return None
        connection.close()

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
    __runcommand(ADD_QUESTION_COMMAND%category, params=[text, answer, attachments, 0, 0, 0, dt.now()], commit=True)

def counttables():
    numbers = None
    try:
        numbers = {x:(__runcommand(NUMBEROF_ENTRIES%x, returnall=True))[0][0] for x in list(tables.values())}
    except Exception as e:
        print(f'\t[{dt.now()}] Exception occurred:\n\t\t{str(e)}')
    finally:
        return numbers

def getqin(category):
    try:
        return  __runcommand(GET_ALL_ENTRIES_IN%category, returnall=True)
    except Exception as e:
        print(f'\t[{dt.now()}] Exception occurred:\n\t\t{str(e)}')
        return []

def exportq(is_backup=False):
    filename = f'Report dd {str(dt.now())[:10]}.json'
    path = os.path.join(FILES_PATH, filename)

    if is_backup:
        filename = f'BACKUP_{str(dt.now())[:10]}.json'
        path = os.path.join(BACKUPS_PATH, filename)
        
    jsons = []
    for category in list(tables.values()):
        jsons.append({'category':category, 'items':getqin(category)})

    with open(path, 'w+') as f:
        json.dump(jsons, f)

    return path


