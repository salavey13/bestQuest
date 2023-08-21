#Let's add the inline buttons to the bot to provide multiple choices for the quiz questions. Additionally, we'll add buttons to start the quiz for the top 13 skills and a button to show all available skills. Here's the updated code:
from db.db import ConnectionPool, get_skill_id_by_skill_name, get_random_question_for_skill, get_agent_statistics_by_id, update_agent_rating, with_connection
import random
import greetings
import data_scraping.search_helper
from sqlite3 import Connection
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, ConversationHandler
ANSWER, CONTINUE = range(2)

# Handler for the "/quiz {skill_name}" command
async def start_quiz(update: Update, context: CallbackContext, connection_pool: ConnectionPool):
    # Extract the skill_name from the command
    if len(update.message.text.split()) == 1:
        return ConversationHandler.END
    skill_name = update.message.text.split()[1]
    # Find the skill_id based on the skill_name (assuming you have a 'skills' table)
    skill_id = get_skill_id_by_skill_name(connection_pool, skill_name)

    #######################################
    #get rating from db:) 
    stat = get_agent_statistics_by_id(connection_pool, update.effective_user.id)
    ############################################

    if skill_id != "":
        question, a, fa, clue_ru, clue_en, a_en, fa_en = get_random_question_for_skill(connection_pool, skill_id)

        # Store the current question, user's rating, and consecutive correct answer count in the context
        context.user_data['current_question'] = question
        context.user_data['a'] = a
        context.user_data['skill_id'] = skill_id
        context.user_data['fa'] = fa
        context.user_data['clue_ru'] = clue_ru
        context.user_data['clue_en'] = clue_en
        
        if context.user_data.get('rating') is None :
            context.user_data['rating'] = stat[0]
        context.user_data['public_rating'] = stat[0]
        context.user_data['correct_count'] = 0

        # Send the question text with multiple choice options to the user
        reply_markup = create_reply_menu(a, fa)
        await update.message.reply_text(question, reply_markup=reply_markup)
        return ANSWER

    else:
        await update.message.reply_text(f"Skill '{skill_name}' not found. Please enter a valid skill name.")
        return ConversationHandler.END

# Handler for the "/quiz {skill_name}" command
async def start_rating_quiz(update: Update, context: CallbackContext, connection_pool: ConnectionPool):
    # Extract the skill_name from the command
    if len(update.message.text.split()) == 1:
        return ConversationHandler.END
    
    skill_name = update.message.text.split()[1]
    # Find the skill_id based on the skill_name (assuming you have a 'skills' table)
    skill_id = get_skill_id_by_skill_name(connection_pool, skill_name)

    #######################################
    #get rating from db:) 
    stat = get_agent_statistics_by_id(connection_pool, update.effective_user.id)
    ############################################

    if skill_id != "":
        question, a, fa, clue_ru, clue_en, a_en, fa_en = get_random_question_for_skill(connection_pool, skill_id)

        # Store the current question, user's rating, and consecutive correct answer count in the context
        context.user_data['current_question'] = question
        context.user_data['a'] = a_en
        context.user_data['skill_id'] = skill_id
        context.user_data['fa'] = fa_en
        context.user_data['clue_ru'] = clue_ru
        context.user_data['clue_en'] = clue_en
        context.user_data['rating'] = stat[0]
        if context.user_data.get('public_rating') is None :
            context.user_data['public_rating'] = stat[0]
        context.user_data['correct_count'] = 0

        # Send the question text with multiple choice options to the user
        reply_markup = create_reply_menu(a_en, fa_en)
        await update.message.reply_text(question, reply_markup=reply_markup)

        return ANSWER
    else:
        await update.message.reply_text(f"Skill '{skill_name}' not found. Please enter a valid skill name.")
        return ConversationHandler.END

