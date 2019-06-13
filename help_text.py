# This only exists so my main file doesnt have this massive blob of text in the middle

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