import json
import logging
import traceback

import _logger
from collections import defaultdict

import requests
from twilio.rest import Client

from settings import ACCOUNT_SID, AUTH_TOKEN, SERVICE_SID

account_sid = ACCOUNT_SID
auth_token = AUTH_TOKEN
service_sid = SERVICE_SID
twilio_number = "+12162841244"
client = Client(account_sid, auth_token)
auth = (account_sid, auth_token)

# naacp_survey_http = "https://studio.twilio.com/v1/Flows/FW34e1b974dafc860cf1149869a6c04d1f/Executions"
# test_survey_http = "https://studio.twilio.com/v1/Flows/FW145b255594b997cb7d4ae5c8746fa176/Executions"

# numbers = ['+17138656269', '+15178031167']

CONTEXT = "context"
WIDGETS = "widgets"
CONTACT = "contact"
CHANNEL = "channel"
ADDRESS = "address"
FLOW_SID = "flow_sid"
EID = "execution_sid"
IN = "inbound"
OUT = "outbound"
FROM = "From"
BODY = "Body"


def ensure_formatted(numbers):
    for n in numbers:
        yield n  # ensure +1[0-9]+ & len(n) == 12


def initiate_workflow(numbers, trigger, info=defaultdict(dict)):

    eids = {}
    for number in ensure_formatted(numbers):

        body = {
            "To": number,
            "From": twilio_number,
            **(info[number] if info else {})
        }

        # initiate text conversation in twilio studio
        resp = requests.post(trigger, auth=auth, data=body)

        if resp.status_code != 200:
            logging.log(logging.ERROR, resp.text)
            eids[number] = None
        else:
            try:
                sid = json.loads(resp.text)["sid"]
                eids[number] = sid
            except:
                logging.log(logging.ERROR, traceback.format_exc())
                eids[number] = None

    return eids


def lookup_trigger(t):
    if t == "TEST":
        return "https://studio.twilio.com/v1/Flows/FWc465bf80ff444a3579c01b4d4764a5a2/Executions"
    return ""


def lookup_template(test):
    if test == "TEST":
        return {
            "qs": [
                "zipcode_question"
            ]
        }


def handle_results(flow_data, test, template=None):

    template = template or lookup_template(test)

    QS = "qs"

    questions = flow_data[CONTEXT][WIDGETS]
    res = {
        "recipient": flow_data[CONTEXT][CONTACT][CHANNEL][ADDRESS],
        FLOW_SID: flow_data[FLOW_SID],
        EID: flow_data[EID],
        "questions": []
    }
    for q in template[QS]:
        q_data = questions[q] if q in questions else None
        if not q_data:
            continue

        res["questions"].append({
            "name": q,
            "response": q_data[IN][BODY]
        })

    return res

