from telegram import Bot
from telegram.ext import Application
from config import Config

application = Application.builder().token(Config.API_TOKEN).build()
bot: Bot = application.bot
