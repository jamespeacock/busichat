import datetime
import json
import logging
import traceback
from json import JSONDecodeError
import requests
import datetime
import re
from collections import defaultdict

import gspread
from fuzzywuzzy import process
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client
from settings import ACCOUNT_SID, AUTH_TOKEN, SERVICE_SID

account_sid = ACCOUNT_SID
auth_token = AUTH_TOKEN
service_sid = SERVICE_SID
client = Client(account_sid, auth_token)
auth = (account_sid, auth_token)


# SHEET COLUMN NAMES
ACTION = "ACTION"
FNAME = "First Name"
LNAME = "Last Name"
PHONE = "phone"
CAMPAIGN = "campaign"
ZIPCODE = "Zipcode"
INIT = "initiated"
COMP = "completed"
EID = "execution_sid"
FLOW_SID = "flow_sid"


def ensure_formatted(numbers):
    re.compile(".*?(\(?\d{3})? ?[\.-]? ?\d{3} ?[\.-]? ?\d{4}).*?", re.S)
    for n in numbers:

        yield n  # ensure +1[0-9]+ & len(n) == 12 //"\+1[0-9]{10}"


class AnswerRecord:

    def __init__(self, row, questions={}, initiating=True):
        self.phone = row.get(PHONE, '')
        self.campaign = row.get(CAMPAIGN, '')
        if initiating:
            self.initiated = row.get('initiated', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            self.completed = row.get('completed', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.execution_sid = row.get(EID)
        self.flow_sid = row[FLOW_SID]
        self.questions = questions

    def update(self, other):
        for q, v in self.questions:
            if not v:
                self.questions[q] = other.questions[q]

        self.completed = other.completed

    def to_row(self):
        row = {
            PHONE: self.phone,
            CAMPAIGN: self.campaign,
            INIT: self.initiated,
            COMP: self.completed or "",
            EID: self.execution_sid,
            FLOW_SID: self.flow_sid,
            **self.questions
        }
        return row


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

    def phone_exists(self, num):
        return True if self.sheet.find(num, in_column=self._col(PHONE)) else False

    def get_columns(self, names, cells):
        matches = [process.extract(n, self.cols, limit=1)[0][0] for n in names]
        return [(p[c] for c in matches) for p in cells]

    def values(self, name, rows=None):
        cname = process.extract(name, self.cols, limit=1)[0][0]
        vals = self.sheet.col_values(self._col(cname))
        return [vals[r-1] for r in rows] if rows else vals

    def _col(self, i):
        return self.cols.index(i)+1

    def create(self, info):
        vals = [*info.values()]
        self.sheet.append_row(vals)

    def findall(self, search, col):
        if col:
            cells = self.sheet.findall(search, in_column=self._col(col))
        else:
            cells = self.sheet.findall(search)
        return [self.sheet.row_values(cell.row) for cell in cells]

    def index(self, search, col):
        return self.sheet.findall(search, in_column=self._col(col))


class Campaign:

    def __init__(self, sheet_name, flow_sid, flow_number, questions=[], action_value=""):
        self.contacts = MySheet(sheet_name)
        self.responses = MySheet(sheet_name, 1)
        self.links = MySheet(sheet_name, 2)
        self.scores = MySheet(sheet_name, 3)
        self.flow_sid = flow_sid
        self.flow_url = self.get_flow_url(flow_sid)
        self._from = flow_number
        self.questions = questions
        self.action = action_value

    @staticmethod
    def retrieve(flow_sid="", action_val=""):
        cmpgns = MySheet("CAMPAIGNS")
        results = cmpgns.findall(flow_sid, FLOW_SID) if flow_sid else cmpgns.findall(action_val, ACTION)
        if not results:
            return None
        result = results[0]
        sheet_name = result["campaign_sheet"]
        flow_number = result["flow_number"]
        questions = result["questions"].split(",")
        action_value = result["action_value"]
        return Campaign(sheet_name, flow_sid, flow_number, questions, action_value)

    def get_flow_url(self, flow_sid):
        return "https://studio.twilio.com/v1/Flows/{flow_sid}/Executions".format(flow_sid=flow_sid)

    def initiate(self):

        #Shared info for campaign launch
        row = {
            "campaign": self.action,
            "flow_sid": self.flow_sid
        }

        ids = self.scan_for_action()

        for n in ids:
            row["eid"] = ids[n]["eid"]
            row['phone'] = n
            # save initiated response
            self.save_response(row)
        return ids

    def save_response(self, row):
        self.responses.create(AnswerRecord(row).to_row())

    def scan_for_action(self):
        act_col = process.extract(ACTION, self.contacts.cols, limit=1)[0][0]

        matches = self.contacts.findall(self.action, act_col)
        if matches:
            rows = [m.row for m in matches]
            numbers = self.contacts.values(PHONE, rows)
            ids = self.initiate_workflow(numbers)

            return ids

    def results(self):
        return self.responses.sheet.get_all_values()

    def update_record(self, record, phone, campaign):
        
        matches = set([c.row for c in self.responses.index(phone, PHONE)])
        matches.intersection(set([c.row for c in self.responses.index(campaign, CAMPAIGN)]))
        row = matches[0] if matches else None
        existing = AnswerRecord(self.responses.sheet.row_values(row))
        existing.update(record)
        self.responses.sheet.insert_row(row, existing.to_row())

    def initiate_workflow(self, numbers, info=defaultdict(dict)):

        ids = {}
        for number in ensure_formatted(numbers):

            body = {
                "To": number,
                "From": self._from,
                **(info[number] if info else {})
            }

            # initiate text conversation in twilio studio
            resp = requests.post(self.flow_url, auth=auth, data=body)

            if resp.status_code != 200:
                logging.log(logging.ERROR, resp.text)
                ids[number] = None
            else:
                try:
                    req_data = json.loads(resp.text)
                    ex_sid = req_data["sid"]
                    ids[number]["eid"] = ex_sid
                except JSONDecodeError:
                    logging.log(logging.ERROR, traceback.format_exc())
                    ids[number] = None

        return ids
