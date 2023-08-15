import csv
#import db_helper
from sqlite3 import Connection
from sqlite3.dbapi2 import connect
from queue import Queue
from functools import wraps
from threading import Lock, Thread
import os
class ConnectionPool:
    def __init__(self, max_connections):
        self.max_connections = max_connections
        self._connections = Queue(maxsize=max_connections)
        self._lock = Lock()

        # Initialize the connection pool with maximum number of connections
        self._initialize_pool()

    def _create_connection(self):
        return connect("your_database.db")

    def get_connection(self) -> Connection:
        connection = self._connections.get(block=True)
        self._connections.put(connection)
        return connection

    def _initialize_pool(self):
        with self._lock:
            while not self._connections.full():
                connection = self._create_connection()
                self._connections.put(connection)

    def close(self):
        with self._lock:
            while not self._connections.empty():
                connection = self._connections.get()
                connection.close()

    def table_exists(self, table_name: str) -> bool:
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None

    def create_table(self, table_name: str, sql_command):
        if self.table_exists(table_name):
            print(f"Table '{table_name}' already exists. Saved your ass! Exiting - to recreate use REcreate_table func:)")
            return

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        cursor.execute(sql_command)
        connection.commit()
        cursor.close()
        print(f"Table '{table_name}' created successfully.")
    
    def REcreate_table(self, table_name: str, sql_command):
        if self.table_exists(table_name):
            print(f"Table '{table_name}' already exists. Recreating.")
            return

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        cursor.execute(sql_command)
        connection.commit()
        cursor.close()
        print(f"Table '{table_name}' created successfully.")


def with_connection(f):
    @wraps(f)
    def wrapper(connection_pool, *args, **kwargs):
        connection = connection_pool.get_connection()
        try:
            return f(connection, *args, **kwargs)
        finally:
            pass # Add any cleanup operations here before releasing the connection
    return wrapper

@with_connection
def init_data(connection: Connection):
    c = connection.cursor()
    # Create the Skills table
    c.execute('''
        CREATE TABLE IF NOT EXISTS  Skills (
            Skill_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Description TEXT
        )
    ''')

    # Create the Sites table
    c.execute('''
        CREATE TABLE IF NOT EXISTS  Sites (
            Site_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Description TEXT
        )
    ''')

    # Create the SiteSkills table
    # Sample data representing the skills mapping for each site
    # site_skills = {
    #     "site1": "skill1,skill2,skill3",
    #     "site2": "skill4,skill5",
    #     "site3": "skill6"
    # }
    c.execute('''
        CREATE TABLE IF NOT EXISTS  SiteSkills (
            Site_ID TEXT,
            Skills TEXT,
            FOREIGN KEY (Site_ID) REFERENCES SupportAgents (Site_ID)
        )
    ''')
    # Insert the site skills mapping into the SiteSkills table
