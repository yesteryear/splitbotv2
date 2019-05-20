# Redemption Splits Bot
This discord bot automatically pulls and updates information regarding OSRS splits for members of the clan Redemption PMV using their dedicated Google doc. 

---

## Main Discord Commands:

### **!splits (player)**:
Finds the player (by their RSN) and get's their split value. The search for the user is a bit forgiving for spelling errors. 

### **!update (player), (amount), (items)**
This command requires the bot admin rank.
Finds the player and adds the amount specified in <amount>. This can be a negative number if you wish to reduce their split. 
You can also add items or a list of items under <item>. This is entirely optional, and can basically be anything. 
When using this command, make sure the number put in for <amount> is just a raw number with no symbols or commas.
  
> !update Jagex, 500000  
> !update Jagex, 500000, Swords x3, Cabbage x4   

### **!add (player), (split), (date), (items)**
This command requires the bot admin rank.   
This adds the player to the end of the spreadsheet, as well as the specified split value, date, and items.    
Note that the last three are completely optional. If you just wish to add a player to the list, you can just specify their RSN.   

> !add Jagex - This will add the player Jagex with a split value of 0 and today's join date.   
> !add Jagex, 5000000, 1/1/2019 - This will add the player Jagex with a split value of 5,000,000 and join date of Jan 1, 2019.   
> !add Jagex, 5000000, 1/1/2019, Swords x3, Cabbage x4 - Same as above but will also add the items specified at the end.

Splits must follow the number format specified in !update. Dates must be of the form M/D/YYYY (following American date format)
Note that while split, date, and items are optional, if you wish to add any of them they must be added in that order and you can't skip an option. For example, say you wanted to add a player who joined last month, but they dont have any split value, must add the split in the command or it will not work.

> !add Jagex, 1/1/2019 - This is INVALID
> !add Jagex, 0, 1/1/2019 - This is VALID

### **!help**
Posts the commands in chat.

---

# Spreadsheet and Discord Requirements
The bot was designed for a specific spreadsheet format and must meet the following requirements:

1. RNS need to be in Column A  
2. Split Values need to be in Column B  
3. Item Names need to be in Column C  
4. Clan Join Dates need to be in Column D  

Additionally, there should be blank rows below so that additional members can be added. These rows at the very least should have =TODAY() under the clan join date as the bot copies and pastes that when adding a user without a specific join date.   

### Admin Rank:
The bot requires an administrator rank on the server to execute updates of splits and adding new members. Please ensure this rank exists and is given to the correct members

---

# Setting up the bot

### Setting up Google API

1. Navigate to the Google APIs console here: https://console.developers.google.com/?pli=1.  
2. Login and accept terms if needed.  
3. Create a new project (Along the top bar there should be an option for "Select a Project", under select New Project in the top right corner of the new window).  
4. Set project name and continue. May take a few minutes to load.  
5. Under the Dashboard, select Enable APIs and Services.  
6. Select the Google Drive API and hit Enable.  
7. Repeat for Google Sheets API (You can search for it directly in the search bar on the top).  
8. Along the left sidebar, select Credentials.  
9. Along the top of the bar, select the dropdown list under Create Credentials and select Service account key.  
10. On the page to create a new service account key:  
  a. Select "New service account" under Service Account.  
  b. Create a name.  
  c. Under Roles, select Project > Owner or Project > Editor.  
  d. Select JSON as the key type.  
11. A file should be downloaded to your PC. Save this in the same file as the bot file.  
12. Rename the file to be credentials.json (This is important!).  
13. Open the credentials.json in a text editor file and search for "client_email".  
14. Copy the email link following that entry (e.g. "test-name@test-proj-20000.iam.gserviceaccount.com").  
15. On the Google doc with the splits, give access to the sheet to the email from the credentials files (click Share in the top right of the Google doc and ensure they can edit).  
Credentials for the google doc are now set!
 
### Setting up Discord Bot:
1. Navigate to the discord developers page (https://discordapp.com/developers/applications/).  
2. Create a new application.  
3. Select "Bot" on the left sidebar.  
4. Note its token listed under Username and next to Icon. This will needed later.  
5. Return to General Information and copy the Client ID.  
6. Navigate to https://discordapp.com/oauth2/authorize?&client_id=CLIENTID&scope=bot&permissions=8, replacing CLIENTID with the number copied from the previous step.  
7. Add the bot to the correct server (You'll need admin rights in this server to do so).  
The discord bot is now ready, all that is left to connect the bot to the script

### Connecting script to the bot:
1. If you initiate the script without any changes, it will run through a prompt to set up a configs file. It will ask you for the following 4 settings:
  a. Bot Token
  b. Admin Rank
  c. Spreadsheet URL
  d. Worksheet Name
2. Follow the prompts given in the script and it will set itself up and save those settings in a file labled configs.json. 
3. You can also make this file and set the configurations manually. A template for the configs file is available in the repository, just ensure the file is named configs.json.
4. Anytime there is a change to the sheet (such as a different URL or worksheet name, change in bot token or change in admin rank name) the configs file needs to be updated. This can be done manually or you can delete the file and run through the first time set-up again. 
