import db.db #ConnectionPool, insert_data, get_data, get_random_question_for_skill
from db.db import ConnectionPool, with_connection
from ticketfuncs import DESCRIPTION, PRICE_CAP, URGENCY, EXAMPLE_LINK, AUTOMATION_SHORTCUT, ANSWER, CONTINUE, promote, estcho, ask_price_cap, ask_urgency, ask_example_link, provide_automation_shortcut, parse_automation_message, start_support_request, get, do, finish
from quizfuncs import start_quiz,start_rating_quiz, handle_answer, handle_continue, send_engagement_message, start_quiz_for_top_skills, show_available_skills
import greetings
import os
import datetime
import logging
from functools import wraps

from telegram import __version__ as TG_VER
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PollAnswerHandler,
    PollHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from telegram.error import TelegramError
import telegram

# Get current date
current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%m")
# Define the log file name
log_file_name = f"logs/log_{current_date}.txt"
# Define the format for log messages
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# Set up logging
#logging.basicConfig(filename=log_file_name, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler
file_handler = logging.FileHandler(log_file_name)
file_handler.setLevel(logging.INFO)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Set the format for the file handler
file_handler.setFormatter(formatter)
# Set the format for the console handler
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
print(f"Log file '{log_file_name}' created.")

# Define the blocked users
blocked_users = []
##########################