#    for site, skills in site_skills.items():
#        c.execute("INSERT INTO SiteSkills (Site, Skills) VALUES (?, ?)", (site, skills))


    # Create the Support Agents table
    c.execute('''
        CREATE TABLE IF NOT EXISTS  SupportAgents (
            Agent_ID INTEGER PRIMARY KEY,
            Nickname TEXT,
            Discord TEXT,
            Skills TEXT,
            Price_Map TEXT,
            Achievements TEXT,
            Verification_Status TEXT,
            Blue_Checkmark TEXT,
            Chat_ID INTEGER,
            Number_of_Executed_Tickets INTEGER,
            Positive_Reviews INTEGER,
            Preferred_Lang TEXT
        )
    ''')

    # Create the Clients table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Clients (
            Client_ID INTEGER PRIMARY KEY,
            Nickname TEXT,
            Discord_Client TEXT,
            Application_Description TEXT,
            Required_Skills TEXT,
            Application_Status TEXT
            Chat_ID INTEGER,
            Number_of_Resolved_Tickets INTEGER,
            Positive_Reviews INTEGER
        )
    ''')
    
    # Create the SupportTickets table
    c.execute('''
        CREATE TABLE IF NOT EXISTS SupportTickets (
            Ticket_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Assigned_Agent_ID INTEGER,
            Client_ID INTEGER,
            Site_ID INTEGER,
            Priority TEXT,
            State TEXT,
            Description TEXT,
            Comments TEXT,
            History TEXT,
            FOREIGN KEY (Assigned_Agent_ID) REFERENCES SupportAgents (Agent_ID),
            FOREIGN KEY (Client_ID) REFERENCES Clients (Client_ID),
            FOREIGN KEY (Site_ID) REFERENCES Site (Site_ID)
        )
    ''')

    # Create the QuizQuestions table with the additional fields
    c.execute('''
        CREATE TABLE IF NOT EXISTS QuizQuestions (
            Q_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Skill_ID INTEGER,
            Site_ID INTEGER,
            Question_text_ru TEXT,
            Question_text_en TEXT,
            Answer TEXT,
            Fake_answer TEXT,
            Clue_ru TEXT,
            Clue_en TEXT,
            Video_url TEXT,
            Vid_ID INTEGER,
            Vid_descr_local TEXT,
            Vid_guest_ID INTEGER,
            Vid_channel_ID INTEGER,
            Chapter_ID INTEGER,
            Timestamp TEXT,
            a_en TEXT,
            a_ru TEXT,
            fa_en TEXT,
            fa_ru TEXT, 
            FOREIGN KEY (Skill_ID) REFERENCES Skills(Skill_ID),
            FOREIGN KEY (Site_ID) REFERENCES Sites(Site_ID),
            FOREIGN KEY (Vid_ID) REFERENCES Videos(Vid_ID), 
            FOREIGN KEY (Vid_guest_ID) REFERENCES Guests(Guest_ID),
            FOREIGN KEY (Vid_channel_ID) REFERENCES Channels(Channel_ID),
            FOREIGN KEY (Chapter_ID) REFERENCES Chapters(Chapter_ID)
        )
    ''')

    # Create the Videos table with the additional fields
    c.execute('''
        CREATE TABLE IF NOT EXISTS Videos (
            Vid_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Skills TEXT,
            Video_url TEXT,
            Vid_article TEXT,
            Vid_descr TEXT,
            Vid_guest_ID INTEGER,
            Vid_channel_ID INTEGER,
            Chapters TEXT,
            Timestamp TEXT,
            FOREIGN KEY (Vid_guest_ID) REFERENCES Guests(Guest_ID),
            FOREIGN KEY (Vid_channel_ID) REFERENCES Channels(Channel_ID)
        )
    ''')

    # Create the Guests table with the additional fields
    c.execute('''
        CREATE TABLE IF NOT EXISTS Guests (
            Guest_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Bio TEXT,
            Guest_Channel_ID INTEGER,
            Achievements TEXT,
            FOREIGN KEY (Guest_Channel_ID) REFERENCES Channels(Channel_ID)
        )
    ''')

    # Create the Channels table with the additional fields
    c.execute('''
        CREATE TABLE IF NOT EXISTS Channels (
            Channel_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Bio TEXT,
            Achievements TEXT
        )
    ''')

    # Create Hello table just for lulz
    c.execute('''
        CREATE TABLE IF NOT EXISTS Hello (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            GG TEXT
        )
    ''')

    
    
    connection.commit()
    creategg(connection)



########################################
########### GENERAL FUNCS ##############
########################################
@with_connection
def get_data(connection: Connection, table_name):
    c = connection.cursor()
    c.execute(f"SELECT * FROM {table_name}")
    data = c.fetchall()
    return data

@with_connection
def insert_data(connection: Connection, table_name, data):
    c = connection.cursor()
    c.execute(f"INSERT INTO {table_name} VALUES (?)", (data,))
    connection.commit()

# Function to save the data from a table to a CSV file
@with_connection
def save_to_csv(connection: Connection, table_name, file_name):
    c = connection.cursor()
    c.execute(f'SELECT * FROM {table_name}')
    rows = c.fetchall()

    with open(file_name, 'w', newline='\n', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter = "\t")
        writer.writerow([description[0] for description in c.description])  # Write the column names
        writer.writerows(rows)  # Write the data rows

# Function to update a table from a CSV file
@with_connection
def update_from_tsv(connection: Connection, table_name, file_name):
    c = connection.cursor()

    with open(file_name, 'r', encoding="utf-8") as file:
        reader = csv.reader(file, delimiter = "\t")
        # Skip the first row as it contains the column names
        next(reader)
        for row in reader:
            if row[0] == "":
                break
            c.execute(f'REPLACE INTO {table_name} VALUES ({",".join(["?"] * len(row))})', row)

    connection.commit()







########################################
############# MAIN FUNCS ###############
########################################
def creategg(connection: Connection):
    # Connect to the SQLite database
    c = connection.cursor()

    # Insert the new support ticket into the SupportTickets table
    c.execute('''
        INSERT INTO Hello (ID, GG)
        VALUES (?, ?)
    ''', (None, "GG"))

# most important ones for managing support tickets. We'll optimize the functions for efficiency and ease of use. Here's a list of functions you might need:
#1. Function to Create a New Support Ticket:
@with_connection
def create_support_ticket(connection: Connection, Ticket_ID, Assigned_Agent_ID, Client_ID, Site_ID, Priority, State, Description, Comments, History, date, by_whom):
    History_str = "Created by " + by_whom + date
    
    # Connect to the SQLite database
    c = connection.cursor()

    # Insert the new support ticket into the SupportTickets table
    c.execute('''
        INSERT INTO SupportTickets (Ticket_ID, Assigned_Agent_ID, Client_ID, Site_ID, Priority, State, Description, Comments, History)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (Ticket_ID, Assigned_Agent_ID, Client_ID, Site_ID, Priority, State, Description, Comments, History_str))

    # Save changes and close the connection
    return connection.commit()

    
