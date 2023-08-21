# please create python code for telegram bot converstaion handler that help to create a support request for website creation. ask 5 appropriate questions for this task. like small description, price cap, urgency, link to preferred example. and please include a shortcut for automation that can provide all info in as one precomposed message - create description for that format also, please.
# Certainly! Here's an example of Python code for a Telegram bot conversation handler that helps create a support request for website creation. It includes five appropriate questions: small description, price cap, urgency, link to a preferred example, and a shortcut for automation that provides all the information in a precomposed message.
import logging
import datetime, os
import greetings
from db.db import ConnectionPool, change_priority_and_add_comment, create_support_ticket, get_support_agent_by_id, get_client_by_id, get_all_support_agents, get_tickets, assign_agent_to_ticket, change_ticket_state
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import ConversationHandler, MessageHandler, CommandHandler

# Configure the logger
logger = logging.getLogger(__name__)
# Define the conversation states
DESCRIPTION, PRICE_CAP, URGENCY, EXAMPLE_LINK, AUTOMATION_SHORTCUT = range(5)
ANSWER, CONTINUE = range(2)

# Start the conversation and ask for a small description or trigger automation
async def start_support_request(update, context, connection_pool: ConnectionPool):
    logger.info("%d tries to create a ticket:)", update.effective_user.id)
    # Check whether it's a new user - check existing agents and clients
    user = get_support_agent_by_id(connection_pool, update.effective_user.id)

    if user == None :
        user = get_client_by_id(connection_pool, update._effective_user.id)
        if user == None :
            if update.message.text.strip() == '/go' or update.message.text.strip() == '/ticket':
                # New user - ask to register first
                await update.message.reply_text(greetings.translations.get("regfirst_" + update._effective_user.language_code, greetings.translations["regfirst_en"]))
                return ConversationHandler.END
    
    if update.message.text.strip() == '/go' or update.message.text.strip() == '/ticket':
        # just command, not precomposed ticket - strat asking questions one by one
        await update.message.reply_text(greetings.translations.get("details_" + update._effective_user.language_code, greetings.translations["details_en"]), reply_markup=ReplyKeyboardRemove())
        return DESCRIPTION
    else:
        # Try to validate the message as an automation shortcut
        await parse_automation_message(update, context, update.message.text, connection_pool)
        return AUTOMATION_SHORTCUT

# Ask for the price cap
async def ask_price_cap(update, context):
    # Save the reply to the context
    context.user_data['description'] = update.message.text
    
    await update.message.reply_text(greetings.translations.get("price_" + update._effective_user.language_code, greetings.translations["price_en"]), reply_markup=ReplyKeyboardRemove())
    return PRICE_CAP

# Ask for the urgency
async def ask_urgency(update, context):
    # Save the reply to the context
    context.user_data['price_cap'] = update.message.text
    
    await update.message.reply_text(greetings.translations.get("urgence_" + update._effective_user.language_code, greetings.translations["urgence_en"]), reply_markup=ReplyKeyboardRemove())
    return URGENCY

# Ask for the link to a preferred example
async def ask_example_link(update, context):
    # Save the reply to the context
    context.user_data['urgency'] = update.message.text
    
    await update.message.reply_text(greetings.translations.get("examplink_" + update._effective_user.language_code, greetings.translations["examplink_en"]), reply_markup=ReplyKeyboardRemove())
    return EXAMPLE_LINK

# Provide a shortcut for automation with a precomposed message
async def provide_automation_shortcut(update, context, connection_pool: ConnectionPool):
    # Save the reply to the context
    context.user_data['example_link'] = update.message.text
    
    # Generate the precomposed message
    precomposed_message = "/go Support Request:\n"\
        "Description: " + context.user_data['description'] + "\n"\
        "Price Cap: " + context.user_data['price_cap'] + "\n"\
        "Urgency: " + context.user_data['urgency'] + "\n"\
        "Preferred Example: " + context.user_data['example_link']
    
    await update.message.reply_text(greetings.translations.get("shortcut_" + update._effective_user.language_code, greetings.translations["shortcut_en"]))
    await update.message.reply_text(precomposed_message)

    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%m")
    by_whom = get_client_by_id(connection_pool, update.effective_user.id)
    if by_whom is None:
        by_whom = get_support_agent_by_id(connection_pool, update.effective_user.id)
        if by_whom is None:
            # New user - ask to register first
            await update.message.reply_text(greetings.translations.get("regfirst_" + update._effective_user.language_code, greetings.translations["regfirst_en"]))
            return ConversationHandler.END

    await parse_automation_message(update, context, precomposed_message, connection_pool)
    return AUTOMATION_SHORTCUT

