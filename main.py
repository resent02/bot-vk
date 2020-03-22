from requests import post, get
import json
import config
import random
from threading import Thread as Th
from time import sleep
from data import *


def request(method, params):
    apiUrl = "https://api.vk.com"
    url = f"{apiUrl}/method/{method}/?access_token={config.TOKEN}&v=5.103"
    for key, value in params.items():
        if isinstance(value, (tuple, list)):
            params.update({key: ",".join(map(str, value))})
        elif value is None:
            params.update({key: ""})
        params.update({key: value})
    print(f"request:params = {params}")
    return post(url, data=params).json()['response']


class LongPoll:
    def lp_check(self):
        param = {
            "group_id": 193126414,
            "lp_version": "5.103",
        }
        r = request("groups.getLongPollServer", param)
        self.key, self.server, self.ts = r.values()

    def genLink(self):
        return f"{self.server}?act=a_check&key={self.key}&ts={self.ts}&wait=0"

longPoll = LongPoll()


def getlongPollThread():
    global longPoll
    while True:
        longPoll.lp_check()
        sleep(15*60)


def writeMsg(peer_id, text):
    method = "messages.send"
    random_id = random.randint(1, 2**31 - 1)
    params = {
        "peer_id": peer_id,
        "random_id": random_id,
        "message": text,
        "oauth": 1,
    }
    return request(method, params)


th = Th(target=getlongPollThread)
th.start()
sleep(1)
sql.init_db()

while True:
    update = get(longPoll.genLink()).json()
    longPoll.ts = int(update['ts'])
    for event in update['updates']:
        event = event['object']
        message = event['text']
        if message == "!start":
            writeMsg(event['peer_id'], "Команды:!name (ФИО)")
        elif message.startswith("!name"):
            print("message")
            addName(f_id=event['peer_id'], name=message[6:])
        elif message.startswith("!class"):
            print("message class")
            addClass(f_id=event['peer_id'], f_class=message[7:])
