from oauth2client.service_account import ServiceAccountCredentials
import gspread
import re


class DocScanner:
    """DocScanner is used to pull and push updates to the required doc
    
    Parameters:
    ss_URL: str - URL of the google sheet to access
    ws_name: str - Name of the worksheet (or tab) on the google sheet

    Methods:
    --------
    connect_to_API():
        Connects to the google sheet. Decorator set up to reconnect
        if connection was lost

    get_all_splits():
        Grabs full list of all splits as a dictionary in the form:
        name = (row_number, splits_value, items, days, rank)

    get_split(name: str):
        Returns the splits value for the specific user (exact match)

    update_split(name: str, delta: int, items: str):
        Adds value of delta to user (name)'s splits. Also appends item list
        based on provided string

    format_items(items: str):
        Formats a list of items into the required format
        1. Comma separated
        2. Single items listed as is
        3. Duplicate items combit with name, splits, date, and itemsned and denoted with (x#)
        e.g.: Sword of the Cliche, Thanoscopter Blade x3

    add_user(name: str, splits: int, date: str, items: str):
        Adds user to spreadshee
        Later 3 parameters are optional

    """

    class Decor:
        def reconnect(func):
            def wrapper(self, *args, **kwargs):
                try:
                    return func(self, *args, **kwargs)
                except gspread.exceptions.APIError:
                    print("API Error, attempting reconnect")
                    self.connect_to_API()
                    return func(self, *args, **kwargs)
            return wrapper

    def __init__(self, ss_URL: str, ws_name: str):
        """Initiates DocScanner class
        
        Parameters:
        -----------
        ss_url: str
            URL of the google doc
        ws_name: str
            Exact name of the specific worksheet within the google doc
        """
        self.ss_URL = ss_URL
        self.ws_name = ws_name
        # Grabs credentials and API information, connects to API
        self.scope = [
            'https://spreadsheets.google.com/feeds', 
            'https://www.googleapis.com/auth/drive'
        ]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            'credentials.json', 
            self.scope
        )
        self.connect_to_API()

    def connect_to_API(self):
        """Opens the document and assigns worksheet to instance variable"""
        gc = gspread.authorize(self.creds)
        self.sheet = gc.open_by_url(self.ss_URL).worksheet(self.ws_name)

    @Decor.reconnect
    def get_all_splits(self):
        """Gets all characters and split values from spreadsheet"""
        # Grabs all values from sheet
        all_vals = self.sheet.get_all_values()       

        # Creates dictionary with a tuple of values
        # [name] = (Row Index, Split Value, Items, Date, Rank)
        # If split cannot be made proper integer, returns None for ammount
        values = {}
        for i in range(len(all_vals)):
            col = all_vals[i]
            name = col[0]
            split = col[1]
            items = col[2]
            days = col[6]
            rank = col[4]
            if name:
                try:
                    amount = int(split.replace(",", "").replace("$", ""))
                except (ValueError, IndexError):
                    amount = None
                if amount is not None:
                    values[name] = (i + 1, amount, items, days, rank)
        return values

    @Decor.reconnect
    def get_split(self, name):
        """Gets individual user split amount from sheet"""
        # Generates list and sends back all values 
        splits_list = self.get_all_splits()
        if name in splits_list:
            return splits_list[name]

    @Decor.reconnect
    def update_split(self, name, delta, items=None):
        """Adds value of delta to name's split"""
        # Generates list
        splits_list = self.get_all_splits()

        if name not in splits_list:
            return None
        splits_vals = splits_list[name]

        # If index is valid, adds provided value to splits
        prev_val = splits_vals[1]
        new_val = prev_val + delta
        self.sheet.update_cell(splits_vals[0], 2, new_val)

        # If item provided, appends item to end of item list
        old_items = new_items = None
        if items is not None:
            old_items = splits_vals[2]

            if old_items:
                new_item_list = old_items + ", " + items
                new_items = self.format_items(new_item_list)  # Format list
            else: 
                new_items = self.format_items(items)
            self.sheet.update_cell(splits_vals[0], 3, new_items)

        # Returns both previous and new value
        return prev_val, new_val, old_items, new_items

    def format_items(self, items):
        """Formats item list correctly. 
        Single items are listed as is (e.g. Sword of the Cliche)
        Duplicate items are added and noted (e.g. Sword of the Cliche x4)
        """

        def proper_case(string):
            # Properly format item name
            words = string.split(' ')
            exceptions = ['a', 'an', 'of', 'the', 'is']
            formatted = [words[0].title()]

            for word in words[1:]:
                appender = word.title() if word not in exceptions else word
                formatted.append(appender)
            return " ".join(formatted)

        # Collect list and count of all items
        all_items = items.split(',')
        item_count = {}

        # Count the number of items and format the name correctly
        for item in all_items:
            item = item.strip().lower()
            count_mark = re.search(r" x[0-9]+$", item)

            # Determines if item currently as "x[0-9]+ and counts appropriately"
            if count_mark: 
                count_mark_S = count_mark.group()
                item = proper_case(item.replace(count_mark_S, ""))
                count_S = re.search(r"[0-9]+", count_mark_S)
                count = int(count_S.group())
            else:
                item = proper_case(item)
                count = 1
            
            if item in item_count:
                item_count[item] += count
            else:
                item_count[item] = count
        
        # Creates list with proper form
        final_out = []
        for item, count in item_count.items():
            # Adds formatting
            final = item if count == 1 else f'{item} x{str(count)}'
            final_out.append(final)
        
        # Joins together as comma separated list
        return ', '.join(final_out)

    @Decor.reconnect
    def add_user(self, name, splits=0, date=None, items=''):
        """Adds user with optional splits, date, and items list"""

        # Confirm if user exists, breaks if it does
        splits_list = self.get_all_splits()
        if name in splits_list:
            return

        # If user does not exist, add to bottom with split

        # Gets row for the end of the list
        col_list = self.sheet.col_values(1)
        row = len(col_list) + 1

        # Updates names, splits and items based on provided values
        self.sheet.update_cell(row, 1, name)
        self.sheet.update_cell(row, 2, splits)
        formatted_items = self.format_items(items)
        self.sheet.update_cell(row, 3, formatted_items)

        # If date is not provided, uses the existing cell value TODAY()
        # Replaces the function in the cell with the value
        if date is None:
            date = self.sheet.cell(row, 4).value
        self.sheet.update_cell(row, 4, date)

        # Confirms user was added
        return self.get_split(name)



# The error code is gspread.exceptions.APIError
if __name__ == "__main__":
    test = DocScanner("https://docs.google.com/spreadsheets/d/1Py0pico9VWu0Nno0nuVFl6kBwZrkmxM8rqlSMWtuGbo/edit#gid=176933786", "test")