# Cancel the conversation
async def cancel(update, context):
    await update.message.reply_text(greetings.translations.get("noticket_" + update._effective_user.language_code, greetings.translations["noticket_en"]))
    return ConversationHandler.END



# In this example, we define the conversation states: DESCRIPTION, PRICE_CAP, URGENCY, EXAMPLE_LINK, and AUTOMATION_SHORTCUT. The start_support_request function initiates the conversation by asking for a small description. Then, each subsequent function asks the appropriate question and saves the user's replies in the user_data dictionary within the context object.

# The provide_automation_shortcut function generates a precomposed message by combining the user's replies and provides it as a shortcut. Finally, the conversation can be cancelled using the cancel function.

# To use this conversation handler, you need to add it to your Telegram bot with the appropriate command and import the necessary modules. You can customize the conversation flow and add more questions as needed.

# I hope this helps! Let me know if you have any further questions.
# super! please add message handler that can parse and  validate precomposed automation message and convert to  it dictionary that can be saved to sqlite db table which already has respectful fields.
# Sure! Here's an updated version of the code that includes a message handler to parse and validate the precomposed automation message and convert it into a dictionary that can be saved to an SQLite database table:


# Parse and validate the precomposed automation message
async def parse_automation_message(update, context, automation_message, connection_pool: ConnectionPool):
    # Split the automation message into lines
    lines = automation_message.split('\n')

    # Validate the number of lines
    if len(lines) < 5:
        await update.message.reply_text("Invalid automation message. Please provide all required fields.\n(description, price_cap, urgency, example_link, last_words)", reply_markup=ReplyKeyboardRemove())
        return AUTOMATION_SHORTCUT

    # Extract and validate each field from the lines
    description = lines[1].split(': ')[1].strip()
    price_cap = lines[2].split(': ')[1].strip()
    urgency = lines[3].split(': ')[1].strip()
    example_link = lines[4].split(': ')[1].strip()
    if not description :
        await update.message.reply_text("Invalid automation message. Description value is a mandatory field, please retry.", reply_markup=ReplyKeyboardRemove())
        return AUTOMATION_SHORTCUT

    last_words = None
    if len(lines) == 6:
        last_words = lines[5]

    # Calculate Priority
    Priority = "Normal"
    if len(urgency) > 13 :
         Priority = "High" 

    # TODO: get client site id
    Site_ID = None

    # Create a dictionary with the extracted fields
    request_data = {
        'price_cap': price_cap,
        'urgency': urgency,
        'example_link': example_link,
        'Client_ID': update.effective_user.id,
        'Ticket_ID': None,
        'Assigned_Agent_ID': None,
        'Client_ID': update.effective_user.id,
        'Site_ID': Site_ID, 
        'Priority': Priority, 
        'State': "Open",
        'Description': description,
        'Comments': last_words,
        'History': datetime.datetime.now().strftime("%Y-%m-%d_%H-%m") + " created",
    }

    # Save the request data to the SQLite database table
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%m")
    by_whom = get_client_by_id(connection_pool, update.effective_user.id)
    if by_whom is None:
        by_whom = get_support_agent_by_id(connection_pool, update.effective_user.id)
        if by_whom is None:
            # New user - ask to register first
            await update.message.reply_text(greetings.translations.get("regfirst_" + update._effective_user.language_code, greetings.translations["regfirst_en"]))
            return ConversationHandler.END

    save_request_to_database(request_data, connection_pool, date, by_whom[1])

    await update.message.reply_text(greetings.translations.get("ticket_success_" + update._effective_user.language_code, greetings.translations["ticket_success_en"]), reply_markup=ReplyKeyboardRemove())
    logger.info("%s (%d) managed to create a ticket!:)", by_whom[1], update.effective_user.id)

    chat_ids = get_all_support_agents(connection_pool)
    for chat_id_item in chat_ids:
        # Sending the message
        bot = Bot(token=os.environ["TGBOTKEY"])
        await bot.send_message(chat_id=chat_id_item[0], text=greetings.translations.get("ticket_success_bm_" + update._effective_user.language_code, greetings.translations["ticket_success_bm_en"]))

    return ConversationHandler.END

