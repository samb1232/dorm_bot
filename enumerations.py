class MenuCallbackButtons:
    MAIN_MENU = "main_menu"
    QUESTION = "question"
    PROFILE = "profile"
    INFO = "info"
    KOMENDANT_INFO = "komendant_info"
    KASTELANSHA_INFO = "kastelansha"
    SHOWER_INFO = "shower"
    LAUNDARY_INFO = "laundary"
    GUESTS_INFO = "guests"
    GYM_INFO = "gym"
    STUDY_ROOM_INFO = "study"
    STUDSOVET_INFO = "studsovet"
    MANSARDA_INFO = "mansarda"

    PAYMENT = "payment"
    SEND_CHECK = "send_check"


class ChangeProfileCallbackButtons:
    CHANGE_NAME = "CHANGE_NAME"
    CHANGE_ROOM = "CHANGE_ROOM"
    CHANGE_CORPUS = "CHANGE_CORPUS"


class ConversationStates:
    MAIN_MENU: int = 0

    REGISTRATION_FULL_NAME: int = 1
    REGISTRATION_ROOM_NUMBER: int = 2
    REGISTRATION_CORPUS: int = 3
    CHANGE_FULL_NAME: int = 4
    CHANGE_ROOM_NUMBER: int = 5

    PAYMENT: int = 6