# Enable logging and catch exceptions
def error_handling(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception  as e:
            logger.error(f"An error occurred: {e}")
    return wrapper

# let those who is unable to comprehend chill
def check_blocked_user(func) -> None:
    @wraps(func)
    def wrapper(update, context) -> None:
        if update.effective_user and update.effective_user.id in blocked_users:
            logger.warning(f"Blocked user {update.effective_user.name} attempted to access command: {update.message.text}")
            return
        return func(update, context)
    return wrapper
# let those who is unable to comprehend chill
def check_blocked_user3(func) -> None:
    @wraps(func)
    def wrapper3(update, context, connection_pool) -> None:
        if update.effective_user and update.effective_user.id in blocked_users:
            logger.warning(f"Blocked user {update.effective_user.name} attempted to access command: {update.message.text}")
            return
        return func(update, context, connection_pool)
    return wrapper3
    


NEWUSER, START, AGRESSOR = range(3)
NICKNAME, DISCORD = range(2) #PHOTO, 
@check_blocked_user3
async def prestart(update: Update, context: ContextTypes.DEFAULT_TYPE, connection_pool: ConnectionPool) -> int:#
    if update.effective_user and update.effective_user.id in blocked_users:
        logger.warning(f"Blocked user {update.effective_user.name} attempted to access command: {update.message.text}")
        return
    logger.info("%d's language is %s", update.effective_user.id, update._effective_user.language_code)
    # Check whether it's a new user - check existing agents and clients
    user = db.db.get_support_agent_by_id(connection_pool, update.effective_user.id)
#    user = None
    if user == None : 
        user = db.db.get_client_by_id(connection_pool, update._effective_user.id)
        if user == None :
            if update.message.text == "/start":
                # New user - align help with his language
                await update.message.reply_text(greetings.translations.get(update._effective_user.language_code, greetings.translations["en"]))

                """Starts the conversation and asks the user about AGRESSOR."""
                reply_keyboard = [[greetings.translations.get("Украина"+update._effective_user.language_code, "Ukraine"), greetings.translations.get("США"+update._effective_user.language_code, "USA"), greetings.translations.get("Россия"+update._effective_user.language_code, "Russia")]]

                await update.message.reply_text(
                    greetings.translations.get("main"+update._effective_user.language_code, "mainen"),
                    reply_markup=ReplyKeyboardMarkup(
                        reply_keyboard, one_time_keyboard=True, input_field_placeholder=greetings.translations.get("Украина или Россия?"+update._effective_user.language_code, greetings.translations.get("Украина или Россия?en"))
                    ),
                )

                return AGRESSOR
            elif update.message.text == "/reg":
                await update.message.reply_text(greetings.translations.get("nickname" + update._effective_user.language_code, greetings.translations["nicknameen"]), reply_markup=ReplyKeyboardRemove())
                context.user_data['isClient'] = False
                return NICKNAME
            elif update.message.text == "/regClient":
                context.user_data['isClient'] = True
                await update.message.reply_text(greetings.translations.get("nickname" + update._effective_user.language_code, greetings.translations["nicknameen"]), reply_markup=ReplyKeyboardRemove())
                
                return NICKNAME
    else :
        await update.message.reply_text("Wazzup, " + user[1] + "!")
        if update.message.text == "/start":
            await update.message.reply_text(greetings.translations.get(update._effective_user.language_code, greetings.translations["en"]), reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

# async def handle_selected_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     # Store the current question, user's rating, and consecutive correct answer count in the context
#     # context.user_data['lang'] = update.callback_query.data
#     # context.user_data['id'] = update._effective_user.language_codeid
#     # context.user_data['skill_id'] = skill_id
#     # context.user_data['fa'] = fa
#     # context.user_data['clue_ru'] = clue_ru
#     # context.user_data['clue_en'] = clue_en
#     # context.user_data['rating'] = 0
#     # context.user_data['correct_count'] = 0
#     #             Agent_ID INTEGER PRIMARY KEY AUTOINCREMENT,
#     #         TG_ID TEXT,
#     #         Nickname TEXT,
#     #         Discord TEXT,
#     #         Skills TEXT,
#     #         Price_Map TEXT,
#     #         Achievements TEXT,
#     #         Verification_Status TEXT,
#     #         Blue_Checkmark TEXT,
#     #         Number_of_Tickets INTEGER,
#     #         Number_of_Executed_Tickets INTEGER,
#     #         Positive_Reviews INTEGER,
#     #         Preferred_Lang TEXT
#     selected_language = update.callback_query.data
#     # Store the selected language in a database or any other storage
#     # Set the user's language preference for future use
#     message = update.message.text
    
#     if (message == "english"):
#         logger.info("%d selected %s language", update.effective_user.id, message)
#         await update.message.reply_text(
#             "I see you are a man of culture!\n\n"
#             "Пришли скриншот своей проблемы или пропусти нажав /skip",
#             reply_markup=ReplyKeyboardRemove(),
#         )

#     else :
#         await update.message.reply_text(
#         "Нахуй туда <", reply_markup=ReplyKeyboardRemove()
#         )
#         blocked_users.append( update.effective_user.id)
#         logger.info("%d - долбоеб, забанен нахуй, сказал - Агрессор : %s", update.effective_user.id, message)
#         return ConversationHandler.END

#     return START

# @check_blocked_user
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Starts the conversation and asks the user about AGRESSOR."""
#     reply_keyboard = [["Украина", "США", "Россия"]]

#     await update.message.reply_text(
#         "Привет, добро пожаловать в центр самообучения, позволь уточнить пару моментов.\n"
#         "Необязательно, пошли /cancel для отмены, просто это тест на долбоеба \n\n"
#         "Кто агрессор?",
#         reply_markup=ReplyKeyboardMarkup(
#             reply_keyboard, one_time_keyboard=True, input_field_placeholder="Украина или Россия?"
#         ),
#     )

#     return AGRESSOR

@check_blocked_user
async def agressor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_user and update.effective_user.id in blocked_users:
        logger.warning(f"Blocked user {update.effective_user.name} attempted to access command: {update.message.text}")
        return ConversationHandler.END
    message = update.message.text
    
    if (message == "Россия" or  message == "Russia" or message == "Росія" ):
        logger.info("%d is ok - said that Agressor is %s", update.effective_user.id, message)
        await update.message.reply_text(
            "I see you are a man of culture as well!\n\n",
            reply_markup=ReplyKeyboardRemove(),
        )
    else :
        await update.message.reply_text(
        "Нахуй туда <", reply_markup=ReplyKeyboardRemove()
        )
        blocked_users.append( update.effective_user.id)
        logger.info("%d - долбоеб, забанен нахуй, сказал - Агрессор : %s", update.effective_user.id, message)
    return ConversationHandler.END

@check_blocked_user
async def nickname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the nickname and asks for some info about the isue."""
    user_nickname = update.message.text
    context.user_data['nickname'] = user_nickname
    logger.info(
        "Nickname set for %d: %s", update.effective_user.id, user_nickname
    )
    
    #await update.message.reply_text(greetings.translations.get("nickname" + update._effective_user.language_code, greetings.translations["nicknameen"]), reply_markup=ReplyKeyboardRemove())
    # TODO: use greetings            
    await update.message.reply_text(
        "Приятно познакомиться, " + user_nickname + "!\n\nНапиши дискорд для связи"
    )

    return DISCORD

@check_blocked_user
async def skip_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the nickname and asks for info about the issue."""
    logger.info("%d skipped nickname", update.effective_user.id)

    #await update.message.reply_text(greetings.translations.get("nickname" + update._effective_user.language_code, greetings.translations["nicknameen"]), reply_markup=ReplyKeyboardRemove())
    # TODO: use greetings 
    await update.message.reply_text(
        "Ну как хочешь. Хоть дискорд дай"
    )

    return DISCORD

                    # @check_blocked_user
                    # async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
                    #     """Stores the screenshot and asks for a nickname."""
                    #     user = update.message.from_user
                    #     photo_file = await update.message.photo[-1].get_file()
                    #     await photo_file.download_to_drive("requests\\" + str(update.effective_user.id) + "_user_photo.jpg")
                    #     #await photo_file.download_to_drive("user_photo.jpg")
                    #     #logger.info("Photo of %d: %s", update.effective_user.id, "user_photo.jpg")
                    #     logger.info("Скриншот: %d_user_photo.jpg", update.effective_user.id)
                    #     await update.message.reply_text(
                    #         "Спасибо! Если хочешь можешь создать псевдоним для анонимности или пришли /skip , если не хочешь."
                    #     )

                    #     return DISCORD

                    # @check_blocked_user
                    # async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
                    #     """Skips the photo and asks for a nickname."""
                    #     user = update.message.from_user
                    #     logger.info("%d решил не присылать скриншот.", update.effective_user.id)
                    #     await update.message.reply_text(
                    #         "Ну и не надо! Если хочешь можешь создать псевдоним для анонимной связи или если не хочешь пришли /skip."
                    #     )

                    #     return DISCORD

@check_blocked_user3
async def discord(update: Update, context: ContextTypes.DEFAULT_TYPE, connection_pool: ConnectionPool) -> int:
    # Stores the discord
    user_discord = update.message.text
    context.user_data['discord'] = user_discord
    logger.info("Discord set for %d: %s", update.effective_user.id, user_discord)

    # save to db
    nickname = "Anonimous"
    if context.user_data.get('nickname') is not None:
        nickname = context.user_data.get('nickname')
    
    if context.user_data.get('isClient') == True :
        db.db.create_client(connection_pool, update.effective_user.id, nickname, user_discord, "no description", "UI", "NONEXISTENT", 0, "0", "0", update._effective_user.language_code)
    else :
        db.db.create_support_agent(connection_pool, update.effective_user.id, nickname, user_discord, "UI", "just4training", "first 13 club", "Approved as Founder", "TRUE", 0, "0", "0", update._effective_user.language_code)
    
    logger.info("%d is IN like %s, discord: %s", update.effective_user.id, nickname, user_discord)

    await update.message.reply_text(
        "nice, u r in"
    )

    return ConversationHandler.END


async def skip_discord(update: Update, context: ContextTypes.DEFAULT_TYPE, connection_pool: ConnectionPool) -> int:
    # Skips the discord
    logger.info("%d skipped discord", update.effective_user.id)

    nickname = "Anonimous"
    if context.user_data.get('nickname') is not None:
        nickname = context.user_data.get('nickname')
    discord = "Anonimous"
    if context.user_data.get('discord') is not None:
        discord = context.user_data.get('discord')

    # save to db
    db.db.create_support_agent(connection_pool, update.effective_user.id, nickname, discord, "UI", "just4training", "first 13 club", "Approved as Founder", "TRUE", update.message.chat_id, "0", "0", update._effective_user.language_code)
    logger.info("%d is IN like %s, discord: %s", update.effective_user.id, nickname, discord)
    
    # Congratulate
    await update.message.reply_text(
        "nice, u r in"
    )

    return ConversationHandler.END

                                        # @check_blocked_user
                                        # async def issue_descr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
                                        #     """Stores the info about the user and ends the conversation."""
                                        #     user = update.message.from_user
                                        #     logger.info("Описание тикета от %d: %s", update.effective_user.id, update.message.text)
                                        #     await update.message.reply_text("На связи!")

                                        #     return ConversationHandler.END

@check_blocked_user
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("%s %dзакэнслил сбор инфы.", user.username, update.effective_user.id)
    await update.message.reply_text(
        "ok", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

async def block_user(update) -> None:
    # Block the user
    user_id = update.effective_user.id
    blocked_users.add(user_id)
    logger.warning(f"User blocked: {update.effective_user.name}")
    await update.message.reply_text(greetings.translations.get("Вы были заблокированы из-за неправильных ответов." + update._effective_user.language_code, greetings.translations.get("Вы были заблокированы из-за неправильных ответов.en")))
    return ConversationHandler.END



                    ##################################
                    ######### CLUES ##################
                    ##################################
                    # Handler for incoming messages
                    # @error_handling
                    # def handle_message(update, context, connection_pool):
                    #     message = update.message
                    #     text = message.text.strip()

                    #     # Define the dictionary of question-answer pairs and their corresponding clues
                    #     question, a , fa, clue_ru, clue_en, a_en, fa_en = db.db.get_random_question_for_skill(connection_pool, 1)
                    #     if text == fa :
                    #         # Send the clue to the user
                    #         message.reply_text(clue_ru + "\n\n" + clue_en)
                    #         # Prompt the user to answer again by presenting the question as a reply keyboard
                    #         message.reply_text(f"Please try again:\n\n{question}", reply_markup=create_reply_keyboard(question, a, fa))
                    #         return
                    #     if text == fa_en:
                    #         # Send the clue to the user
                    #         message.reply_text(clue_ru + "\n\n" + clue_en)
                    #         # Prompt the user to answer again by presenting the question as a reply keyboard
                    #         message.reply_text(f"Please try again:\n\n{question}", reply_markup=create_reply_keyboard(question, a_en, fa_en))
                    #         return


# Function to create a reply keyboard with question options
@error_handling
def create_reply_keyboard(question, answer, fake_answer):
    options = [answer, fake_answer]
    keyboard = ReplyKeyboardMarkup([[option] for option in options], one_time_keyboard=True)
    return keyboard

@check_blocked_user
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display a help message"""
    # Greetings
    if update.effective_user.language_code == "en" :
        await update.message.reply_text(greetings.translations.get("help_" + update._effective_user.language_code, greetings.translations.get("help_en")))
    elif update.effective_user.language_code == "uk":
        await update.message.reply_text(greetings.translations.get("help_" + update._effective_user.language_code, greetings.translations.get("help_uk")))
    else : # ru is default
        await update.message.reply_text(greetings.translations.get("help_" + update._effective_user.language_code, greetings.translations.get("help_ru")))

# Define an error handler function
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log and handle any errors that occur"""
    logger.error("Exception while handling an update:", exc_info=context.error)



# # # MSG HANDLER # ## # #
##########################
##########################
@check_blocked_user3
async def msg_handler(update: Update,  context: ContextTypes.DEFAULT_TYPE, connection_pool:ConnectionPool):
    """Forward message to registered user"""
    bot = telegram.Bot(token=os.environ["TGBOTKEY"])

    # Replace CHAT_ID with the ID of the chat you want to send the message to
    remote_chat_id = '413553377'

    # Replace MESSAGE_TEXT with the text you want to send
    message_text = 'Hello, how are you?'

    # Validate input
    if validate_forward_input(update.message.text) :
        remote_nickname = update.message.text.split()[1]
        message_text = ' '.join(update.message.text.split()[2:])
        remote_user = None
        local_user = db.db.get_support_agent_by_id(connection_pool, update.effective_user.id)
        if local_user is None :
            local_user = db.db.get_client_by_id(connection_pool, update.effective_user.id)
        if local_user is not None :
            if remote_nickname != "Anonimous":
                remote_user = db.db.get_support_agent_by_nickname(connection_pool, remote_nickname)
                if remote_user is None :
                        remote_user = db.db.get_client_by_id(connection_pool, update.effective_user.id)
                    

                if remote_user is not None :
                    message_text = "Вам сообщение от " +  local_user[1]  +" : " + message_text
                    chat_id = remote_user[0]

                    # Sending the message
                    await bot.send_message(chat_id=chat_id, text=message_text)
                    
                elif remote_nickname == "EVERYONE" :
                    message_text = "Всем сообщение от " +  local_user[1]  +" : " + message_text
                    chat_ids = db.db.get_all_support_agents(connection_pool)
                    for chat_id_item in chat_ids:
                        # Sending the message
                        await bot.send_message(chat_id=chat_id_item[0], text=message_text)
                    #secret agent:)
                    #await bot.send_message(chat_id="", text=message_text + " твой чат захардкодил)")
                else :
                    # Oops case
                    await update.message.reply_text("Can't find user with Nickname " + remote_nickname)
            else :
                await update.message.reply_text("Anonymous'ы могут получать только общие сообщения?")
        else :
            await update.message.reply_text("Anonymous, сначала /reg ;)")
##########################
##########################


# # # start_support_request
##########################
##########################
#  -> ticketfuncs.py
##########################
##########################

def validate_forward_input(input_string):
    # Split the input string into parts
    parts = input_string.split()

    # Check if the input string has the correct format
    if len(parts) < 3 or parts[0] != '/msg':
        return False

    # Check if the second and third parts are not empty
    if not parts[1] or not parts[2]:
        return False

    # Return True if the input is valid
    return True
    
def main():
    # Create the Application and pass it your bot's token.
    YOUR_TELEGRAM_BOT_TOKEN=os.environ["TGBOTKEY"]
    application = Application.builder().token(YOUR_TELEGRAM_BOT_TOKEN).build()
    
    ## Initialize connection pool with maximum number of connections
    connection_pool = ConnectionPool(max_connections=5)

    # Example usage #######################################
    data = db.db.get_data(connection_pool, "QuizQuestions")
    print("quiz loaded")#(data)
    data = db.db.get_all_support_agents(connection_pool)
    print("current agents:")
    print(data)

    data = db.db.get_data(connection_pool, "SupportAgents")
    print("current agents:")
    for agent in data :
        print(agent)
    # insert_data(connection_pool, "New data") ############


    # Add the registration handler
    reg_handler = ConversationHandler(
        entry_points=[CommandHandler("reg", lambda update, context: prestart(update, context, connection_pool)),CommandHandler("regClient", lambda update, context: prestart(update, context, connection_pool))],
        states={
            NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, nickname), CommandHandler("skip", skip_nickname)],
            #PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
            DISCORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: discord(update, context, connection_pool)), CommandHandler("skip", skip_discord)],
            # SKILL: [MessageHandler(filters.Regex("^(english|український|русский)$"), start)],
            # AGRESSOR: [MessageHandler(filters.Regex("^(Ukraine|USA|Russia|Украина|США|Россия|Україна|Росія)$"), agressor)],
            
            # NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, nickname), CommandHandler("skip", skip_nickname)],
            # ISSUE_DESCR: [MessageHandler(filters.TEXT & ~filters.COMMAND, issue_descr)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(reg_handler)
    


    # Add conversation handler with the states AGRESSOR, PHOTO, NICKNAME  and ISSUE DESCRIPTION
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", lambda update, context: prestart(update, context, connection_pool))],
        states={
 #           NEWUSER: [MessageHandler(filters.Regex("^(english|український|русский)$"), handle_selected_language)],
 #           START: [MessageHandler(filters.Regex("^(english|український|русский)$"), start)],
            AGRESSOR: [MessageHandler(filters.Regex("^(Ukraine|USA|Russia|Украина|США|Россия|Україна|Росія)$"), agressor)],
 #           PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
 #           NICKNAME: [
 #               MessageHandler(filters.TEXT & ~filters.COMMAND, nickname),
  #              CommandHandler("skip", skip_nickname),
 #           ],
 #           ISSUE_DESCR: [MessageHandler(filters.TEXT & ~filters.COMMAND, issue_descr)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    # Command handlers
 #   application.add_handler(CommandHandler("quiz", lambda update, context: start_quiz(update, context, connection_pool)))
 #   application.add_handler(CommandHandler("rating_quiz", lambda update, context: start_rating_quiz(update, context, connection_pool)))
 #   application.add_handler(CommandHandler("topquiz", start_quiz_for_top_skills)

    application.add_handler(CommandHandler("showskills", show_available_skills))
    application.add_handler(CommandHandler("estchoposkilam", show_available_skills))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("msg", lambda update, context: msg_handler(update, context, connection_pool)))
    #application.add_handler(CommandHandler("msg", msg_handler))
 #   application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: handle_answer(update, context, connection_pool)))
 #   application.add_handler(MessageHandler(filters.Regex('^Continue|Продолжить|Продовжити$'), lambda update, context: handle_continue(update, context, connection_pool)))


    # Create the Quiz conversation handler
    quiz_handler = ConversationHandler(
        entry_points=[CommandHandler("quiz", lambda update, context: start_quiz(update, context, connection_pool)),
                      CommandHandler("rating_quiz", lambda update, context: start_rating_quiz(update, context, connection_pool)),
                      CommandHandler("topquiz", start_quiz_for_top_skills)],
        states={
            ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: handle_answer(update, context, connection_pool))],
            CONTINUE: [MessageHandler(filters.Regex('^Continue|Продолжить|Продовжити$'), lambda update, context: handle_continue(update, context, connection_pool))]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(quiz_handler)

    # Create the Support Ticket conversation handler
    support_request_handler = ConversationHandler(
        entry_points=[CommandHandler('ticket', lambda update, context: start_support_request(update, context, connection_pool)), 
                    CommandHandler("go", lambda update, context: start_support_request(update, context, connection_pool)), 
                    CommandHandler("estcho", lambda update, context: estcho(update, context, connection_pool)), 
                    CommandHandler("get", lambda update, context: get(update, context, connection_pool)), 
                    CommandHandler("do", lambda update, context: do(update, context, connection_pool)), 
                    CommandHandler("finish", lambda update, context: finish(update, context, connection_pool)), 
                    CommandHandler("promote", lambda update, context: promote(update, context, connection_pool))],
        states={
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_price_cap)],
            PRICE_CAP: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_urgency)],
            URGENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_example_link)],
            EXAMPLE_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: provide_automation_shortcut(update, context, connection_pool))],
            AUTOMATION_SHORTCUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: parse_automation_message(update, context, connection_pool))]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(support_request_handler)

    application.add_error_handler(error_handler)


    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

    # Close the connection pool when done
    connection_pool.close()

if __name__ == '__main__':
    main()