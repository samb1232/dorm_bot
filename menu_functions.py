import datetime
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

import strings
from enumerations import MenuCallbackButtons, ConversationStates
from database.db_operations import db_helper

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if db_helper.get_user_by_id(update.effective_user.id) is None:
        logger.info(f"Добавление нового пользователя {update.effective_user.name} в базу данных")

        db_helper.add_new_user(user_id=update.effective_user.id)
        await context.bot.send_message(text=strings.GREETING_TEXT,
                                       chat_id=update.effective_chat.id)
        return ConversationStates.REGISTRATION_FULL_NAME
    else:
        logger.debug("Пользователь обнаружен в базе данных")
        return await main_menu(update, context)


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [
            InlineKeyboardButton(strings.INFO_TEXT, callback_data=MenuCallbackButtons.INFO)
        ],
        [
            InlineKeyboardButton(strings.QUESTION_BUTTON_TEXT, callback_data=MenuCallbackButtons.QUESTION)
        ],
        [
            InlineKeyboardButton(strings.PAYMENT_BUTTON_TEXT, callback_data=MenuCallbackButtons.PAYMENT)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(text=strings.MAIN_MENU_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)
    return ConversationStates.MAIN_MENU


async def callback_buttons_manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery"""
    query = update.callback_query
    await query.answer()

    match query.data:
        case MenuCallbackButtons.INFO:
            await info(update, context)
        case MenuCallbackButtons.MAIN_MENU:
            await main_menu(update, context)
        case MenuCallbackButtons.KOMENDANT_INFO:
            await send_info(update, context, query.data)
        case MenuCallbackButtons.KASTELANSHA_INFO:
            await send_info(update, context, query.data)
        case MenuCallbackButtons.SHOWER_INFO:
            await send_info(update, context, query.data)
        case MenuCallbackButtons.LAUNDARY_INFO:
            await send_info(update, context, query.data)
        case MenuCallbackButtons.GUESTS_INFO:
            await send_info(update, context, query.data)
        case MenuCallbackButtons.QUESTION:
            # await question(update, context)
            await context.bot.send_message(text="Данная функция находится в разработке...",
                                           chat_id=update.effective_chat.id)
        case MenuCallbackButtons.GYM_INFO:
            await send_info(update, context, query.data)
        case MenuCallbackButtons.STUDY_ROOM_INFO:
            await send_info(update, context, query.data)
        case MenuCallbackButtons.STUDSOVET_INFO:
            await send_info(update, context, query.data)
        case MenuCallbackButtons.PAYMENT:
            # await payment(update, context)
            await context.bot.send_message(text="Данная функция находится в разработке...",
                                           chat_id=update.effective_chat.id)
        case MenuCallbackButtons.NOT_IMPLEMENTED:
            await context.bot.send_message(text="Данная функция находится в разработке...",
                                           chat_id=update.effective_chat.id)


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(strings.KOMENDANT_BUTTON_TEXT, callback_data=MenuCallbackButtons.KOMENDANT_INFO),
            InlineKeyboardButton(strings.KASTELANSHA_BUTTON_TEXT, callback_data=MenuCallbackButtons.KASTELANSHA_INFO)
        ],
        [
            InlineKeyboardButton(strings.SHOWER_BUTTON_TEXT, callback_data=MenuCallbackButtons.SHOWER_INFO),
            InlineKeyboardButton(strings.LAUNDARY_BUTTON_TEXT, callback_data=MenuCallbackButtons.LAUNDARY_INFO)
        ],
        [
            InlineKeyboardButton(strings.GUESTS_BUTTON_TEXT, callback_data=MenuCallbackButtons.GUESTS_INFO),
            InlineKeyboardButton(strings.GYM_BUTTON_TEXT, callback_data=MenuCallbackButtons.GYM_INFO)
        ],
        [
            InlineKeyboardButton(strings.STUDY_ROOM_BUTTON_TEXT, callback_data=MenuCallbackButtons.STUDY_ROOM_INFO),
            InlineKeyboardButton(strings.STUDSOVET_BUTTON_TEXT, callback_data=MenuCallbackButtons.STUDSOVET_INFO)
        ],
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=MenuCallbackButtons.MAIN_MENU)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(text=strings.INFO_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)
    return ConversationStates.MAIN_MENU


async def send_info(update: Update, context: ContextTypes.DEFAULT_TYPE, info_type: str):
    info_mapping = {
        MenuCallbackButtons.KOMENDANT_INFO: strings.KOMENDANT_INFO_TEXT,
        MenuCallbackButtons.KASTELANSHA_INFO: strings.KASTELANSHA_INFO_TEXT,
        MenuCallbackButtons.SHOWER_INFO: strings.SHOWER_INFO_TEXT,
        MenuCallbackButtons.LAUNDARY_INFO: strings.LAUNDARY_INFO_TEXT,
        MenuCallbackButtons.GUESTS_INFO: strings.GUESTS_INFO_TEXT,
        MenuCallbackButtons.GYM_INFO: strings.GYM_INFO_TEXT,
        MenuCallbackButtons.STUDY_ROOM_INFO: strings.STUDY_ROOM_INFO_TEXT,
        MenuCallbackButtons.STUDSOVET_INFO: strings.STUDSOVET_INFO_TEXT,
    }

    info_text = info_mapping.get(info_type)

    await context.bot.send_message(text=info_text, chat_id=update.effective_chat.id)
    # return await info(update, context)


async def unknown_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.message.edit_reply_markup(None)
    await query.answer()
    return await start(update, context)