#This function allows you to create a new support ticket by providing the client's ID and the site's ID for which the ticket is created.

#2. Function to Change Ticket State:
@with_connection
def change_ticket_state(connection: Connection, ticket_id, new_state, date, by_whom):
    # Connect to the SQLite database
    c = connection.cursor()

    # Update the state of the specified ticket
    c.execute('''
        UPDATE SupportTickets
        SET State = ?
        WHERE Ticket_ID = ?
    ''', (new_state, ticket_id))

    # Save changes and close the connection
    connection.commit()
#This function allows you to update the state of a support ticket identified by its ticket ID.

#3. Function to Assign an Agent to a Ticket:
@with_connection
def assign_agent_to_ticket(connection: Connection, ticket_id, agent_id, date, by_whom):
    ticket_history = get_ticket_history(connection, ticket_id) + "\n" + "Agent assigned: " + get_support_agent_by_id(connection, agent_id)[1] + " by " + get_client_by_id(connection, by_whom)[1] + date
    
    # Connect to the SQLite database
    c = connection.cursor()

    # Update the assigned agent for the specified ticket
    c.execute('''
        UPDATE SupportTickets
        SET Assigned_Agent_ID = ?
        WHERE Ticket_ID = ?
    ''', (agent_id, ticket_id))

    # Save changes and close the connection
    connection.commit()
#This function allows you to assign an agent to a support ticket, given the ticket ID and the agent's ID.

#4. Function to Get All Open Tickets for an Agent:
@with_connection
def get_open_tickets_for_agent(connection: Connection, agent_id):
    # Connect to the SQLite database
    c = connection.cursor()

    # Retrieve all open tickets assigned to the specified agent
    c.execute('''
        SELECT Ticket_ID
        FROM SupportTickets
        WHERE Assigned_Agent_ID = ? AND State = 'Open'
    ''', (agent_id,))
    open_tickets = [row[0] for row in c.fetchall()]

    return open_tickets


#This function allows you to get a list of all open tickets assigned to a specific agent.

#5. Function to Get Ticket Details:
@with_connection
def get_ticket_details(connection: Connection, ticket_id):
    # Connect to the SQLite database
    c = connection.cursor()

    # Retrieve details of the specified ticket
    c.execute('''
        SELECT *
        FROM SupportTickets
        WHERE Ticket_ID = ?
    ''', (ticket_id,))
    ticket_details = c.fetchone()

    return ticket_details
#This function allows you to retrieve all details of a support ticket based on its ticket ID.

#Remember, you can further optimize these functions based on your specific requirements, and you may need to handle additional error cases or add more functionality as your platform evolves. Let me know if you need any further assistance or more functions!
#6. Function to Get Ticket State:
@with_connection
def get_ticket_state(connection: Connection, ticket_id):
    # Connect to the SQLite database and retrieve the ticket state
    # ...
    # Connect to the SQLite database
    c = connection.cursor()
    # Retrieve details of the specified ticket
    c.execute('''
        SELECT *
        FROM SupportTickets
        WHERE Ticket_ID = ?
    ''', (ticket_id,))
    ticket_details = c.fetchone()

    return ticket_details[5]
#This function retrieves the current state of a support ticket based on its ticket ID.

#7. Function to Update Ticket Priority:
@with_connection
def update_ticket_priority(connection: Connection, ticket_id, priority, date, by_whom):
    ticket_history = get_ticket_history(connection, ticket_id) + "\n" + "Priority was updateed: " + priority + " by " + by_whom + date

    # Connect to the SQLite database
    c = connection.cursor()
    # Update the assigned agent for the specified ticket
    c.execute('''
        UPDATE SupportTickets
        SET Priority = ?, History = ?
        WHERE Ticket_ID = ?
    ''', (priority, ticket_history, ticket_id))

    # Save changes and close the connection
    connection.commit()
#This function allows you to update the priority of a support ticket based on its ticket ID.

