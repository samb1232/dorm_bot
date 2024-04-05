import logging
import threading

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, \
    ConversationHandler

import bot_instance
import change_profile_functions
import notifications
import payment_functions
import registration
from enumerations import ConversationStates
from menu_functions import start, unknown_callback_handler, callback_buttons_manager

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("database.db_operations").setLevel(logging.DEBUG)
logging.getLogger("excursion").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)


def main() -> None:
    """Starts the bot."""
    main_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                      MessageHandler(filters.ALL, start),
                      CallbackQueryHandler(unknown_callback_handler)
                      ],
        states={
            ConversationStates.MAIN_MENU: [
                CommandHandler("start", start),
                CallbackQueryHandler(callback_buttons_manager),
                MessageHandler(filters.ALL, start),
                CallbackQueryHandler(unknown_callback_handler),
            ],
            ConversationStates.REGISTRATION_FULL_NAME: [
                MessageHandler(filters.TEXT, registration.get_name),
                MessageHandler(filters.COMMAND, registration.no_command),
                CallbackQueryHandler(unknown_callback_handler)
            ],
            ConversationStates.REGISTRATION_ROOM_NUMBER: [
                MessageHandler(filters.TEXT, registration.get_room_number),
                MessageHandler(filters.COMMAND, registration.no_command),
                CallbackQueryHandler(unknown_callback_handler)
            ],

            ConversationStates.REGISTRATION_CORPUS: [
                MessageHandler(filters.TEXT, registration.choose_corpus),
                MessageHandler(filters.COMMAND, registration.no_command),
                CallbackQueryHandler(unknown_callback_handler)
            ],

            ConversationStates.CHANGE_FULL_NAME: [
                MessageHandler(filters.TEXT, change_profile_functions.full_name_change_handler),
                CallbackQueryHandler(unknown_callback_handler)
            ],

            ConversationStates.CHANGE_ROOM_NUMBER: [
                MessageHandler(filters.TEXT, change_profile_functions.room_number_change_handler),
                CallbackQueryHandler(unknown_callback_handler)
            ],

            ConversationStates.PAYMENT: [
                MessageHandler(filters.ATTACHMENT, payment_functions.receive_check_file),
                CommandHandler("cancel", payment_functions.cancel_sending_check),
                MessageHandler(filters.ALL, payment_functions.unknown_message_handler),
                CallbackQueryHandler(unknown_callback_handler)
            ],
        },
        fallbacks=[]
    )

    bot_instance.application.add_handler(main_conversation_handler)

    notifications.start_schedule_functions()
    threading.Thread(target=notifications.run_schedules, daemon=True).start()

    # Run the bot
    bot_instance.application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
