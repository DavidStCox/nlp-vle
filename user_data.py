import os
import pickle

# poor man's sqlite. Fix this Christian :-)
def get_user_data(userid):
    filename = "user_data/data_{}.db".format(userid)
    if not os.path.exists(filename):
        return UserData(userid)

    with open(filename, "rb+") as f:
        return pickle.load(f)

def save_user_data(data):
    filename = "user_data/data_{}.db".format(data.userid)
    with open(filename, "wb+") as f:
        pickle.dump(data, f)

def get_all_users():
    users = []
    for n in os.listdir("user_data"):
        with open(os.path.join("user_data", n), "rb+") as f:
            users.append(pickle.load(f))
    return users

def get_test_tasks(userid):

    tasks = [
        {
            "id": 1,
            "name": "Task 1 - Navigation by menu",
            "text": "Cambodia has what World Heritage Site?",
            "link": "http://www.wikidata.org/entity/Q45949",
            "view": "navigation",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 2,
            "name": "Task 2 - Navigation by menu",
            "text": "The Great Wall of China is in which country's World Heritage Sites list?",
            "link": "http://www.wikidata.org/entity/Q12501",
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
            "text": "Where is the Stave Church in Norway's list of World Heritage Sites?",
            "link": "http://www.wikidata.org/entity/Q210678",
            "view": "navigation",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 6,
            "name": "Task 1 - Free text search",
            "text": "Does Poland have a salt mine as a World Heritage site?",
            "link": "http://www.wikidata.org/entity/Q454019",
            "view": "search",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 7,
            "name": "Task 2 - Free text search",
            "text": "What U.S. state has the capital of Annapolis?",
            "link": "http://www.wikidata.org/entity/Q28271",
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
            "text": "Kublai Khan was the Emperor of which Chinese Dynasty?",
            "link": "http://www.wikidata.org/entity/Q7523",
            "view": "search",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 10,
            "name": "Task 5 - Free text search",
            "text": "Which type of Nobel Prize did Hjalmar Branting win?",
            "link": "http://www.wikidata.org/entity/Q53620",
            "view": "search",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 11,
            "name": "Task 1 - Suggestion-based search",
            "text": "Who was the last Pope of the 20th century?",
            "link": "http://www.wikidata.org/entity/Q989",
            "view": "search_suggest",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 12,
            "name": "Task 2 - Suggestion-based search",
            "text": "Which Nobel Prize did Sully Prudhomme win?",
            "link": "http://www.wikidata.org/entity/Q42247",
            "view": "search_suggest",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 13,
            "name": "Task 3 - Suggestion-based search",
            "text": "What is the capital of Swaziland?",
            "link": "http://www.wikidata.org/entity/Q101418",
            "view": "search_suggest",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 14,
            "name": "Task 4 - Suggestion-based search",
            "text": "In which country is Ha Long Bay?",
            "link": "http://www.wikidata.org/entity/Q190128",
            "view": "search_suggest",
            "clicks": None,
            "aborted": None,
            "finished": False,
        },
        {
            "id": 15,
            "name": "Task 5 - Suggestion-based search",
            "text": "Which President had 'Teddy' as his nickname?",
            "link": "http://www.wikidata.org/entity/Q33866",
            "view": "search_suggest",
            "clicks": None,
            "aborted": None,
            "finished": False,
        }
    ]

    def get_hash(s, n=3):
        import hashlib
        return int(hashlib.sha1(s).hexdigest(), 16) % n

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