#8. Function to Get Ticket Assignee:
@with_connection
def get_ticket_assignee(connection: Connection, ticket_id):
    # Connect to the SQLite database and retrieve the assigned agent of the ticket
    c = connection.cursor()
    # Retrieve details of the specified ticket
    c.execute('''
        SELECT *
        FROM SupportTickets
        WHERE Ticket_ID = ?
    ''', (ticket_id,))
    ticket_details = c.fetchone()
    return ticket_details[1]#assignee
#This function retrieves the agent assigned to a support ticket based on its ticket ID.

#9. Function to Add a Comment to a Ticket:
@with_connection
def add_comment_to_ticket(connection: Connection, ticket_id, comment, date, by_whom):
    ticket_history = get_ticket_history(connection, ticket_id) + "\n" + "Comment addeded: " + comment + " by " + by_whom + date
    
    # Connect to the SQLite database and add a new comment to the ticket
    ticket_comments = get_ticket_comments(connection, ticket_id)
    ticket_comments += "\n\n" + comment 

    # Connect to the SQLite database and retrieve the comments of the ticket
    c = connection.cursor()
    # Update the assigned agent for the specified ticket
    c.execute('''
        UPDATE SupportTickets
        SET Comments = ?, History = ?
        WHERE Ticket_ID = ?
    ''', (ticket_comments, ticket_history, ticket_id))

    # Save changes and close the connection
    connection.commit()
#This function allows you to add a comment to a support ticket. The comment can be any additional information or updates related to the ticket.

#10. Function to Get Ticket Comments:
@with_connection
def get_ticket_comments(connection: Connection, ticket_id):
    # Connect to the SQLite database and retrieve the comments of the ticket
    c = connection.cursor()
    # Retrieve details of the specified ticket
    c.execute('''
        SELECT Comments
        FROM SupportTickets
        WHERE Ticket_ID = ?
    ''', (ticket_id,))
    ticket_comments = c.fetchone()
    return ticket_comments
#This function retrieves all the comments associated with a support ticket based on its ticket ID.

#11. Function to Close a Ticket:
@with_connection
def close_ticket(connection: Connection, ticket_id, date, by_whom):
    ticket_history = get_ticket_history(connection, ticket_id) + "\n" + "Date Of Closure: " + date + " by " + by_whom
    
    # Connect to the SQLite database and close the specified ticket
    c = connection.cursor()

    # Update the ticket
    c.execute('''
        UPDATE SupportTickets
        SET State = ?, History = ?
        WHERE Ticket_ID = ?
    ''', ( "Closed", ticket_history, ticket_id))

    # Save changes and close the connection
    connection.commit()
#This function changes the state of a support ticket to "Closed" based on its ticket ID.

#12. Get ticket history
@with_connection
def get_ticket_history(connection: Connection, ticket_id):
    # Connect to the SQLite database and close the specified ticket
    c = connection.cursor()

    # Retrieve details of the specified ticket
    c.execute('''
        SELECT History
        FROM SupportTickets
        WHERE Ticket_ID = ?
    ''', (ticket_id,))
    ticket_history = c.fetchone()
    return ticket_history

#13. 
@with_connection
def get_tickets(connection: Connection):
    c = connection.cursor()
    c.execute('''
        SELECT *
        FROM SupportTickets
    ''')
    sites = c.fetchall()
    return sites
#These functions should provide you with a good foundation for managing your support tickets in your platform. Remember to customize them according to your specific needs and database structure.

# Function that retrieves a list of agent IDs for agents who have the required skills for a support ticket, you can use the following code:
@with_connection
def get_agents_with_required_skills(connection: Connection, skills):
    c = connection.cursor()

    # Retrieve the agent IDs with the required skills
    c.execute('''
        SELECT Agent_ID
        FROM SupportAgents
        WHERE Skills LIKE ?
    ''', ('%{}%'.format(','.join(skills)),))
    agent_ids = [row[0] for row in c.fetchall()]

    return agent_ids

@with_connection
def create_skill(connection: Connection, name, description):
    c = connection.cursor()
    c.execute('''
        INSERT INTO Skills (Name, Description)
        VALUES (?, ?)
    ''', (name, description))
    # Save changes and return True to indicate successful update
    connection.commit()
    return True

@with_connection
def get_all_skills(connection: Connection):
    c = connection.cursor()
    c.execute('''
        SELECT *
        FROM Skills
    ''')
    skills = c.fetchall()

@with_connection
def get_skill_by_id(connection: Connection, skill_id):
    c = connection.cursor()
    c.execute('''
        SELECT *
        FROM Skills
        WHERE Skill_ID = ?
    ''', (skill_id,))
    skill = c.fetchone()

@with_connection
def get_skill_by_skill_name(connection: Connection, skill_name):
    c = connection.cursor()
    c.execute('''
        SELECT *
        FROM Skills
        WHERE Name = ?
    ''', (skill_name,))
    skill = c.fetchone()

