import json, os
from dbrequests import addquestion
from datetime import datetime as dt
from params import FILES_PATH

def merge_db(filename):
    try:
        with open(os.path.join(FILES_PATH, filename.lower()), 'rb') as f:
            js = list(json.load(f))
            questions = []
            for element in js:
                category = element['category']
                for item in element['items']:
                    text = item[0]
                    answer = item[1]
                    attachments = item[2]

                    questions.append([category, text, answer, attachments])

            for question in questions:
                addquestion(*question)

            return True
    except Exception as e:
        print(e)
        return False