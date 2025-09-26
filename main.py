import asyncio
import threading

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, \
    ConversationHandler

import bot_instance
from states_functions import change_profile_functions, payment_functions, registration_functions, menu_functions
from configs.my_logger import get_logger
import notifications
from enumerations import ConversationStates


logger = get_logger(__name__)


def main() -> None:
    """Starts the bot."""
    main_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", menu_functions.start),
                      MessageHandler(filters.ALL, menu_functions.start),
                      CallbackQueryHandler(menu_functions.unknown_callback_handler)
                      ],
        states={
            ConversationStates.MAIN_MENU: [
                CommandHandler("start", menu_functions.start),
                CallbackQueryHandler(menu_functions.callback_buttons_manager),
                MessageHandler(filters.ALL, menu_functions.start),
                CallbackQueryHandler(menu_functions.unknown_callback_handler),
            ],
            ConversationStates.REGISTRATION_FULL_NAME: [
                MessageHandler(filters.TEXT, registration_functions.get_name),
                MessageHandler(filters.COMMAND, registration_functions.no_command),
                CallbackQueryHandler(menu_functions.unknown_callback_handler)
            ],
            ConversationStates.REGISTRATION_ROOM_NUMBER: [
                MessageHandler(filters.TEXT, registration_functions.get_room_number),
                MessageHandler(filters.COMMAND, registration_functions.no_command),
                CallbackQueryHandler(menu_functions.unknown_callback_handler)
            ],

            ConversationStates.REGISTRATION_CORPUS: [
                MessageHandler(filters.TEXT, registration_functions.choose_corpus),
                MessageHandler(filters.COMMAND, registration_functions.no_command),
                CallbackQueryHandler(menu_functions.unknown_callback_handler)
            ],

            ConversationStates.CHANGE_FULL_NAME: [
                MessageHandler(filters.TEXT, change_profile_functions.full_name_change_handler),
                CallbackQueryHandler(menu_functions.unknown_callback_handler)
            ],

            ConversationStates.CHANGE_ROOM_NUMBER: [
                MessageHandler(filters.TEXT, change_profile_functions.room_number_change_handler),
                CallbackQueryHandler(menu_functions.unknown_callback_handler)
            ],

            ConversationStates.PAYMENT: [
                MessageHandler(filters.ATTACHMENT, payment_functions.receive_check_file),
                CommandHandler("cancel", payment_functions.cancel_sending_check),
                MessageHandler(filters.ALL, payment_functions.unknown_message_handler),
                CallbackQueryHandler(menu_functions.unknown_callback_handler)
            ],
        },
        fallbacks=[]
    )

    bot_instance.application.add_handler(main_conversation_handler)

    notifications.start_schedule_functions()
    threading.Thread(target=run_async_schedule, daemon=True).start()
    # Run the bot
    logger.info("Бот запущен")
    bot_instance.application.run_polling(allowed_updates=Update.ALL_TYPES)


def run_async_schedule():
    asyncio.run(notifications.run_schedules())


if __name__ == "__main__":
    main()
