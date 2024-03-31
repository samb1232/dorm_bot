from telegram import Bot
from telegram.ext import Application
import config

# Create the Application
application = Application.builder().token(config.API_TOKEN).build()
bot: Bot = application.bot
