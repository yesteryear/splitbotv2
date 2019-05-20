import sys
import asyncio 
import time
import discord
import json
import gspread
import help_text
from doc_scan import DocScanner
from datetime import datetime

client = discord.Client()

def print_log(text, delay=0.35):
    """Prints message with time in console and to log file"""
    curTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = curTime + " - " + str(text)
    print(message)
    with open("Log.txt", "a") as logger:
        logger.write(message + "\n")
    time.sleep(delay)


def validate_date(given_date):
    """Confirms format of the date to match dd/mm/YYYY or mm/dd/YYYY"""
    try:
        datetime.strptime(given_date, "%m/%d/%Y")
        return True
    except(ValueError, TypeError):
        return False


def invalid_input():
    print_log(help_text.Invalid_Input)
    sys.exit()


def first_time_setup():
    print_log("Please answer the following questions", 1)
    print_log("Please ensure Google API credentials are setup as per Readme", 1)
    print_log("Press enter to continue", 1)
    input()

    configs = {}
    print_log("1. Enter the Bot Token from the discord developement page (consult Readme for more info)")
    configs["Bot Token"] = str(input()).strip()

    print_log("2. Enter the EXACT name of the required rank for bot admin commands")
    configs["Admin Rank"] = str(input()).strip()

    print_log("3. Enter the exact URL of the spreadsheet")
    configs["Spreadsheet URL"] = str(input()).strip()

    print_log("4. Enter the exact name of the worksheet (or tab) of the google doc")
    configs["Worksheet Name"] = str(input()).strip()


    with open("configs.json", "w") as file:
        json.dump(configs, file, indent=4)

    return configs


# Initiates bot, verifies all settings then launches Docs API
try:
    print_log("=" * 10)
    print_log("=" * 10)
    print_log("Welcome! Initializing bot...")


    # Loads configs file, if configs file does not exist initiates first time setup
    try:
        print_log("Loading Configs File...")
        configs = {}
        # Opens and loads configs file
        with open("configs.json", "r") as configs_file:
            print_log("configs.json file loaded")
            configs = json.load(configs_file)
    # If Configs/configs.json does not exist, initiates FTS
    except(FileNotFoundError):
        print_log("configs.json was not found, initiating First Time Setup", 2)
        configs = first_time_setup()


    # Verifies all entries and google credentials file exist. 
    print_log("Verifying configuration settings...")
    try:
        file = open("credentials.json", "r")
        file.close()
    except(FileNotFoundError):
        print_log("credentials.json was not found, please consult the Readme")
        sys.exit()

    req_configs = (
        "Bot Token", 
        "Admin Rank",
        "Spreadsheet URL",
        "Worksheet Name",
    )
    try:
        for req in req_configs:
            configs[req]
    except(KeyError):
        print_log("One or more of the required configs missing.")
        invalid_input()

    print(json.dumps(configs, indent=4))
    print_log(help_text.Initial_Message, 3)

    print_log("-" * 5)

    # Prepares to open sheet, if error encounters exists application
    print_log("Preparing to open spreadsheet...")

    # Initiates spreadsheet or catches error when failed
    url = configs["Spreadsheet URL"]
    worksheet = configs["Worksheet Name"]
    print_log("Loading document...")
    try:
        doc = DocScanner(url, worksheet)
        print_log("Document loaded correctly")
    except(gspread.exceptions.NoValidUrlKeyFound): 
        print_log("ERROR: Document could not be loaded from the URL")
        invalid_input()
    except(gspread.exceptions.WorksheetNotFound):
        print_log("ERROR: Document could not find worksheet " + worksheet)
        invalid_input()
    except(FileNotFoundError):
        print_log("ERROR: Credentials file could not be found")
        print_log("Please obtain credentials as outlined in the Readme")

    admin_rank = configs["Admin Rank"]
    token = configs["Bot Token"]


except(SystemExit):
    print_log("Press enter to exit...")
    input()



