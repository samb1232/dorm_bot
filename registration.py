import datetime
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

import menu_functions
import strings
from enumerations import MenuCallbackButtons, ConversationStates
from database.db_operations import db_helper

logger = logging.getLogger(__name__)


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_full_name = update.message.text
    name_splits = user_full_name.split(' ')
    if len(name_splits) < 2:
        await update.message.reply_text("У тебя должно быть как минимум имя и фамилия")
        return

    await update.message.reply_text(f"Очень приятно, {user_full_name.split(' ')[1]}! Какой у тебя номер комнаты?")
    user_full_name = user_full_name.lower().replace("ё", "е")
    db_helper.set_user_full_name(update.effective_user.id, user_full_name)
    return ConversationStates.REGISTRATION_ROOM_NUMBER


async def get_room_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        await update.message.reply_text("Я тебя не понял. Введи номер комнаты корректно")
        return
    user_room_num = int(update.message.text)
    db_helper.set_user_room(update.effective_user.id, user_room_num)
    await update.message.reply_text(
        f"Отлично! Записал тебя в {user_room_num} комнату. Теперь скажи в каком ты корпусе: А или Б?")
    return ConversationStates.REGISTRATION_CORPUS


async def choose_corpus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.lower()
    if user_input == "а" or user_input == "б":
        await update.message.reply_text("Отлично! Регистрация закончена.")
        db_helper.set_user_lives_in_b(update.effective_user.id, user_input == "б")
        return await menu_functions.main_menu(update, context)
    await update.message.reply_text("Я тебя не понял. Введи корпус корректно")


async def no_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(text="Не командуй мне тут. Делай что говорят",
                                   chat_id=update.effective_chat.id)
