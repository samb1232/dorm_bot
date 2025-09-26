import logging
import os.path
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

import config
import menu_functions
import strings
import utils
from database.db_operations import DbHelper
from enumerations import ConversationStates, MenuCallbackButtons
from google_drive_api import GoogleDriveAPI

ALLOWED_CHECK_EXTENSIONS = ["jpg", "png", "jpeg", "pdf"]


logger = logging.getLogger(__name__)


async def payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = DbHelper.get_user_by_id(update.effective_user.id)
    debt_amount = DbHelper.get_debt_by_name(user.full_name)

    debt_str = "У тебя сейчас нет долга по оплате общежития.\n"

    if debt_amount != 0:
        debt_str = f"Твой долг составляет: {debt_amount} руб.\n"
    payment_info_text = (debt_str + "Если хочешь прикрепить чек, нажми на кнопку")
    keyboard = [
        [
            InlineKeyboardButton("Таблица долгов", url=f'https://docs.google.com/spreadsheets/d/{config.GS_SPREADSHEETS_ID}')
        ],
        [
            InlineKeyboardButton(strings.SEND_CHECK_BUTTON_TEXT,
                                 callback_data=MenuCallbackButtons.SEND_CHECK)],
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=MenuCallbackButtons.MAIN_MENU)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(text=payment_info_text,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)
    return ConversationStates.MAIN_MENU


async def send_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(text=strings.SEND_CHECK_TEXT,
                                   chat_id=update.effective_chat.id)
    return ConversationStates.PAYMENT


async def unknown_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(text=strings.UNKNOWN_TEXT,
                                   chat_id=update.effective_chat.id)


async def cancel_sending_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(text=strings.CANCEL_TEXT,
                                   chat_id=update.effective_chat.id)

    return await menu_functions.main_menu(update, context)


async def receive_check_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = DbHelper.get_user_by_id(update.effective_user.id)

    if update.message.document is not None:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
        file_unique_id = update.message.document.file_unique_id
    elif len(update.message.photo) != 0:
        file_id = update.message.photo[-1].file_id
        file_name = "temp.png"
        file_unique_id = update.message.photo[-1].file_unique_id
    elif update.message.sticker is not None:
        logger.info("Дибилыч стикер отправил...")
        await context.bot.send_message(text="*посмеялся*",
                                       chat_id=update.effective_chat.id)
        return ConversationStates.PAYMENT

    elif update.message.voice is not None:
        await context.bot.send_message(text="тебя не слышно",
                                       chat_id=update.effective_chat.id)
        return ConversationStates.PAYMENT
    else:
        await context.bot.send_message(text=strings.INCORRECT_FILE_TEXT,
                                       chat_id=update.effective_chat.id)
        return ConversationStates.PAYMENT

    extension = utils.get_extension_from_file_name(file_name)
    if extension not in ALLOWED_CHECK_EXTENSIONS:
        await context.bot.send_message(text=strings.INCORRECT_FILE_TEXT,
                                       chat_id=update.effective_chat.id)
        return ConversationStates.PAYMENT

    file = await context.bot.get_file(file_id)

    new_file_name = "5"
    if user.lives_in_b:
        new_file_name += "Б"
    else:
        new_file_name += "А"

    new_file_name += "_" + str(user.full_name).replace(" ", "_") + "_" + file_unique_id + "." + extension
    await file.download_to_drive(new_file_name)

    await context.bot.send_message(text="Пробую загрузить твой чек...",
                                   chat_id=update.effective_chat.id)

    GoogleDriveAPI.upload_file(new_file_name, new_file_name)

    os.remove(new_file_name)

    await context.bot.send_message(text="Чек успешно загружен! Комендант обработает его по возможности",
                                   chat_id=update.effective_chat.id)

    return await menu_functions.main_menu(update, context)