@with_connection
def get_skill_id_by_skill_name(connection: Connection, skill_name):
    c = connection.cursor()
    c.execute('''
        SELECT *
        FROM Skills
        WHERE Name = ?
    ''', (skill_name,))
    try:
        skill_id = c.fetchone()[0]
    except Exception as e:
        skill_id = ""
    
    return skill_id

#2. Functions for the "Site" table:
@with_connection
def create_site(connection: Connection, name, description):
    c = connection.cursor()
    c.execute('''
        INSERT INTO Sites (Name, Description)
        VALUES (?, ?)
    ''', (name, description))
    # Save changes and return True to indicate successful update
    connection.commit()
    return True

@with_connection
def get_all_sites(connection: Connection):
    c = connection.cursor()
    c.execute('''
        SELECT *
        FROM Sites
    ''')
    sites = c.fetchall()

@with_connection
def get_site_by_id(connection: Connection, site_id):
    c = connection.cursor()
    c.execute('''
        SELECT *
        FROM Sites
        WHERE id = ?
    ''', (site_id,))
    site = c.fetchone()
    return site

#3. Functions for the "SupportAgents" table:
@with_connection
def create_support_agent(connection: Connection, agent_id, nickname, discord, skills, price_map, achievements, verification_status, blue_checkmark, chat_id, number_of_executed_tickets, positive_reviews, lang):
    c = connection.cursor()
    c.execute('''
        INSERT INTO SupportAgents (Agent_ID, Nickname, Discord, Skills, Price_Map, Achievements, Verification_Status, Blue_Checkmark, Chat_ID, Number_of_Executed_Tickets, Positive_Reviews, Preferred_Lang)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (agent_id, nickname, discord, skills, price_map, achievements, verification_status, blue_checkmark, chat_id, number_of_executed_tickets, positive_reviews, lang))
    # Save changes and return True to indicate successful update
    connection.commit()
    return True
# Agent_ID INTEGER PRIMARY KEY AUTOINCREMENT,
# Nickname TEXT,
# Discord TEXT,
# Skills TEXT,
# Price_Map TEXT,
# Achievements TEXT,
# Verification_Status TEXT,
# Blue_Checkmark TEXT,
# Chat_ID INTEGER,
# Number_of_Executed_Tickets INTEGER,
# Positive_Reviews INTEGER,
# Preferred_Lang TEXT


@with_connection
def get_all_support_agents(connection: Connection):
    c = connection.cursor()
    c.execute('''
        SELECT *
        FROM SupportAgents
    ''')
    support_agents = c.fetchall()
    return support_agents

@with_connection
def get_support_agent_by_id(connection: Connection, agent_id):
    c = connection.cursor()
    c.execute('''
        SELECT *
        FROM SupportAgents
        WHERE Agent_ID = ?
    ''', (agent_id,))
    support_agent = c.fetchone()
    return support_agent

@with_connection
def get_support_agent_by_nickname(connection: Connection, agent_nickname):
    c = connection.cursor()
    c.execute('''
        SELECT *
        FROM SupportAgents
        WHERE Nickname = ?
    ''', (agent_nickname,))
    support_agent = c.fetchone()
    return support_agent


#4. Functions for the "Clients" table:
@with_connection
def create_client(connection: Connection, client_id, nickname, discord_client, application_description, required_skills, application_status, chat_id, number_of_resolved_tickets, positive_peviews, preferred_lang):
    c = connection.cursor()
    c.execute('''
        INSERT INTO Clients (Client_ID, Nickname, Discord_Client, Application_Description, Required_Skills, Application_Status, Chat_ID, Positive_Reviews, Preferred_Lang)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (client_id, nickname, discord_client, application_description, required_skills, application_status, chat_id, number_of_resolved_tickets, positive_peviews, preferred_lang))

    # Save changes and return True to indicate successful update
    connection.commit()
    return True
# Client_ID INTEGER PRIMARY KEY,
# Nickname TEXT,
# Discord_Client TEXT,
# Application_Description TEXT,
# Required_Skills TEXT,
# Application_Status TEXT
# Chat_ID INTEGER,
# Number_of_Resolved_Tickets INTEGER,
# Positive_Reviews INTEGER


@with_connection
def get_all_clients(connection: Connection):
    c = connection.cursor()
    c.execute('''
        SELECT *
        FROM Clients
    ''')
    clients = c.fetchall()

@with_connection
def get_client_by_id(connection: Connection, client_id):
    c = connection.cursor()
    c.execute('''
        SELECT *
        FROM Clients
        WHERE Client_ID = ?
    ''', (client_id,))
    client = c.fetchone()


