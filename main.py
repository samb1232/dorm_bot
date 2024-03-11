import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, \
    ConversationHandler

import config
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
    # Create the Application
    application = Application.builder().token(config.API_TOKEN).build()

    main_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                      MessageHandler(filters.ALL, start),
                      CallbackQueryHandler(unknown_callback_handler)],
        states={
            ConversationStates.MAIN_MENU: [
                CommandHandler("start", start),
                CallbackQueryHandler(callback_buttons_manager),
                MessageHandler(filters.ALL, start)
            ],
            ConversationStates.REGISTRATION_FULL_NAME: [
                MessageHandler(filters.TEXT, registration.get_name),
                MessageHandler(filters.COMMAND, registration.no_command),
                CallbackQueryHandler(unknown_callback_handler)
            ],
            ConversationStates.REGISTRATION_ROOM_NUMBER: [
                MessageHandler(filters.TEXT, registration.get_room_number),
                MessageHandler(filters.COMMAND, registration.no_command),
                CallbackQueryHandler(unknown_callback_handler)],

            ConversationStates.REGISTRATION_CORPUS: [
                MessageHandler(filters.TEXT, registration.choose_corpus),
                MessageHandler(filters.COMMAND, registration.no_command),
                CallbackQueryHandler(unknown_callback_handler)],
        },
        fallbacks=[]
    )

    application.add_handler(main_conversation_handler)

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
