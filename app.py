# app.py
from telegram_bot.db.db import ConnectionPool, insert_data, get_data, get_random_question_for_skill
from telegram_bot.quizfuncs import start_quiz, handle_answer, handle_continue, send_engagement_message, start_quiz_for_top_skills, show_available_skills
import demodata
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
    Update,
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

# Get current date
current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%m")
# Define the log file name
log_file_name = f"logs/log_{current_date}.txt"
# Define the format for log messages
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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

YOUR_TELEGRAM_BOT_TOKEN=os.environ['TGBOTKEY']

# Define the mandatory questions
MANDATORY_QUESTION_1 = "Who is the aggressor?"
MANDATORY_QUESTION_1_ru = "Кто агрессор?"
MANDATORY_QUESTION_2 = "Do you know English?"
MANDATORY_QUESTION_2_ru = "Английский знаешь?"

# Define the conversation states
LANGUAGE_CHOICE, NICKNAME, MANDATORY_QUESTIONS = range(3)

# Define the supported UI languages
UI_LANGUAGES = {
    'rus': 'Russian',
    'eng': 'English',
    'ukr': 'Ukrainian'
}
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
            logger.warning(f"Blocked user attempted to access command: {update.effective_user.name}")
            return
        return func(update, context)
    return wrapper


@check_blocked_user
@error_handling
async def language_choice(update, context) -> None:
    # Update the preferred UI language based on the user's choice
    query = update.callback_query
    context.user_data['language'] = query.data
    await context.bot.edit_message_text(text=f"Your preferred UI language is {UI_LANGUAGES[query.data]}", chat_id=query.message.chat_id, message_id=query.message.message_id)
 
    """Send a predefined poll"""
    questions =[]
    if context.user_data['language'] == "rus":
        context.user_data['current_question'] = MANDATORY_QUESTION_1_ru
        questions = ["Россия", "Украина"]
    else :
        context.user_data['current_question'] = MANDATORY_QUESTION_1
        questions = ["Russia", "Ukraine"]
    message = await update.effective_message.reply_poll(
        context.user_data['current_question'], questions, type=Poll.QUIZ, correct_option_id=0
    )
    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    payload = {
        message.poll.id: {"chat_id": update.effective_chat.id, "message_id": message.message_id}
    }
    context.bot_data.update(payload)

    
    #update.message.reply_text(MANDATORY_QUESTION_1)
    return MANDATORY_QUESTIONS

@check_blocked_user
@error_handling
async def handle_mandatory_questions(update, context):
    # Validate the answers to the mandatory questions
    answers = {
        MANDATORY_QUESTION_1: 'Russia',
        MANDATORY_QUESTION_1_ru: 'Россия',
        MANDATORY_QUESTION_2: 'Yes',
        MANDATORY_QUESTION_2_ru: 'Да'
    }

    message = update.message.text
    current_question = context.user_data.get('current_question')
    if not current_question:
        logger.warning(f"Invalid question received from user: {message}")
        return

    expected_answer = answers.get(current_question)
    if not expected_answer or message.lower() != expected_answer.lower():
        logger.warning(f"Invalid answer received from user: {message}")
