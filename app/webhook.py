from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
import Constants

viber = Api(BotConfiguration(
    name=Constants.BOT_NAME,
    avatar=Constants.AVATAR_URL,
    auth_token=Constants.AUTH_TOKEN
))
viber.set_webhook("https://f52f33cbbe87.ngrok.io")