@client.event
async def on_message(message):
    """Initiates command by bot based on inputs"""

    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    author = message.author.name
    admin = str(message.author.roles).find(admin_rank) != -1

    incorrect_input_message = {
        "int": "Please enter a number without commas or symbols for the split.",
        "date": "Please make sure date format is M/D/YYYY."
    }

    try:
        if message.content.startswith("!splits "):
            print_log("User {}: {}".format(author, message.content))
            """Returns splits by user request"""
            msg = message.content
            username = msg.replace("!splits", "").strip()
            response = await doc.get_split(username)
            print(response)
            if response is None:
                reply = "Can't find the name {} in the list!".format(username)
            else:
                name = response[1]
                amount = response[0]
                reply = "{} has an item split of {:,}!".format(name, amount)
            await message.channel.send(reply)
            print_log(reply)
            
        if message.content.startswith("!update ") and admin is True:
            print_log("User {}: {}".format(author, message.content))
            """Adds split amount if user has admin rank"""
            msg = message.content

            # Splits input 
            request = msg.replace("!update", "").split(",")

            # Grabs name
            name = request[0].strip()

            # Gets splits value, if value was invalid prints appropriate message
            try:
                delta = int(request[1].strip())
            except(ValueError, SyntaxError, TypeError, IndexError):
                delta = None

            # Gets list of items if it exists
            item_list = ", ".join(request[2:]).strip() if len(request) > 2 else None
            
            # Updates split value and sends response to discord server
            if delta is not None:
                response = await doc.update_split(name, delta, item_list)
                if response is not None:
                    username = response[2]
                    prev_val = response[0]
                    new_val = response[1]
                    reply = "{}'s split changed from {:,} to {:,}.".format(
                        username,
                        prev_val, 
                        new_val
                    )
                else:
                    reply = "Can't find player {}".format(name)
            else:
                reply = incorrect_input_message["int"]

            await message.channel.send(reply)
            print_log(reply)

        if message.content.startswith("!add ") and admin is True:
            print_log("User {}: {}".format(author, message.content))
            """Adds user with inputs (!add_user name (split) (date) (items))"""
            msg = message.content

            # Splits input 
            request = msg.replace("!add", "").split(",")

            # Grabs name
            name = request[0].strip()
            reply = "The player {} was added".format(name)

            # Will prevent the doc API call if the provided inputs are incorrect
            validate_inputs = True
            splits = 0
            date = None
            item_list = ''

            # Gets and confirms split value
            if len(request) > 1:
                try:
                    split = int(request[1].strip())
                    reply += " with a split value of {}".format(split)
                except(TypeError, ValueError):
                    validate_inputs = False
                    reply = incorrect_input_message["int"]

            # Gets and confirms date value
            if (len(request) > 2) and (validate_inputs is True):
                date = request[2].strip()
                if validate_date(date) is True:
                    reply += ", and the join date {}".format(date)
                else:
                    validate_inputs = False
                    reply = incorrect_input_message["date"]

            # Gets list of items
            item_list = ", ".join(request[3:]).strip() if len(request) > 2 else ""

            if validate_inputs is True:
                reply += "!"
                added = await doc.add_user(name, splits, date, item_list)
                if added is False:
                    reply = "User {} already exists!".format(name)

            await message.channel.send(reply)
            print_log(reply)

    except(gspread.exceptions.APIError):
        reply = help_text.API_error
        await message.channel.send(reply)

    if message.content.startswith("!help"):
        print_log("User {}: {}".format(author, message.content))
        reply = help_text.help_reply
        if admin is True:
            reply = reply + "\n" + help_text.admin_help_reply
        await message.channel.send(reply)

    # Exit command - for debugging purposes only
    # if message.content.startswith("!exit"):
    #    await client.logout()


@client.event
async def on_ready():
    print_log("Logged in as")
    print_log(client.user.name)
    print_log(client.user.id)
    print_log("------")

# Initiates dicord API
try:
    print_log("Initiating Discord API...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.start(token))
except(discord.errors.LoginFailure):
    print_log("ERROR: Token was not accepted or correct")
    invalid_input()
except(discord.errors.GatewayNotFound, discord.errors.HTTPException):
    print_log("ERROR: Cannot load discord API")
    print_log("This can be due to lack of internet connection or API outage")
    print_log("Please try again later")
    sys.exit()
except(SystemExit):
    print_log("Press enter to exit...")
    input()