#5. Functions for the "AgentStatistics" portion of SupportAgents table:
@with_connection
def get_all_agent_statistics(connection: Connection):
    c = connection.cursor()
    c.execute('''
        SELECT Agent_ID, Number_of_Requests, Number_of_Executed_Requests, Positive_Reviews
        FROM SupportAgents
    ''')
    agent_statistics = c.fetchall()

@with_connection
def get_agent_statistics_by_id(connection: Connection, agent_id):
    c = connection.cursor()
    c.execute('''
        SELECT Agent_ID, Number_of_Requests, Number_of_Executed_Requests, Positive_Reviews
        FROM SupportAgents
        WHERE Agent_ID = ?
    ''', (agent_id,))
    agent_statistics = c.fetchone()
# One essential function that I recommend is a function to update the details of a support agent. This function allows you to modify the information of a support agent in the database. Here's an example implementation:
@with_connection
def update_support_agent(connection: Connection, agent_id, name=None, discord=None, skills=None, price_map=None, achievements=None, verification_status=None, blue_checkmark=None):
    support_agent = get_support_agent_by_id(connection, agent_id)
    
    if not support_agent:
        # Support agent with the provided ID does not exist
        return False
    
    c = connection.cursor()
    # Update the support agent's details if provided
    if name:
        support_agent['Name'] = name
    if discord:
        support_agent['Discord'] = discord
    if skills:
        support_agent['Skills'] = skills
    if price_map:
        support_agent['Price_Map'] = price_map
    if achievements:
        support_agent['Achievements'] = achievements
    if verification_status:
        support_agent['Verification_Status'] = verification_status
    if blue_checkmark:
        support_agent['Blue_Checkmark'] = blue_checkmark
    
    # Update the support agent in the database
    c.execute('''
        UPDATE SupportAgents
        SET Name = ?, Discord = ?, Skills = ?, Price_Map = ?, Achievements = ?, Verification_Status = ?, Blue_Checkmark = ?
        WHERE Agent_ID = ?
    ''', (support_agent['Name'], support_agent['Discord'], support_agent['Skills'], support_agent['Price_Map'], support_agent['Achievements'], support_agent['Verification_Status'], support_agent['Blue_Checkmark'], agent_id))
    
    # Save changes and return True to indicate successful update
    connection.commit()
    return True
#This function allows you to update various details of a support agent, such as their name, Discord ID, skills, price map, achievements, verification status, and blue checkmark. It verifies if the support agent with the given ID exists using the get_support_agent_by_id function. If the support agent exists, it updates the provided details and executes an SQL UPDATE statement to modify the corresponding row in the "SupportAgents" table.
#Here are some second-tier functions that can utilize the first-tier getter and setter functions we have implemented:

#1. Function to Get All Skills of an Agent:
@with_connection
def get_skills_of_agent(connection: Connection, agent_id):
    agent = get_support_agent_by_id(connection, agent_id)
    if agent:
        skills = [get_skill_by_id(connection, skill_id) for skill_id in agent['Skills'].split(',')]
        return skills
    return []
#This function retrieves all the skills of a support agent based on their agent ID. It calls the get_support_agent_by_id function to retrieve the agent's details, and then uses the get_skill_by_id function to retrieve the skill details for each skill ID associated with the agent.


#2. Function to Get All Tickets for a Client:
@with_connection
def get_all_tickets_for_client(connection: Connection, client_id):
    return [get_ticket_details(connection, ticket_id) for ticket_id in get_client_by_id(connection, client_id)['Ticket_ID']]
#This function retrieves all the tickets for a client based on their client ID. It calls the get_client_by_id function to retrieve the client's details, and then iterates over the list of ticket IDs associated with the client, calling the get_ticket_details function for each ticket ID to retrieve the ticket details.


#3. Function to Get Agents with Highest Positive Reviews:
@with_connection
def get_agents_with_highest_positive_reviews(connection: Connection, num_agents):
    agent_statistics = get_all_agent_statistics(connection)
    agent_statistics.sort(key=lambda x: x['Positive_Reviews'], reverse=True)
    return [get_support_agent_by_id(connection, stats['Agent_ID']) for stats in agent_statistics[:num_agents]]
#This function retrieves the agents with the highest number of positive reviews. It calls the get_all_agent_statistics function to retrieve the agent statistics, sorts them based on the positive reviews in descending order, and then retrieves the agent details using the get_support_agent_by_id function for the selected agents.

#4. Function to Get Sites with Required Skills:
@with_connection
def get_sites_with_required_skills(connection: Connection, required_skills):
    sites = get_all_sites(connection)
    return [site for site in sites if all(skill in site['Skills'] for skill in required_skills)]
