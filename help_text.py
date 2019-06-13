# This only exists so my main file doesnt have this massive blob of text in the middle

<<<<<<< Updated upstream
help_reply = """**!splits <Runescape name>: Gets the splits for the given user**
e.g. !splits Jagax 
"""

admin_help_reply = """These commands are for admins only:

**!update <Runescape name>, <amount>, <list of items>:**
Adds <amount> to the player's split (accepts negative numbers). *Do NOT add commas in the number or you'll break everything*. 
e.g. !update INGAME_GAME, 500000
e.g. !update INGAME_GAME, 17000, Theatre of Blood Cabbages x500

**!add INGAME_GAME, <splits>, <join date>, <items>:**
Creates the user if that name doesnt already exist. You can also set their starting split, join date, and items. While these last three are optional, they must be added in that order (e.g. if you have a date but no starting split value, you must enter 0 for splits).
If no join date is added, it defaults to today's date. Dates must also be of the form MM/DD/YYYY. 
examples: 
!add INGAME_GAME
!add INGAME_GAME, 500000, 5/20/2019, Ancestral Robe Top, Dexterous Prayer Scroll
!add INGAME_GAME, 0, 1/30/2019
"""

API_error = """API Error! There's been too many commands in too short of a period of time. The API can only handle 100 actions per 100 seconds. 
Please wait at least two minutes and try again"""

Initial_Message = "If any of these values are incorrect, please modify or delete the congifs.json and restart the bot"

Invalid_Input = "Please correct in the configs file (config.json) or delete the file to start the first time set-up again."
=======
help_embed = {
    "title": "**Split Bot Commands**", 
    "desc": 'Please make sure:\nNames match exactly for what you are searching (case sensitive)\nNumbers don\'t have any symbols (no commas or $)\nNates are in the number form MM/DD/YYYY\nItems are comma separated with the proper notation for multiple items (" x2" or " x4" at the end).',
    "n_check": "!check <RSN>",
    "v_check": "Shows stats for the player matching the given RSN.",
    "n_up": "!update <RSN>, <splits>, <items>",
    "v_up": "Adds the split given to the player with the matching RSN. Items are optional but should be added as a comma separated list at the end. Requires the @ADMIN role.",
    "n_add": "!add <RSN>, <splits>, <date>, <items>",
    "v_add": "Creates a new player entry with the given RSN, splits, date, and items. The last three are optional but must be added in that order (so to add a date without adding a split value, use 0. e.g !add Player, 0, 6/12/2019). Requires the @ADMIN role.",
    "footer": "Bot designed by Xaad#1337"
}

API_error = "API Error, either there's been too many inputs in too short of a period or there's been another issue. Please try again in two minutes, if it doesnt work please contact Xaad#1337"
>>>>>>> Stashed changes