#        return block_user(update)
    logger.warning(f"Invalid question: {current_question}")
    if current_question == MANDATORY_QUESTION_1 or current_question == MANDATORY_QUESTION_1_ru:
        keyboard = []
        keyboard.append([InlineKeyboardButton("No", callback_data="No")])
        keyboard.append([InlineKeyboardButton("Yes", callback_data="Yes")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = "Do you know English?"
        await update.message.reply_text(message, reply_markup=reply_markup)
        questions = []
        if context.user_data['language'] == "rus":
            context.user_data['current_question'] = MANDATORY_QUESTION_2_ru
            questions = ["Да", "Нет"]
        else :
            context.user_data['current_question'] = MANDATORY_QUESTION_2
            questions = ["Yes", "No"]
        #message = await update.effective_message.reply_poll(
        #    context.user_data['current_question'], questions, type=Poll.QUIZ, correct_option_id=0
        #)
        #await context.bot.send_message(chat_id=update.effective_chat.id, text=f"What is your nickname?")
        return MANDATORY_QUESTIONS
    if (current_question == MANDATORY_QUESTION_2 or current_question == MANDATORY_QUESTION_2_ru): #TODO: check answer
        return NICKNAME;#set_nickname(update, context)
    
    next_question_idx = list(answers.keys()).index(current_question) + 2
    next_question = list(answers.keys())[next_question_idx]
    context.user_data['current_question'] = next_question

    await update.message.reply_text(next_question)
    return MANDATORY_QUESTIONS

@check_blocked_user
@error_handling
async def set_nickname(update, context) -> None:
    # Set the user's nickname
    nickname = update.message.text
    context.user_data['nickname'] = nickname
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your nickname is set to {nickname}")
    return ConversationHandler.END

@check_blocked_user
@error_handling
async def cancel(update, context) -> None:
    # Handle the cancel command
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Registration canceled.")
    return ConversationHandler.END

async def block_user(update) -> None:
    # Block the user
    user_id = update.effective_user.id
    blocked_users.add(user_id)
    logger.warning(f"User blocked: {update.effective_user.name}")
    await update.message.reply_text("You have been blocked due to incorrect answers.")
    return ConversationHandler.END


# @check_blocked_user
# async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Sends a predefined poll"""
#     questions = ["Good", "Really good", "Fantastic", "Great"]
#     message = await context.bot.send_poll(
#         update.effective_chat.id,
#         "How are you?",
#         questions,
#         is_anonymous=False,
#         allows_multiple_answers=True,
#     )
#     # Save some info about the poll the bot_data for later use in receive_poll_answer
#     payload = {
#         message.poll.id: {
#             "questions": questions,
#             "message_id": message.message_id,
#             "chat_id": update.effective_chat.id,
#             "answers": 0,
#         }
#     }
#     context.bot_data.update(payload)

# @check_blocked_user
# async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Summarize a users poll vote"""
#     answer = update.poll_answer
#     answered_poll = context.bot_data[answer.poll_id]
#     try:
#         questions = answered_poll["questions"]
#     # this means this poll answer update is from an old poll, we can't do our answering then
#     except KeyError:
#         return
#     selected_options = answer.option_ids
#     answer_string = ""
#     for question_id in selected_options:
#         if question_id != selected_options[-1]:
#             answer_string += questions[question_id] + " and "
#         else:
#             answer_string += questions[question_id]
#     await context.bot.send_message(
#         answered_poll["chat_id"],
#         f"{update.effective_user.mention_html()} feels {answer_string}!",
#         parse_mode=ParseMode.HTML,
#     )
#     answered_poll["answers"] += 1
#     # Close poll after three participants voted
#     if answered_poll["answers"] == TOTAL_VOTER_COUNT:
#         await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])

# @check_blocked_user
# async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Send a predefined poll"""
#     questions = ["1", "2", "4", "20"]
#     message = await update.effective_message.reply_poll(
#         "How many eggs do you need for a cake?", questions, type=Poll.QUIZ, correct_option_id=2
#     )
#     # Save some info about the poll the bot_data for later use in receive_quiz_answer
#     payload = {
#         message.poll.id: {"chat_id": update.effective_chat.id, "message_id": message.message_id}
#     }
#     context.bot_data.update(payload)

# @check_blocked_user
# async def receive_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Close quiz after three participants took it"""
#     # the bot can receive closed poll updates we don't care about
#     if update.poll.is_closed:
#         return
#     if update.poll.total_voter_count == TOTAL_VOTER_COUNT:
#         try:
#             quiz_data = context.bot_data[update.poll.id]
#         # this means this poll answer update is from an old poll, we can't stop it then
#         except KeyError:
#             return
#         await context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])

# @check_blocked_user
# async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Ask user to create a poll and display a preview of it"""
#     # using this without a type lets the user chooses what he wants (quiz or poll)
#     button = [[KeyboardButton("Press me!", request_poll=KeyboardButtonPollType())]]
#     message = "Press the button to let the bot generate a preview for your poll"
#     # using one_time_keyboard to hide the keyboard
#     await update.effective_message.reply_text(
#         message, reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=True)
#     )

# @check_blocked_user
# async def receive_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """On receiving polls, reply to it by a closed poll copying the received poll"""
#     actual_poll = update.effective_message.poll
#     # Only need to set the question and options, since all other parameters don't matter for
#     # a closed poll
#     await update.effective_message.reply_poll(
#         question=actual_poll.question,
#         options=[o.text for o in actual_poll.options],
#         # with is_closed true, the poll/quiz is immediately closed
#         is_closed=True,
#         reply_markup=ReplyKeyboardRemove(),
#     )

@check_blocked_user
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display a help message"""
    await update.message.reply_text("Use /quiz, /poll or /preview to test this bot.")

# Define an error handler function
def error_handler(update, context):
    """Log and handle any errors that occur"""
    logger.error("Exception while handling an update:", exc_info=context.error)












AGRESSOR, PHOTO, NICKNAME, ISSUE_DESCR = range(4)

@check_blocked_user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about AGRESSOR."""
    reply_keyboard = [["Украина", "США", "Россия"]]

    await update.message.reply_text(
        "Привет, добро пожаловать в центр самообучения, позволь уточнить пару моментов.\n"
        "Необязательно, пошли /cancel для отмены, просто это тест на долбоеба \n\n"
        "Кто агрессор?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Украина или Россия?"
        ),
    )

    return AGRESSOR

@check_blocked_user
async def agressor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected AGRESSOR and asks for a photo."""
    message = update.message.text
    
    if (message == "Россия"):
        logger.info("%d угадал - Агрессор : %s", update.effective_user.id, message)
        await update.message.reply_text(
            "I see you are a man of culture!\n\n"
            "Пришли скриншот своей проблемы или пропусти нажав /skip",
            reply_markup=ReplyKeyboardRemove(),
        )
    else :
        await update.message.reply_text(
        "Нахуй туда <", reply_markup=ReplyKeyboardRemove()
        )
        blocked_users.append( update.effective_user.id)
        logger.info("%d - долбоеб, забанен нахуй, сказал - Агрессор : %s", update.effective_user.id, message)
        return ConversationHandler.END

    return PHOTO

@check_blocked_user
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the screenshot and asks for a nickname."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("requests\\" + str(update.effective_user.id) + "_user_photo.jpg")
    #await photo_file.download_to_drive("user_photo.jpg")
    #logger.info("Photo of %d: %s", update.effective_user.id, "user_photo.jpg")
    logger.info("Скриншот: %d_user_photo.jpg", update.effective_user.id)
    await update.message.reply_text(
        "Спасибо! Если хочешь можешь создать псевдоним для анонимности или пришли /skip , если не хочешь."
    )

    return NICKNAME

@check_blocked_user
async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the photo and asks for a nickname."""
    user = update.message.from_user
    logger.info("%d решил не присылать скриншот.", update.effective_user.id)
    await update.message.reply_text(
        "Ну и не надо! Если хочешь можешь создать псевдоним для анонимной связи или если не хочешь пришли /skip."
    )

    return NICKNAME

@check_blocked_user
async def nickname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the nickname and asks for some info about the isue."""
    user = update.message.from_user
    user_nickname = update.message.text
    logger.info(
        "Псевдоним %d: %s", update.effective_user.id, user_nickname
    )
    await update.message.reply_text(
        "Приятно познакомиться, " + user_nickname + "!\n\nОпиши свой реквест, будем рады помочь."
    )

    return ISSUE_DESCR

@check_blocked_user
async def skip_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the nickname and asks for info about the issue."""
    logger.info("%s не прислал псевдоним.", update.effective_user.id)
    await update.message.reply_text(
        "Ну как хочешь. Главное расскжи зачем пришел, будем рабы помочь!"
    )

    return ISSUE_DESCR

@check_blocked_user
async def issue_descr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Описание тикета от %d: %s", update.effective_user.id, update.message.text)
    await update.message.reply_text("На связи!")

    return ConversationHandler.END

@check_blocked_user
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("%s %dзакэнслил сбор инфы.", user.username, update.effective_user.id)
    await update.message.reply_text(
        "До связи.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END






##################################
######### CLUES ##################
##################################
# Handler for incoming messages
@error_handling
def handle_message(update, context, connection_pool):
    message = update.message
    text = message.text.strip()

    # Define the dictionary of question-answer pairs and their corresponding clues
    question, a , fa, clue_ru, clue_en = get_random_question_for_skill(connection_pool, 1)
    if text == fa:
        # Send the clue to the user
        message.reply_text(clue_ru + "\n\n" + clue_en)
        # Prompt the user to answer again by presenting the question as a reply keyboard
        message.reply_text(f"Please try again:\n{question}", reply_markup=create_reply_keyboard(question, a, fa))
        return


# Function to create a reply keyboard with question options
@error_handling
def create_reply_keyboard(question, answer, fake_answer):
    options = [answer, fake_answer]
    keyboard = ReplyKeyboardMarkup([[option] for option in options], one_time_keyboard=True)
    return keyboard









    




def main():
    ## Initialize connection pool with maximum number of connections
    connection_pool = ConnectionPool(max_connections=5)

    # Example usage
    data = get_data(connection_pool, "QuizQuestions")
    print(data)
    
    #insert_data(connection_pool, "New data")

    # Configure the conversation handler
    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler('start', start)],
    #     states={
    #         LANGUAGE_CHOICE: [CallbackQueryHandler(language_choice)],
    #         MANDATORY_QUESTIONS: [MessageHandler(filters.TEXT, handle_mandatory_questions)],
    #         NICKNAME: [MessageHandler(filters.TEXT, set_nickname)]
    #     },
    #     fallbacks=[CommandHandler('cancel', cancel)]
    # )



    # Add conversation handler with the states AGRESSOR, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AGRESSOR: [MessageHandler(filters.Regex("^(Ukraine|USA|Russia|Украина|США|Россия)$"), agressor)],
            PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
            NICKNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, nickname),
                CommandHandler("skip", skip_nickname),
            ],
            ISSUE_DESCR: [MessageHandler(filters.TEXT & ~filters.COMMAND, issue_descr)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add the conversation handler to the dispatcher
    #dispatcher.add_handler(conv_handler)
    
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(YOUR_TELEGRAM_BOT_TOKEN).build()
    application.add_handler(conv_handler)
#    application.add_handler(MessageHandler(filters.TEXT, handle_message(connection_pool)))
    # Command handlers
    quiz_handler = CommandHandler("quiz", lambda update, context: start_quiz(update, context, connection_pool))
    application.add_handler(quiz_handler)
    #application.add_handler(CommandHandler("quiz", start_quiz))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: handle_answer(update, context, connection_pool)))#handle_answer))
    application.add_handler(MessageHandler(filters.Regex('^Continue|Продолжить$'), lambda update, context: handle_continue(update, context, connection_pool)))#handle_continue))
    application.add_handler(CommandHandler("topquiz", start_quiz_for_top_skills))
    application.add_handler(CommandHandler("showskills", show_available_skills))






    #application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("poll", poll))
    # application.add_handler(CommandHandler("quiz", quiz))
    # application.add_handler(CommandHandler("preview", preview))
    # application.add_handler(CommandHandler("help", help_handler))
    # application.add_handler(MessageHandler(filters.TEXT, handle_mandatory_questions))
    # application.add_handler(MessageHandler(filters.POLL, receive_poll))
    # application.add_handler(PollAnswerHandler(receive_poll_answer))
    # application.add_handler(PollHandler(receive_quiz_answer))
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    #application.run_polling(allowed_updates=Update.ALL_TYPES)
    #application.bot.send_message(text="Use /quiz, /start to test this bot.")
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    #application.bot.send_message(text="Use /quiz, /start to test this bot.")
    # Start the bot
    #updater.start_polling()
    #updater.idle()


    # Close the connection pool when done
    connection_pool.close()

if __name__ == '__main__':
    main()