#This function retrieves the sites that have all the required skills. It calls the get_all_sites function to retrieve all the sites, and then filters the sites based on whether they contain all the required skills using the all function with a list comprehension.


#Here are some second-tier functions that can utilize the first-tier getter and setter functions we have implemented:
#1. Function to Get All Skills of an Agent:
@with_connection
def get_skills_of_agent(connection: Connection, agent_id):
    agent = get_support_agent_by_id(connection, agent_id)
    if agent:
        skills = [get_skill_by_skill_name(connection, skill_name) for skill_name in agent['Skills'].split(',')]
        return skills
    return []
#This function retrieves all the skills of a support agent based on their agent ID. It calls the get_support_agent_by_id function to retrieve the agent's details, and then uses the get_skill_by_id function to retrieve the skill details for each skill ID associated with the agent.

#2. Function to Get All Tickets for a Client:
@with_connection
def get_all_tickets_for_client(connection: Connection, client_id):
    return [get_ticket_details(connection, ticket_id) for ticket_id in get_client_by_id(client_id)['Ticket_ID']]
#This function retrieves all the tickets for a client based on their client ID. It calls the get_client_by_id function to retrieve the client's details, and then iterates over the list of ticket IDs associated with the client, calling the get_ticket_details function for each ticket ID to retrieve the ticket details.

#3. Function to Get Agents with Highest Positive Reviews:
@with_connection
def get_agents_with_highest_positive_reviews(connection: Connection, num_agents):
    agent_statistics = get_all_agent_statistics(connection)
    agent_statistics.sort(key=lambda x: x['Positive_Reviews'], reverse=True)
    return [get_support_agent_by_id(connection, stats['Agent_ID']) for stats in agent_statistics[:num_agents]]
#This function retrieves the agents with the highest number of positive reviews. It calls the get_all_agent_statistics function to retrieve the agent statistics, sorts them based on the positive reviews in descending order, and then retrieves the agent details using the get_support_agent_by_id function for the selected agents.

#4. Function to Get Sites with Required Skills:
@with_connection
def get_sites_with_required_skills(connection: Connection, required_skills):
    sites = get_all_sites(connection)
    return [site for site in sites if all(skill in site['Skills'] for skill in required_skills)]
#This function retrieves the sites that have all the required skills. It calls the get_all_sites function to retrieve all the sites, and then filters the sites based on whether they contain all the required skills using the all function with a list comprehension.

#These are just a few examples of second-tier functions that can be built upon the first-tier getter and setter functions. You can continue to build more complex functionality using these basic building blocks to suit your specific requirements.

# Create the function to get a random question for a given skill_id
@with_connection
def get_random_question_for_skill(connection: Connection, skill_id):
    c = connection.cursor()
    c.execute('''
        SELECT * FROM QuizQuestions
        WHERE (Skill_ID = ?)
        ORDER BY RANDOM()
    ''', (skill_id,))
    question_all = c.fetchone()
    question = question_all[3]
    a = question_all[5]
    fa = question_all[6]
    clue_ru = question_all[7]
    clue_en = question_all[8]
    a_en = question_all[16]
    fa_en = question_all[18]
    #
    #  AND (Q_ID > 0 ) AND (Q_ID < 350)#        LIMIT 1
    return question, a , fa, clue_ru, clue_en, a_en, fa_en

