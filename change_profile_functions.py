from telegram import Update
from telegram.ext import ContextTypes

import menu_functions
import strings
from database.db_operations import db_helper
from enumerations import ConversationStates

async def change_user_corpus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = db_helper.get_user_by_id(update.effective_user.id)
    db_helper.set_user_lives_in_b(user.user_id, not user.user_lives_in_b)
    await context.bot.send_message(text=strings.CORPUS_CHANGED_TEXT,
                                   chat_id=update.effective_chat.id)
    return await menu_functions.show_profile(update, context)


async def change_user_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(text=strings.ENTER_FULL_NAME_TEXT,
                                   chat_id=update.effective_chat.id)
    return ConversationStates.CHANGE_FULL_NAME


async def change_user_room_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(text=strings.ENTER_ROOM_NUMBER_TEXT,
                                   chat_id=update.effective_chat.id)
    return ConversationStates.CHANGE_ROOM_NUMBER


async def full_name_change_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_full_name = update.message.text
    name_splits = user_full_name.split(' ')
    if len(name_splits) < 2:
        await update.message.reply_text("У тебя должно быть как минимум фамилия и имя")
        return

    user_full_name = user_full_name.lower().replace("ё", "е")
    db_helper.set_user_full_name(update.effective_user.id, user_full_name)
    await update.message.reply_text(strings.FULL_NAME_CHANGED_TEXT)
    return await menu_functions.show_profile(update, context)


async def room_number_change_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        await update.message.reply_text("Я тебя не понял. Введи номер комнаты корректно")
        return
    user_room_num = int(update.message.text)
    db_helper.set_user_room(update.effective_user.id, user_room_num)
    await update.message.reply_text(strings.ROOM_NUMBER_CHANGED_TEXT)
    return await menu_functions.show_profile(update, context)


