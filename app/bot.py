import logging
import datetime
import json
import app.Constants as Constants
import requests

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('system.log', 'a', 'utf-8')
root_logger.addHandler(handler)


def read_file():
    try:
        data_file = open('data.json', encoding="utf8")
        data = json.load(data_file)
        data_file.close()
        return data
    except:
        logging.info("error read data")
        return None


def get_list_users_today():
    data = read_file()
    if data is None:
        return None
    list_user = []
    now_date = datetime.datetime.now().date()
    for user in data:
        user_DOB = datetime.datetime.strptime(user.get("DOB"), "%Y-%m-%d").date()

        if user_DOB == now_date:
            list_user.append(user)
        else:
            continue
    return list_user


def get_list_users_in_month():
    data = read_file()
    if data is None:
        return None
    list_user = []
    now_month = datetime.datetime.now().month
    for user in data:
        user_month = (datetime.datetime.strptime(user.get("DOB"), "%Y-%m-%d")).date().month
        if user_month == now_month:
            list_user.append(user)
        else:
            continue
    return list_user


def create_broadcast_message(data):
    now_date = datetime.datetime.now()
    logging.info(" send_message " + now_date.strftime("%d/%m/%Y, %H:%M:%S"))
    content = "Danh sách nhân viên sinh nhật tháng {0}".format(now_date.month)
    # send_message(content)
    send_broadcast(content)
    for user in data:
        content = "{name} ".format(name=user.get("name"))
        if user.get("department") is not None:
            content = content + "({department})".format(department=user.get("department"))
        user_date = (datetime.datetime.strptime(user.get("DOB"), "%Y-%m-%d")).strftime("%d/%m/%Y")
        content = content + " {DOB}".format(DOB=user_date)
        try:
            # send_message(content)
            send_broadcast(content)
        except:
            logging.info("error when send message user: " + user + " in " + now_date.strftime("%d/%m/%Y, %H:%M:%S"))

    content = "-- end --"
    # send_message(content)
    send_broadcast(content)


def create_message(data):
    now_date = datetime.datetime.now()
    logging.info(" send_message " + now_date.strftime("%d/%m/%Y, %H:%M:%S"))
    for user in data:
        content = "Chúc mừng sinh nhật {0}".format(user.get("name"))
        receiver_id = user.get("viber_id")
        if receiver_id is not None:
            try:
                send_message(content, receiver_id)
            except:
                logging.info("error when send message user: " + user + " in " + now_date.strftime("%d/%m/%Y, %H:%M:%S"))


def get_users_id():
    list_ids = []
    try:
        file_reader = open("users.txt", "r")
        all_users = file_reader.readlines()
        file_reader.close()
    except:
        pass
    for user in all_users:
        if user[-1] == '\n':
            user = user[:-1]
        list_ids.append(user)
    return list_ids


def send_message(content: str, receiver_id: str):
    header = {
        "Accept": "*/*",
        "X-Viber-Auth-Token": Constants.AUTH_TOKEN,
        "Content-Type": "application/json"
    }
    viber_bot = {
        "receiver": receiver_id,
        "min_api_version": 1,
        "sender": Constants.SENDER,
        "tracking_data": "tracking data",
        "type": "text",
        "text": content
    }
    payload = json.dumps(viber_bot)
    result = requests.post(headers=header, url=Constants.URL_SEND_MESSAGE, data=payload)
    return result.status_code


def send_broadcast(content: str):
    header = {
        "Accept": "*/*",
        "X-Viber-Auth-Token": Constants.AUTH_TOKEN,
        "Content-Type": "application/json"
    }
    list_ids = get_users_id()
    viber_bot = {
        "sender": Constants.SENDER,
        "min_api_version": 2,
        "type": "text",
        "broadcast_list": list_ids,
        "text": content
    }
    payload = json.dumps(viber_bot)
    result = requests.post(headers=header, url=Constants.URL_SEND_BROADCAST, data=payload)
    return result.status_code


def run_bot():
    logging.info("start bot " + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
    if datetime.date.today().day == 1:
        list_users = get_list_users_in_month()
        create_broadcast_message(list_users)
    list_users = get_list_users_today()
    create_message(list_users)


#
# schedule.every().day.at("08:00").do(run_bot)
# schedule.every(10).seconds.do(run_bot)
# while True:
#     schedule.run_pending()
#     time.sleep(10)

# if __name__ == "__main__":
#     run_bot()