# Save the request data to the SQLite database table
def save_request_to_database(request_data, connection_pool: ConnectionPool, date, by_whom):
    description = (f"{request_data['Description']}\n$: {request_data['price_cap']}\n!: {request_data['urgency']}\n#: {request_data['example_link']}")
    
    new_ticket_id = create_support_ticket(
        connection_pool,
        None,
        request_data['Assigned_Agent_ID'],
        request_data['Client_ID'],
        request_data['Site_ID'],
        request_data['Priority'],
        request_data['State'],
        description,
        request_data['Comments'],
        request_data['History'],
        date,
        by_whom
    )
    
    logger.info("Ticket created: %d %s", new_ticket_id, request_data)


# Display a list of all tickets
async def estcho(update, context, connection_pool: ConnectionPool):
    tickets = get_tickets(connection_pool)
    ticket_list = "All tickets:\n\n"
    
    for ticket in tickets:
        if ticket is not None:
            ticket_card = generate_ticket_card(connection_pool, ticket)
            ticket_list += f"{ticket_card}\n"
    
    await update.message.reply_text(ticket_list)

# Update ticket status and display details
async def do(update, context, connection_pool: ConnectionPool):
    ticket_id = validate_ticket_id(update)
    
    if ticket_id is None:
        await update.message.reply_text("ID?")
        return
    
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")  # Corrected the time format

    by_whom = get_client_by_id(connection_pool, update.effective_user.id)
    if by_whom is None:
        by_whom = get_support_agent_by_id(connection_pool, update.effective_user.id)
        if by_whom is None:
            # New user - ask to register first
            await update.message.reply_text(greetings.translations.get("regfirst_" + update._effective_user.language_code, greetings.translations["regfirst_en"]))
            return ConversationHandler.END
    
    ticket = change_ticket_state(connection_pool, update.message.text.split()[1].strip(), user_id, "In Progress", date, by_whom[1])
    if ticket is not None:
        ticket_card = generate_ticket_card(connection_pool, ticket)
        await update.message.reply_text(ticket_card)
        await notifyEVERYONE(greetings.translations.get("ticket_in_progress_bm_" + update._effective_user.language_code, greetings.translations["ticket_in_progress_bm_en"]) + "\n" + ticket_card, ticket[2], connection_pool)
        
        logger.info("Ticket in progress: %d %s", ticket[0], ticket)

async def get(update, context, connection_pool: ConnectionPool):
    ticket_id = validate_ticket_id(update)
    
    if ticket_id is None:
        await update.message.reply_text("ID?")
        return
    
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")  # Corrected the time format
    user_id = update.effective_user.id
    by_whom = get_client_by_id(connection_pool, update.effective_user.id)
    if by_whom is None:
        by_whom = get_support_agent_by_id(connection_pool, update.effective_user.id)
        if by_whom is None:
            # New user - ask to register first
            await update.message.reply_text(greetings.translations.get("regfirst_" + update._effective_user.language_code, greetings.translations["regfirst_en"]))
            return ConversationHandler.END
    
    ticket = assign_agent_to_ticket(connection_pool, update.message.text.split()[1].strip(), user_id, date, by_whom[1])
    if ticket is not None:
        ticket_card = generate_ticket_card(connection_pool, ticket)
        await update.message.reply_text(ticket_card)
        await notifyEVERYONE(greetings.translations.get("ticket_assigned_bm_" + update._effective_user.language_code, greetings.translations["ticket_assigned_bm_en"]) + "\n" + ticket_card, ticket[2], connection_pool)
        logger.info("Ticket assigned: %d %s", ticket[0], ticket)

