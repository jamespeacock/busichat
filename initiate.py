import gspread
from fuzzywuzzy import process
from gspread import Worksheet
from oauth2client.service_account import ServiceAccountCredentials

# SHEET COLUMN NAMES
from utils import initiate_workflow, lookup_trigger

ACTION = "ACTION"
FNAME = "First Name"
LNAME = "Last Name"
PHONE = "Contact Phone Number"
ZIPCODE = "Zipcode"


class MySheet:

    def __init__(self, name, sheet=0):
        # use creds to create a client to interact with the Google Drive API
        # scope = ['https://spreadsheets.google.com']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json')
        client = gspread.authorize(creds)
        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        # all_sheets = client.list_spreadsheet_files()
        # print(all_sheets)
        self.sheet = client.open(name).get_worksheet(sheet)

        # Extract and print all of the values
        # data = self.sheet.get_all_records()
        # print(list(data[:5]))

        self.cols = list(self.sheet.row_values(1))

    def get_columns(self, names, cells):
        matches = [process.extract(n, self.cols, limit=1)[0][0] for n in names]
        return [(p[c] for c in matches) for p in cells]

    def values(self, name, rows=None):
        cname = process.extract(name, self.cols, limit=1)[0][0]
        vals = self.sheet.col_values(self._col(cname))
        return [vals[r-1] for r in rows] if rows else vals

    def scan_for_action(self, action: str):
        act_col = process.extract(ACTION, self.cols, limit=1)[0][0]

        matches = self.sheet.findall(action, in_column=self._col(act_col))
        if matches:
            rows = [m.row for m in matches]
            act_val = matches[0].value
            numbers = self.values(PHONE, rows) # make columns element of this class
            info = {}
            for n in numbers:
                info[n] = {"a": "b"}
            initiate_workflow(numbers, lookup_trigger(act_val), info)

    def _col(self, i):
        return self.cols.index(i)+1


sheet1 = MySheet('Editable Contact Status')
sheet1.scan_for_action("TEST")
