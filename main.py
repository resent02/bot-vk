from requests import post, get
import json
import config
import random
from threading import Thread as Th
from time import sleep
import sqlite3 as sq


def request(method, params):
    url = f"https://api.vk.com/method/{method}/?access_token={config.TOKEN}&v=5.103"
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

def writeMsg(peer_id, message):
    pass

th = Th(target=getlongPollThread)
th.start()
sleep(1)

while True:
    update = get(longPoll.genLink()).json()
    longPoll.ts = int(update['ts'])
    for event in update['updates']:
        print(event)
        if event['object']['text'] == "!start":
            print("New message")
