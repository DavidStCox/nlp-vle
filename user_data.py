import os
import pickle
import hashlib

def sha1hex(s):
    return hashlib.sha1(s).hexdigest()

def get_filename(userid):
    sanitized = sha1hex(userid.encode("utf-8")) # don't *ever* do otherwise
    return os.path.join("user_data", "data_{}.db".format(sanitized))

def get_user_data(userid):
    filename = get_filename(userid)
    if not os.path.exists(filename):
        return UserData(userid)

    with open(filename, "rb+") as f:
        return pickle.load(f)

def save_user_data(data):
    filename = get_filename(data.userid)
    with open(filename, "wb+") as f:
        pickle.dump(data, f)

def get_all_users():
    users = []
    for n in os.listdir("user_data"):
        # Ignore README.md and other files
        if not n.endswith(".db"):
            continue
        with open(os.path.join("user_data", n), "rb+") as f:
            users.append(pickle.load(f))
    return users

def get_test_tasks(userid):
    tasks = [
        {
            "id": 1,
            "name": "Task 1 - Navigation by menu",
            "text": "Which World Heritage Site is in Cambodia?",
            "link": "http://www.wikidata.org/entity/Q2397751",
            "view": "navigation",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 2,
            "name": "Task 2 - Navigation by menu",
            "text": "What is the capital city of Ecuador?",
            "link": "http://www.wikidata.org/entity/Q2900",
            "view": "navigation",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 3,
            "name": "Task 3 - Navigation by menu",
            "text": "Which American President won the Nobel Peace Prize in 2009?",
            "link": "http://www.wikidata.org/entity/Q76",
            "view": "navigation",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 4,
            "name": "Task 4 - Navigation by menu",
            "text": "Who was the 3rd Pope of the Catholic Church?",
            "link": "http://www.wikidata.org/entity/Q80450",
            "view": "navigation",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 5,
            "name": "Task 5 - Navigation by menu",
            "text": "Which country has The Great Wall as a World Heritage Site?",
            "link": "http://www.wikidata.org/entity/Q12501",
            "view": "navigation",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 6,
            "name": "Task 1 - Free text search",
            "text": "Which World Heritage site was designed by Antoni Gaudi for Manuel Vicens?",
            "link": "http://www.wikidata.org/entity/Q746333",
            "view": "search",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 7,
            "name": "Task 2 - Free text search",
            "text": "What is the capital of the U.S. state nicknamed Big Sky Country?",
            "link": "http://www.wikidata.org/entity/Q38733",
            "view": "search",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 8,
            "name": "Task 3 - Free text search",
            "text": "Who was the 43rd Prime Minister of the United Kingdom?",
            "link": "http://www.wikidata.org/entity/Q134982",
            "view": "search",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 9,
            "name": "Task 4 - Free text search",
            "text": "Which Chinese Emperor created the Yuan Dynasty?",
            "link": "http://www.wikidata.org/entity/Q7523",
            "view": "search",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 10,
            "name": "Task 5 - Free text search",
            "text": "Which Swedish Prime Minister won the Nobel Peace Prize in 1921?",
            "link": "http://www.wikidata.org/entity/Q53620",
            "view": "search",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 11,
            "name": "Task 1 - Suggestion-based search",
            "text": "Which Polish saint was the last elected Pope of the 20th century?",
            "link": "http://www.wikidata.org/entity/Q989",
            "view": "search_suggest",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 12,
            "name": "Task 2 - Suggestion-based search",
            "text": "Which French poet won the Nobel Literature Prize in 1901?",
            "link": "http://www.wikidata.org/entity/Q42247",
            "view": "search_suggest",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 13,
            "name": "Task 3 - Suggestion-based search",
            "text": "Which city is the Royal capital of Swaziland?",
            "link": "http://www.wikidata.org/entity/Q101418",
            "view": "search_suggest",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 14,
            "name": "Task 4 - Suggestion-based search",
            "text": "What World Heritage Site in Vietnam is composed of 1600 islands?",
            "link": "http://www.wikidata.org/entity/Q190128",
            "view": "search_suggest",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 15,
            "name": "Task 5 - Suggestion-based search",
            "text": "Which U.S. President had 'Teddy' as his nickname?",
            "link": "http://www.wikidata.org/entity/Q33866",
            "view": "search_suggest",
            "clicks": None,
            "aborted": None,
            "finished": False,
        }
    ]

    def get_hash(s, n=3):
        return int(sha1hex(s), 16) % n

    def shift(l, n):
        return l[n:] + l[:n]

    task_objects = []
    for t in tasks:
        task_objects.append(Task(t["id"], t["name"], t["text"], t["link"], t["view"]))
    order = get_hash(userid.encode("utf-8"))
    return shift(task_objects, order * 5)

class Task:
    def __init__(self, id, name, text, link, view):
        self.id = id
        self.name = name
        self.text = text
        self.link = link
        self.view = view
        self.stats = []
        self.link_found = None
        self.active = False
        self.finished = False
    
    def get_id(self):
        return str(self.id)

    def start(self):
        self.active = True

    def complete(self):
        self.active = False
        self.finished = True

    def is_finished(self):
        return str(self.finished)

    def append_stats(self, stats):
        self.stats.extend(stats)

    def time_elapsed(self):
        if len(self.stats) < 2:
            return "0"
        return str(self.stats[-1]["timestamp"] - self.stats[0]["timestamp"])

    def success(self):
        return str(self.link == self.link_found)

    def number_of_clicks(self):
        return str(len(self.stats))

class UserData:
    def __init__(self, userid):
        self.userid = userid
        self.tasks = get_test_tasks(userid)
        self.tasks[0].active = True
        self.current_task = 0

    def get_task(self):
        return self.tasks[self.current_task]

    def get_tasks(self):
        return self.tasks

    def end_task(self):
        task = self.tasks[self.current_task]
        task.complete()
        self.current_task += 1
        try:
            task = self.tasks[self.current_task]
            task.start()
        except:
            pass