async def finish(update, context, connection_pool: ConnectionPool):
    ticket_id = validate_ticket_id(update)
    
    if ticket_id is None:
        await update.message.reply_text("ID?")
        return
    
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")  # Corrected the time format

    by_whom = get_client_by_id(connection_pool, update.effective_user.id)
    if by_whom is None:
        by_whom = get_support_agent_by_id(connection_pool, update.effective_user.id)
        if by_whom is None:
            # New user - ask to register first
            await update.message.reply_text(greetings.translations.get("regfirst_" + update._effective_user.language_code, greetings.translations["regfirst_en"]))
            return ConversationHandler.END
            
    ticket = None
    if by_whom is None:
        by_whom = get_support_agent_by_id(connection_pool, update.effective_user.id)
        if by_whom is None:
            # New user - ask to register first
            await update.message.reply_text(greetings.translations.get("regfirst_" + update._effective_user.language_code, greetings.translations["regfirst_en"]))
            return ConversationHandler.END
        else :
            ticket = change_ticket_state(connection_pool, update.message.text.split()[1].strip(), update.effective_user.id, "Resolved", date, by_whom[1])
            logger.info("Ticket Resolved: %d %s", ticket[0], ticket)
    else:
        ticket = change_ticket_state(connection_pool, update.message.text.split()[1].strip(), update.effective_user.id, "Closed", date, by_whom[1])
        logger.info("Ticket Closed: %d %s", ticket[0], ticket)
    
    if ticket is not None:
        ticket_card = generate_ticket_card(connection_pool, ticket)
        await update.message.reply_text(ticket_card)
        await notifyEVERYONE(greetings.translations.get("ticket_finished_bm_" + update._effective_user.language_code, greetings.translations["ticket_finished_bm_en"]) + "\n" + ticket_card, ticket[2], connection_pool)

async def promote(update, context, connection_pool: ConnectionPool):
    ticket_id = validate_ticket_id(update)
    
    if ticket_id is None:
        await update.message.reply_text("ID?")
        return
    
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")  # Corrected the time format

    by_whom = get_client_by_id(connection_pool, update.effective_user.id)
    if by_whom is None:
        by_whom = get_support_agent_by_id(connection_pool, update.effective_user.id)
        if by_whom is None:
            # New user - ask to register first
            await update.message.reply_text(greetings.translations.get("regfirst_" + update._effective_user.language_code, greetings.translations["regfirst_en"]))
            return ConversationHandler.END
    
    ticket = change_priority_and_add_comment(
        connection_pool,
        ticket_id,
        "High",
        "Client Doubled the money!",
        date,
        by_whom[1]
    )
    
    if ticket is not None:
        ticket_card = generate_ticket_card(connection_pool, ticket)
        await update.message.reply_text(ticket_card)
        await notifyEVERYONE(greetings.translations.get("ticket_promoted_bm_" + update._effective_user.language_code, greetings.translations["ticket_promoted_bm_en"]) + "\n" + ticket_card, ticket[2], connection_pool)

# Subfunction to generate ticket card
def generate_ticket_card(connection_pool, ticket):
    ticket_id, assigned_agent_id, client_id, site_id, priority, state, description, comments, history = ticket
    ticket_card = "Updated ticket:\n\n"  # Used lowercase variable names
    
    ticket_card += f"No: {ticket_id}\n\n"
    
    if assigned_agent_id is not None:
        agent_name = get_support_agent_by_id(connection_pool, assigned_agent_id)[1]
        ticket_card += f"Agent: {agent_name}\n"
    else:
        ticket_card += "Agent:\n"
    
    client_info = get_client_by_id(connection_pool, client_id)
    if client_info is not None:
        ticket_card += f"Client: {client_info[1]}\n"
    
    ticket_card += f"Priority: {priority}\n"
    ticket_card += f"State: {state}\n"
    ticket_card += f"Description: {description}\n"
    
    if comments is not None:
        ticket_card += f"Comments: {comments}\n"
    
    ticket_card += f"History: {history}\n"
    
    return ticket_card
        