def main(): 
    # Initialize connection pool with maximum number of connections 
    connection_pool = ConnectionPool(max_connections=5) 
    #connection_pool.__init__() 
    
    # Example usage
    init_data(connection_pool)
    data = get_data(connection_pool, "Hello") 
    print(data)

    # # Create the QuizQuestions table # 
    ##########################
    # # Get the absolute path to the file
    # file_path = os.path.abspath("telegram_bot\\db\\69UI_questions4tgBot_withClues.tsv")
    # # Check if the file exists
    # if os.path.exists(file_path):
    #     update_from_tsv(connection_pool, "QuizQuestions", file_path)
    # else:
    #     print(f"File not found!: {file_path}")
    #     save_to_csv(connection_pool, "QuizQuestions", file_path)

    # connection_pool.create_table("QuizQuestions", '''
    #     CREATE TABLE IF NOT EXISTS QuizQuestions (
    #         Q_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    #         Skill_ID INTEGER,
    #         Site_ID INTEGER,
    #         Question_text_ru TEXT,
    #         Question_text_en TEXT,
    #         Answer TEXT,
    #         Fake_answer TEXT,
    #         Clue_ru TEXT,
    #         Clue_en TEXT,
    #         Video_url TEXT,
    #         Vid_ID INTEGER,
    #         Vid_descr_local TEXT,
    #         Vid_guest_ID INTEGER,
    #         Vid_channel_ID INTEGER,
    #         Chapter_ID INTEGER,
    #         Timestamp TEXT,
    #         a_en TEXT,
    #         a_ru TEXT,
    #         fa_en TEXT,
    #         fa_ru TEXT, 
    #         FOREIGN KEY (Skill_ID) REFERENCES Skills(Skill_ID),
    #         FOREIGN KEY (Site_ID) REFERENCES Sites(Site_ID),
    #         FOREIGN KEY (Vid_ID) REFERENCES Videos(Vid_ID), 
    #         FOREIGN KEY (Vid_guest_ID) REFERENCES Guests(Guest_ID),
    #         FOREIGN KEY (Vid_channel_ID) REFERENCES Channels(Channel_ID),
    #         FOREIGN KEY (Chapter_ID) REFERENCES Chapters(Chapter_ID)
    #     )
    # ''')


    # # Create the Skill table
    ##########################
    # file_path = os.path.abspath("telegram_bot\\db\\UI_questions4tgBot - Skills.tsv")
    # # Check if the file exists
    # if os.path.exists(file_path):
    #     update_from_tsv(connection_pool, "Skills", file_path)
    # else:
    #     print(f"File not found!: {file_path}")
    #     save_to_csv(connection_pool, "Skills", file_path)
    # data = get_data(connection_pool, "Skills") 
    # print(data) 
    
    
    # connection_pool.create_table("Skills", '''
    #     CREATE TABLE Skills (
    #         Skill_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    #         Name TEXT,
    #         Description TEXT
    #     )
    # ''')


    # # Create the Support Agents table
    ##########################
    # # Get the absolute path to the Agents tsv file
    # file_path = os.path.abspath("telegram_bot\\db\\Agents.tsv")
    # # Check if the file exists
    # if os.path.exists(file_path):
    #     print(file_path)
    #     update_from_tsv(connection_pool, "SupportAgents", file_path)
    # else:
    #     print(f"File not found!: {file_path}")
    #     save_to_csv(connection_pool, "SupportAgents", file_path)
    # data = get_data(connection_pool, "SupportAgents") 
    # print(data) 

    # connection_pool.create_table("SupportAgents", '''
    #     CREATE TABLE IF NOT EXISTS SupportAgents (
    #         Agent_ID INTEGER PRIMARY KEY,
    #         Nickname TEXT,
    #         Discord TEXT,
    #         Skills TEXT,
    #         Price_Map TEXT,
    #         Achievements TEXT,
    #         Verification_Status TEXT,
    #         Blue_Checkmark TEXT,
    #         Chat_ID INTEGER,
    #         Number_of_Executed_Tickets INTEGER,
    #         Positive_Reviews INTEGER,
    #         Preferred_Lang TEXT
    #     )
    # ''')

    # # Create the Clients table
    ##########################
    #connection_pool.create_table("Clients", '''
    connection_pool.REcreate_table("Clients", '''
        CREATE TABLE IF NOT EXISTS Clients (
            Client_ID INTEGER PRIMARY KEY,
            Nickname TEXT,
            Discord_Client TEXT,
            Application_Description TEXT,
            Required_Skills TEXT,
            Application_Status TEXT
            Chat_ID INTEGER,
            Number_of_Resolved_Tickets INTEGER,
            Positive_Reviews INTEGER,
            Preferred_Lang TEXT
        )
    ''')
    data = get_data(connection_pool, "Clients") 
    print(data)

    # # Create the SupportTickets table
    ##########################
    #connection_pool.create_table('''
    connection_pool.REcreate_table("SupportTickets", '''
        CREATE TABLE IF NOT EXISTS SupportTickets (
            Ticket_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Assigned_Agent_ID INTEGER,
            Client_ID INTEGER,
            Site_ID INTEGER,
            Priority TEXT,
            State TEXT,
            Description TEXT,
            Comments TEXT,
            History TEXT,
            FOREIGN KEY (Assigned_Agent_ID) REFERENCES SupportAgents (Agent_ID),
            FOREIGN KEY (Client_ID) REFERENCES Clients (Client_ID),
            FOREIGN KEY (Site_ID) REFERENCES Site (Site_ID)
        )
    ''')
    data = get_data(connection_pool, "SupportTickets") 
    print(data)





    # # MISC # #
    ############
    #insert_data("New data") 
    #file_path = os.path.abspath("telegram_bot\\db\\input_file.txt")
    #db_helper.process_strings(file_path)




    # Close the connection pool when done 
    connection_pool.close()

if __name__ == '__main__':
    main()