class MenuCallbackButtons:
    MAIN_MENU = "main_menu"
    QUESTION = "question"
    PAYMENT = "payment"
    INFO = "info"
    KOMENDANT_INFO = "komendant_info"
    KASTELANSHA_INFO = "kastelansha"
    SHOWER_INFO = "shower"
    LAUNDARY_INFO = "laundary"
    GUESTS_INFO = "guests"
    GYM_INFO = "gym"
    STUDY_ROOM_INFO = "study"
    STUDSOVET_INFO = "studsovet"
    NOT_IMPLEMENTED = "_"


class ConversationStates:
    MAIN_MENU: int = 0

    REGISTRATION_FULL_NAME: int = 1
    REGISTRATION_ROOM_NUMBER: int = 2
    REGISTRATION_CORPUS: int = 3

    PAYMENT: int = 4