async def notifyEVERYONE(text, client, connection_pool: ConnectionPool):
    chat_ids = get_all_support_agents(connection_pool)
    for chat_id_item in chat_ids:
        # Sending the message
        bot = Bot(token=os.environ["TGBOTKEY"])
        await bot.send_message(chat_id=chat_id_item[0], text=text)
    await bot.send_message(chat_id=client, text=text)

def validate_ticket_id(update):
    try:
        ticket_id = update.message.text.split()[1].strip()
        return ticket_id
    except IndexError:
        return None
    
# In this updated code, I've added the parse_automation_message function as a MessageHandler to the AUTOMATION_SHORTCUT state. This function parses and validates the precomposed automation message and extracts the required fields. If the message is valid, it creates a dictionary (request_data) with the extracted fields. Then, it calls the save_request_to_database function to save the request data to an SQLite database table.

# The save_request_to_database function connects to the SQLite database file (support_requests.db), inserts the request data into the support_requests table, and commits the changes.

# Please make sure to customize the SQLite table and connection settings according to your needs.

# I hope this helps! Let me know if you have any further questions.
# wow, great - it's more then i asked for, thank you for creatinig swlite code right away, very helpful, i inderstood!

# we need to add entry point for automation shortcut. lets modify start_support_request function in following ways:
# 1) in case besides the command the initial text is empty - star the converstaion
# 2) if some additional text is present then first try to validate it as automation shortcut message, and trigger it, or if validation failed - treat this message as description and save to context and skip first step in conversation.

# and by the way, as a guy trying to service as many clients as pissible should i be transparent with price right away with customers? and may be it's better to ask about urgency befor price cap? statin price right away is seems too like-a-boss move for me, i'm newby in business) afraid to spook clients, i think building client base first is better, lets maybe make it a hidden questions, for trusted clients;)
# Certainly! I understand your concerns. We can modify the start_support_request function to handle the cases you mentioned. Here's the updated code:

# In the updated code:

# 1. We change the entry point to a MessageHandler with a filter that matches any text input that is not a bot command ((~Filters.command)). If the input is an empty string, it starts the conversation. Otherwise, it attempts to validate the message as an automation shortcut.

# 2. We extract the automation message parsing logic into a separate parse_automation_message function. If the automation message is valid, the function returns the request data as a dictionary. If it is invalid, the function returns None.

# 3. If the message is a valid automation shortcut, it saves the request data to the database and ends the conversation.

# If the message doesn't match the automation shortcut structure, it treats it as a description and proceeds to the next step in the conversation. This way, if someone accidentally adds some additional text, it won't disrupt the conversation flow.

# Regarding your question about transparency with prices, it depends on your business strategy. It's common for service providers to discuss pricing early on to s
# et expectations and avoid wasting time for both parties if there is a significant mismatch in budget. However, if you prefer to build a client base first and establish trust, you can keep the price discussion until later stages of the conversation. It's a good approach to tailor your conversation flow and order of questions based on your business goals.

# I hope this modification addresses your requirements. Let me know if there's anything else I can assist you with!

# def handle_help_command(chat_id):
#     help_message = "Welcome to the Telegram Bot Help! Here are the available commands:\n\n" \
#                   "/help - Display this help message\n" \
#                   "/iam {nickname} - Set your nickname\n" \
#                   "/msg {nickname} {message} - Forward a message to a user\n\n" \
#                   "Note: If you set a nickname using the /iam command, it will be used in forwarded messages.\n" \
#                   "Otherwise, forwarded messages will be anonymous."
    
#     # TODO: send to chat from db through bot :)
    
#     # if response.status_code == 200:
#     #     print("Help message sent successfully!")
#     # else:
#     #     print("Failed to send the help message.")

# # Example usage

# chat_id = "413553377"
# handle_help_command(chat_id)