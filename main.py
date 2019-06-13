import discord
import asyncio
import json
import gspread
import re
from datetime import datetime
from doc_scan import DocScanner
from help_text import help_embed, API_error


class RedemptionBot(discord.Client):
    """Discord client for all Redemption Bot operations"""

    def __init__(self, doc, configs):
        super().__init__()
        self.token = configs['Bot Token']
        self.admin_name = configs['Admin Rank']
        self.doc = doc
        self.start_bot()

    def start_bot(self):
        """Connects discord API"""
        loop = asyncio.get_event_loop()
        loop.create_task(self.start(self.token))
        try:
            loop.run_forever()
        finally:
            loop.stop()

    async def on_ready(self):
        print('Logged in successfully')
        print(self.user.name)
        print(self.user.id)
        print('-' * 5)
        game = discord.Game('!splits_help')
        await self.change_presence(activity=game)

    async def on_message(self, message):
        """Bot commands via text inputs"""
        # Prevent bot responding to itself
        if message.author == self.user:
            return

        # Verify command was sent
        command = re.search(r'^![a-z_]+', message.content)
        if command is None:
            return

        # Prepares basic variables
        command = command.group()
        command = command.replace('!', '')
        msg = message.content.replace(f'!{command}', '').strip()
        author = message.author
        channel = message.channel
        guild = channel.guild
        isAdmin = str(author.roles).find(self.admin_name) != -1
        
        try:
            await self.check(command, msg, author, channel, guild, isAdmin)
        except gspread.exceptions.APIError:
            await channel.send(API_error)



    async def check(self, command, msg, author, channel, guild, isAdmin):
        """Commands:
        !check
        !update
        !add
        !splits_help
        """
        if command == 'check':
            # Request to find information on member
            print(f'User {author}: Checking for "{msg}"')
            await channel.trigger_typing()
            await self.send_user(msg, channel, guild)
            
        if command == 'update' and isAdmin:
            print(f'User {author} updating: "{msg}"')
            await channel.trigger_typing()

            # Updates user info (!update <name>, <split change>, <items>)
            inputs = msg.split(',')

            # Name:
            name = inputs[0].strip()
            # Delta Values:
            try: 
                delta = int(inputs[1])
            except(ValueError, SyntaxError, TypeError, IndexError):
                await channel.send("Incorrect format, see !splits_help")
                return
            # Gathers items
            items = ', '.join(inputs[2:]).strip() if len(inputs) > 2 else None

            # Updates sheet
            updates = self.doc.update_split(name, delta, items)
            if updates is None:
                await channel.send(f'Cant find "{name}" on the sheet')
                return
            

            # Builds Embed
            prev_val, new_val, old_items, new_items = updates
            em_title = f"Splits increased by {delta:,}!"
            em_desc = f"-----"
            em_author = f"Updating {name}'s stats"
            em_url = None
            em_color = 0x01b0cf
            em_name_a = "Old Splits"
            em_val_a = "{:,}".format(prev_val)
            em_name_b = "New Splits"
            em_val_b = "{:,}".format(new_val)
            em_name_c = "Old Items"
            em_val_c = old_items
            em_name_d = "New Items"
            em_val_d = new_items

            player = guild.get_member_named(name)
            if player is not None:
                em_url = str(player.avatar_url)

            embed = discord.Embed(
                title=em_title, 
                description=em_desc, 
                color=em_color
            )
            if em_url is not None:
                embed.set_author(name=em_author, icon_url=em_url)
            else:
                embed.set_author(name=em_author)
            embed.add_field(name=em_name_a, value=em_val_a, inline=True)
            embed.add_field(name=em_name_b, value=em_val_b, inline=True)
            embed.add_field(name=em_name_c, value=em_val_c, inline=False)
            embed.add_field(name=em_name_d, value=em_val_d, inline=False)

            await channel.send(embed=embed)

        if command == 'add' and isAdmin:
            print(f'User {author} adding: "{msg}"')
            await channel.trigger_typing()

            # Grabs inputs 
            inputs = msg.split(',')
            name = None
            splits = 0
            date = None
            items = []

            for i in range(len(inputs)):
                if i == 0:
                    name = inputs[i].strip()
                    if name == '':
                        await channel.send('I need a name (see !splits_help)')
                        return 
                elif i == 1:
                    try:
                        splits = int(inputs[i].strip())
                    except (ValueError, SyntaxError, TypeError, IndexError):
                        await channel.send('Incorrect splits format (see !splits_help)')
                        return
                elif i == 2:
                    date_format = r'^[0-1]?[0-9]/[0-3]?[0-9]/20[0-9][0-9]$'
                    check = re.match(date_format, inputs[i].strip())
                    if check is None:
                        await channel.send('Incorrect date format (see !splits_help)')
                        return 
                    date = check.group()
                    try:
                        datetime.strptime(date, r'%m/%d/%Y')
                    except ValueError:
                        await channel.send('Incorrect date format (see !splits_help)')
                        return 
                else:
                    items.append(inputs[i])
            item_list = ', '.join(items)

            # Attempts to add based on provided info
            results = self.doc.add_user(name, splits, date, item_list)

            if results is None:
                await channel.send('User already exists!')
            else:
                await self.send_user(name, channel, guild)

        if command == 'splits_help':
            await channel.trigger_typing()
            # Sends help text
            em = help_embed
            emb = discord.Embed(
                title=em['title'], 
                description=em['desc'], 
                color=0x01b0cf
            )
            v_up = em['v_up'].replace('@ADMIN', self.admin_name)
            v_add = em['v_add'].replace('@ADMIN', self.admin_name)
            emb.add_field(name=em['n_check'], value=em['v_check'], inline=False)
            emb.add_field(name=em['n_up'], value=v_up, inline=False)
            emb.add_field(name=em['n_add'], value=v_add, inline=False)
            emb.set_footer(text=em['footer'])
            await channel.send(embed=emb)


    async def send_user(self, name, channel, guild):
        # Send embed with splits info

        values = self.doc.get_split(name)
        if values is None:
            await channel.send(f'Can\'t find someone named "{name}"')
            return

        # Prepares display values
        splits = values[1]
        days = values[3]
        rank = values[4]
        avatar = None

        player = guild.get_member_named(name)
        if player is not None:
            avatar = str(player.avatar_url)
        
        # Build embed
        em_title = "Split Value:"
        em_desc = "{:,}".format(splits)
        em_color = 0x01b0cf
        em_author = f"{name}'s stats:"
        em_url = avatar
        em_name_a = "Current Rank: "
        em_value_a = f'{rank}'
        em_name_b = "Days in Clan: "
        em_value_b = f'{days} days'

        embed = discord.Embed(
            title=em_title, 
            description=em_desc, 
            color=em_color
        )
        if em_url is not None:
            embed.set_author(name=em_author, icon_url=em_url)
        else:
            embed.set_author(name=em_author)
        embed.add_field(name=em_name_a, value=em_value_a, inline=False)
        embed.add_field(name=em_name_b, value=em_value_b, inline=False)

        await channel.send(embed=embed)


