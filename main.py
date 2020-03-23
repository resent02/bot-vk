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
            writeMsg(event['peer_id'], "Команды:\n!name (ФИО)\n!class (Число и буква Номер школы)\n!numb (Номер услуги)\n!date (Название предмета и дата в формате ДД.ММ.ГГ)\nДля отправки заявки напишите !pull")
            writeMsg(event['peer_id'], "После отправки заявки перечислите деньги с указанием в комментариях ваше ФИО! Иначе оценка не поставится!")
            writeMsg(event['peer_id'], "Реквизиты:\nСбербанк - 5469 0600 2619 1251")
            writeMsg(event['peer_id'], "Пример:\n!name Иванов Иван Иванович\n!class 10Б 31\n!numb 4\n!date Математика 23.03.20")
            writeMsg(event['peer_id'], "Список услуг можно увидеть на стене группы")
        elif message.startswith("!name"):
            print("message")
            addName(f_id=event['peer_id'], name=message[6:])
        elif message.startswith("!class"):
            print("message class")
            addClass(f_id=event['peer_id'], f_class=message[7:])
        elif message.startswith("!numb"):
            numChoose(event['peer_id'], message[6:])
        elif message.startswith("!date"):
            addDate(event['peer_id'], message[6:])
        elif message.startswith('!заявки') and event['peer_id'] == 418060855:
            print(getRequests())
            if getRequests() == []:
                writeMsg(event['peer_id'], "Заявок нету")
            else:
                for costRequest in getRequests():
                    writeMsg(418060855, f"Айди пользователя:{costRequest[0]}\nИмя:{costRequest[1]}\nКласс:{costRequest[2]}\nНомер услуги:{costRequest[3]}\nПредмет и дата:{costRequest[4]}")
        elif message.startswith('!pull'): # Отображение Текущих заявок!
            for costRequest in getRequests():
                if event['peer_id'] in costRequest:
                    if None in costRequest:
                        writeMsg(event['peer_id'], "Вы забыл заполнить поле\nВаша заявка выглядит вот так:")
                        writeMsg(event['peer_id'], f"Имя:{costRequest[1]}\nКласс:{costRequest[2]}\nНомер услуги:{costRequest[3]}\nПредмет и дата:{costRequest[4]}")
                    else:
                        writeMsg(418060855, f"Айди пользователя:{costRequest[0]}\nИмя:{costRequest[1]}\nКласс:{costRequest[2]}\nНомер услуги:{costRequest[3]}\nПредмет и дата:{costRequest[4]}")
                        writeMsg(event['peer_id'], "Заявка отправлена , выставление оценки произойдет после оплаты в течении 1-3часов")
        elif message.startswith('!delete') and event['peer_id'] == 418060855:
            if delStr(message[8:]):
                writeMsg(event['peer_id'], "Завяка удалена")
            else:
                writeMsg(event['peer_id'], "Заявка не удалена")
