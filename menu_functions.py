import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import change_profile_functions
import payment_functions
import strings
import utils
from database.db_operations import DbHelper
from enumerations import MenuCallbackButtons, ConversationStates, ChangeProfileCallbackButtons

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if DbHelper.get_user_by_id(update.effective_user.id) is None:
        logger.info(f"Добавление нового пользователя {update.effective_user.name} в базу данных")

        DbHelper.add_new_user(user_id=update.effective_user.id)
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
        # [
        #     InlineKeyboardButton(strings.QUESTION_BUTTON_TEXT, callback_data=MenuCallbackButtons.QUESTION)
        # ],
        [
            InlineKeyboardButton(strings.PAYMENT_BUTTON_TEXT, callback_data=MenuCallbackButtons.PAYMENT)
        ],
        [
            InlineKeyboardButton(strings.PROFILE_BUTTON_TEXT, callback_data=MenuCallbackButtons.PROFILE)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(text=strings.MAIN_MENU_TEXT,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)
    return ConversationStates.MAIN_MENU


async def callback_buttons_manager(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Parses the CallbackQuery"""
    query = update.callback_query
    await query.answer()

    query_data = query.data

    if query_data == MenuCallbackButtons.INFO:
        result = await info(update, context)
    elif query_data == MenuCallbackButtons.MAIN_MENU:
        result = await main_menu(update, context)
    elif query_data in [MenuCallbackButtons.KOMENDANT_INFO, MenuCallbackButtons.KASTELANSHA_INFO,
                        MenuCallbackButtons.SHOWER_INFO, MenuCallbackButtons.LAUNDARY_INFO,
                        MenuCallbackButtons.GUESTS_INFO, MenuCallbackButtons.GYM_INFO,
                        MenuCallbackButtons.STUDY_ROOM_INFO, MenuCallbackButtons.STUDSOVET_INFO,
                        MenuCallbackButtons.MANSARDA_INFO]:
        result = await send_info(update, context, query_data)
    elif query_data == MenuCallbackButtons.QUESTION:
        await context.bot.send_message(text="Данная функция находится в разработке...",
                                       chat_id=update.effective_chat.id)
        result = None
    elif query_data == MenuCallbackButtons.PAYMENT:
        result = await payment_functions.payment_info(update, context)
    elif query_data == MenuCallbackButtons.SEND_CHECK:
        result = await payment_functions.send_check(update, context)
    elif query_data == MenuCallbackButtons.PROFILE:
        result = await show_profile(update, context)
    elif query_data == ChangeProfileCallbackButtons.CHANGE_NAME:
        result = await change_profile_functions.change_user_full_name(update, context)
    elif query_data == ChangeProfileCallbackButtons.CHANGE_ROOM:
        result = await change_profile_functions.change_user_room_number(update, context)
    elif query_data == ChangeProfileCallbackButtons.CHANGE_CORPUS:
        result = await change_profile_functions.change_user_corpus(update, context)
    else:
        result = None

    return result


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
            InlineKeyboardButton(strings.MANSARDA_BUTTON_TEXT, callback_data=MenuCallbackButtons.MANSARDA_INFO)
        ],
        [
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


async def send_info(update: Update, context: ContextTypes.DEFAULT_TYPE, info_type: str) -> int:
    user = DbHelper.get_user_by_id(update.effective_user.id)
    info_mapping = {
        MenuCallbackButtons.KOMENDANT_INFO: strings.KOMENDANT_INFO_TEXT,
        MenuCallbackButtons.KASTELANSHA_INFO: strings.KASTELANSHA_INFO_TEXT,
        MenuCallbackButtons.SHOWER_INFO: strings.SHOWER_INFO_TEXT,
        MenuCallbackButtons.LAUNDARY_INFO: strings.LAUNDARY_INFO_TEXT,
        MenuCallbackButtons.GUESTS_INFO: strings.GUESTS_INFO_TEXT,
        MenuCallbackButtons.GYM_INFO: strings.GYM_INFO_TEXT,
        MenuCallbackButtons.STUDY_ROOM_INFO: strings.STUDY_ROOM_INFO_TEXT,
        MenuCallbackButtons.MANSARDA_INFO: strings.MANSARDA_INFO_TEXT,
        MenuCallbackButtons.STUDSOVET_INFO: "stud_info",
    }

    info_text = info_mapping.get(info_type)

    if info_text == "stud_info":
        if user.lives_in_b:
            info_text = strings.STUDSOVET_INFO_B_TEXT
        else:
            info_text = strings.STUDSOVET_INFO_A_TEXT

    await context.bot.send_message(text=info_text, chat_id=update.effective_chat.id)
    return ConversationStates.MAIN_MENU


async def unknown_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.message.edit_reply_markup(None)
    await query.answer()
    return await start(update, context)


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = DbHelper.get_user_by_id(update.effective_user.id)
    corpus = "А"
    if user.lives_in_b:
        corpus = "Б"

    info_text = (f"Профиль: \n"
                 f"ФИО: {utils.capitalize_full_name(user.full_name)}\n"
                 f"Комната: {user.room_number}\n"
                 f"Корпус: {corpus}")
    keyboard = [
        [
            InlineKeyboardButton(strings.CHANGE_NAME_BUTTON_TEXT,
                                 callback_data=ChangeProfileCallbackButtons.CHANGE_NAME)],
        [
            InlineKeyboardButton(strings.CHANGE_ROOM_BUTTON_TEXT,
                                 callback_data=ChangeProfileCallbackButtons.CHANGE_ROOM)],
        [
            InlineKeyboardButton(strings.CHANGE_CORPUS_BUTTON_TEXT,
                                 callback_data=ChangeProfileCallbackButtons.CHANGE_CORPUS)
        ],
        [
            InlineKeyboardButton(strings.MAIN_MENU_BUTTON_TEXT, callback_data=MenuCallbackButtons.MAIN_MENU)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(text=info_text,
                                   chat_id=update.effective_chat.id,
                                   reply_markup=reply_markup)
    return ConversationStates.MAIN_MENU