def start():
    print("Initiating...")
    try:
        with open("configs.json", "r") as configs_file:
            print("configs.json file loaded")
            configs = json.loads(configs_file.read())
    except(FileNotFoundError):
        print('ERROR: Configs file not found, please consult Readme')
        return

    # Verifies configs
    reqs = ("Bot Token", "Admin Rank", "Spreadsheet URL", "Worksheet Name")
    if not all(req in configs for req in reqs):
        print('ERROR: Configs not formatting correctly, please consult the Readme')
        return

    # Opens document
    print('Loading Google sheet...')
    try:
        doc = DocScanner(configs["Spreadsheet URL"], configs["Worksheet Name"])
        print("Document loaded correctly")
    except(gspread.exceptions.NoValidUrlKeyFound): 
        print("ERROR: Document could not be loaded from the URL")
        invalid_input()
    except(gspread.exceptions.WorksheetNotFound):
        print("ERROR: Document could not find worksheet " + worksheet)
        invalid_input()
    except(FileNotFoundError):
<<<<<<< Updated upstream
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
=======
        print("ERROR: Credentials file not found, please consult Readme")
>>>>>>> Stashed changes

    # Loads bot API
    print('Loading discord bot...')
    redemption_bot = RedemptionBot(doc, configs)
    
    # Shuts down
    print('Bot successfully shut down')
    print('Good bye')
    



<<<<<<< Updated upstream
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
=======
if __name__ == "__main__":
    start()
>>>>>>> Stashed changes