# Handler for handling user's response
async def handle_answer(update: Update, context: CallbackContext, connection_pool: ConnectionPool):
    user_answer = update.message.text.lower()
    current_question = context.user_data.get('current_question')
    correct_answer = context.user_data.get('a')
    clue = context.user_data.get('clue_ru')
    skill_id = context.user_data.get('skill_id')
    correct_count = context.user_data.get('correct_count', 0)
    
    if current_question:
        if user_answer[:5] == correct_answer.lower()[:5]:
            # Correct answer
            context.user_data.pop('clue_given', None)
            if "(" in context.user_data['a'] :
                context.user_data['public_rating'] += 13
                # update in db
                update_agent_rating(connection_pool, update.effective_user.id, context.user_data['public_rating'])
            else :
                context.user_data['rating'] += 13
                # update in db
                update_agent_rating(connection_pool, update.effective_user.id, context.user_data['rating'])

            context.user_data['correct_count'] += 1

            

            if correct_count + 1 >= 5 and context.user_data['correct_count'] not in [10, 25, 50, 69, 100, 420]:
                await update.message.reply_text(f"Вы ответили верно на {context.user_data['correct_count']} вопросов!\nMMR: {context.user_data['rating']}\npublic: {context.user_data['public_rating']}")
                #update.message.reply_text(f"Congratulations! You've answered {context.user_data['correct_count']} questions correctly in a row.")

            elif correct_count + 1 in [5, 10, 25, 50, 69, 100, 420]:
                await update.message.reply_text(f"Круто! Вы ответили верно на {context.user_data['correct_count']} вопросов, красавчик!")
                #update.message.reply_text(f"Congratulations! You've answered {context.user_data['correct_count']} questions correctly in a row. Well done!")

            question, a, fa, clue_ru, clue_en, a_en, fa_en = get_random_question_for_skill(connection_pool, skill_id)  # Assuming skill_id is in the 2nd position

            # Update the current question and the correct answer count in the context for the next interaction
            context.user_data['current_question'] = question
            if "(" in user_answer :
                context.user_data['a'] = a
                context.user_data['fa'] = fa
            else :
                context.user_data['a'] = a_en
                context.user_data['fa'] = fa_en
            context.user_data['clue_ru'] = clue_ru
            context.user_data['clue_en'] = clue_en

            # Handle engagement messages
            if context.user_data['correct_count'] % 13 == 0:
                await send_engagement_message(update)

            # Send the question text with multiple choice options to the user
            reply_markup = None
            if "(" in user_answer :
                reply_markup = create_reply_menu(a, fa)
            else :
                reply_markup = create_reply_menu(a_en, fa_en) 
            await update.message.reply_text(question, reply_markup=reply_markup)
            return ANSWER

        elif 'clue_given' not in context.user_data:
            # Incorrect answer, give a clue
            context.user_data['clue_given'] = True
            gif_url = data_scraping.search_helper.search_and_download_gif(context.user_data['a'], True)
            if gif_url != None:
                await update.message.reply_text(f"Неа, подсказака:\n{gif_url}\n\n{clue}")
            else:
                await update.message.reply_text(f"Неа, подсказака:\n\n{clue}")
            if "(" in user_answer:
                context.user_data['public_rating'] -= 12
            else :
                context.user_data['rating'] -= 12
            #await update.message.reply_text(f"Sorry, that's incorrect. Here's a clue: {clue}")
            
            return ANSWER
        else:
            # Incorrect answer, give video description and URL with a button to continue
            context.user_data.pop('clue_given', None)
            if "(" in user_answer :
                context.user_data['public_rating'] -= 13
            else :
                context.user_data['rating'] -= 13
            if context.user_data['public_rating'] < 0:
                context.user_data['public_rating'] = 0
            if context.user_data['rating'] < 0:
                context.user_data['rating'] = 0
            video_description = "топ видео ютуба"  # Assuming the video description is in the 10th position
            video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Assuming the video URL is in the 9th position

            #update.message.reply_text("Sorry, that's incorrect. Let's educate yourself!\n"
            await update.message.reply_text("Да что ты будешь делать! Посмотри видос и продолжим)\n"
                                      f"{video_description}\n"
                                      f"{video_url}")#,
                                      #reply_markup=ReplyKeyboardMarkup([['Продолжить','Continue']], one_time_keyboard=True))
            return CONTINUE

# Handler for handling the "Continue" button after sending the video details
async def handle_continue(update: Update, context: CallbackContext, connection_pool: ConnectionPool):
    question, a, fa, clue_ru, clue_en, a_en, fa_en = get_random_question_for_skill(connection_pool, context.user_data['skill_id'])
    context.user_data['current_question'] = question
    if "(" in context.user_data['a']:
        context.user_data['a'] = a
        context.user_data['fa'] = fa
    else :
        context.user_data['a'] = a_en
        context.user_data['fa'] = fa_en
    context.user_data['clue_ru'] = clue_ru
    context.user_data['clue_en'] = clue_en

    # Send the question text with multiple choice options to the user
    reply_markup = None
    if "(" in context.user_data['a']:
        reply_markup = create_reply_menu(a, fa)
    else :
        reply_markup = create_reply_menu(a_en, fa_en)
    await update.message.reply_text(question, reply_markup=reply_markup)
    return ANSWER

# Send engagement messages
async def send_engagement_message(update: Update):
    # messages = [
    #     "Relax dude, postpone it till tomorrow, like you've done it your whole life. You won't make it!",
    #     "Joking! You're doing great! Keep up the good work! 😄"
    # ]
    # messages = [
    #     "Расслабься, чувак, отложи на завтра, как будто всю жизнь этим занимался. Не сможешь!",
    #     "Шучу! У тебя отлично получается! Продолжай в том же духе! 😄"
    #  ]
    await update.message.reply_text(greetings.translations.get("relax"+update._effective_user.language_code, greetings.translations.get("relaxen")))
    await update.message.reply_text(greetings.translations.get("relax2"+update._effective_user.language_code, greetings.translations.get("relax2en")))
    return ANSWER

# Create inline reply menu for question options
def create_reply_menu(a, fa):
    answers = [a, fa]  # Assuming fake_answer1, fake_answer2 are in the 5th and 6th positions
    random.shuffle(answers)
    keyboard = [
        [
            InlineKeyboardButton(answers[0], callback_data=answers[0]),
            InlineKeyboardButton(answers[1], callback_data=answers[1]),
        ]
    ]
    return ReplyKeyboardMarkup(keyboard)

# Command handler to start quiz for top 13 skills
async def start_quiz_for_top_skills(update: Update, context: CallbackContext):
    # Fetch the top 13 skills (modify the SQL query as per your table structure)

#    top_skills = cursor.fetchall()

    # Create a keyboard with buttons for each top skill
    keyboard = [["/quiz UI","/rating_quiz UI"]]#, "VatnikVerse"] #[[skill[0]] for skill in top_skills]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    # Await the reply_text function call
#!!await update.message.reply_text("Choose a skill to start the quiz:", reply_markup=reply_markup)
    await update.message.reply_text("Выбери скилл и начнем quiz:", reply_markup=reply_markup)

# Handler for showing all available skills
async def show_available_skills(update: Update, context: CallbackContext):
    # cursor.execute('SELECT skill_name FROM skills')
    # all_skills = cursor.fetchall()
    # skill_list = '\n'.join([skill[0] for skill in all_skills])


    
#!!await update.message.reply_text(f"Available skills: UI)\n")#{skill_list}")
    await update.message.reply_text(f"Доступные скилы: UI\n")#{skill_list}")

#Feel free to customize the code further and let me know if you have any more questions!