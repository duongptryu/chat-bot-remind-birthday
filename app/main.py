from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberMessageRequest, ViberSubscribedRequest
from viberbot.api.user_profile import UserProfile
import json
import os
import app.Constants as Constants
import datetime
import logging
import app.bot as bot
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
viber = Api(BotConfiguration(
    name=Constants.BOT_NAME,
    avatar=Constants.AVATAR_URL,
    auth_token=Constants.AUTH_TOKEN
))
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('system.log', 'a', 'utf-8')
root_logger.addHandler(handler)

scheduler = BackgroundScheduler()


def read_file():
    try:
        data_file = open(os.getcwd() + '\\app\\data.json', encoding="utf8")
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


def get_user_id(new_user_id):
    try:
        file_reader = open(os.getcwd() + "\\app\\users.txt", "r")
        all_users = file_reader.readlines()
        file_reader.close()

    except:
        pass
    check_exist = False
    for user in all_users:
        if user[-1] == '\n':
            user = user[:-1]
        if user == new_user_id:
            check_exist = True
            break
        else:
            continue
    if not check_exist:
        file_write = open('users.txt', 'a')
        file_write.write("\n")
        file_write.writelines(new_user_id)
        file_reader.close()


def send_list_users(receiver_id, list_users):
    now_date = datetime.datetime.now()
    for user in list_users:
        content = "{name} ".format(name=user.get("name"))
        if user.get("department") is not None:
            content = content + "({department})".format(department=user.get("department"))
        user_date = (datetime.datetime.strptime(user.get("DOB"), "%Y-%m-%d")).strftime("%d/%m/%Y")
        content = content + " {DOB}".format(DOB=user_date)
        while True:
            try:
                viber.send_messages(receiver_id, [TextMessage(text=content)])
                break
            except:
                logging.info("error when send message user: " + user + " in " + now_date.strftime(
                    "%d/%m/%Y, %H:%M:%S"))
                continue


@app.route('/', methods=['POST'])
def incoming():
    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        # lets echo back
        get_user_id(viber_request.sender.id)
        request_content = str(viber_request.message.text).lower()
        if request_content.__eq__(Constants.QUERY_BIRTHDAY_MONTH):
            list_user = get_list_users_in_month()
            if list_user is None or len(list_user) == 0:
                viber.send_messages(viber_request.sender.id,
                                    [TextMessage(text="Tháng này không có nhân viên có sinh nhật \n --end--")])
            else:
                now_date = datetime.datetime.now()
                viber.send_messages(viber_request.sender.id,
                                    [TextMessage(
                                        text="Danh sách nhân viên sinh nhật tháng {0} :".format(now_date.month))])
                send_list_users(viber_request.sender.id, list_user)
                viber.send_messages(viber_request.sender.id,
                                    [TextMessage(text="--end--")])

        elif request_content.__eq__(Constants.QUERY_BIRTHDAY_TODAY):
            list_user = get_list_users_today()
            if list_user is None or len(list_user) == 0:
                viber.send_messages(viber_request.sender.id,
                                    [TextMessage(text="Hôm nay không có nhân viên có sinh nhật \n --end--")])
            else:
                now_date = datetime.datetime.now()
                viber.send_messages(viber_request.sender.id,
                                    [TextMessage(
                                        text="Danh sách nhân viên sinh nhật ngày {0} :".format(
                                            now_date.date().strftime("%d/%m/%Y")))])
                send_list_users(viber_request.sender.id, list_user)
            viber.send_messages(viber_request.sender.id, [TextMessage(text="--end--")])
        elif request_content.__eq__(Constants.QUERY_GET_USER_ID):
            message = viber_request.message
            viber.send_messages(viber_request.sender.id, [
                message
            ])
        else:
            viber.send_messages(viber_request.sender.id,
                                [TextMessage(text="Xin chào " + str(
                                    viber_request.sender.name) +
                                                  "\n - Để lấy danh sách sinh nhật tháng này, gửi:{0}".format(
                                                      Constants.QUERY_BIRTHDAY_MONTH) +
                                                  "\n - Để lấy danh sách sinh nhật hôm nay, gửi: {0}".format(
                                                      Constants.QUERY_BIRTHDAY_TODAY) +
                                                  "\n --end--")])
    elif isinstance(viber_request, ViberSubscribedRequest):
        get_user_id(viber_request.sender.id)
        viber.send_messages(viber_request.get_user.id, [TextMessage(text="thanks for subscribing!")])
    return Response(status=200)


def run_bot():
    # run test
    # scheduler.add_job(bot.run_bot, 'cron', second=30)
    scheduler.add_job(bot.run_bot, 'cron', hour=8)
    scheduler.start()


# if __name__ == "__main__":
#     logging.info("start bot " + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
#     run_bot()
#     app.run(host='0.0.0.0', port=8080, debug=True)
