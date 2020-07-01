import logging
from collections import defaultdict

import requests
from twilio.rest import Client

from settings import ACCOUNT_SID, AUTH_TOKEN, SERVICE_SID

account_sid = ACCOUNT_SID
auth_token = AUTH_TOKEN
service_sid = SERVICE_SID
naacp_number = "+12162841244"
client = Client(account_sid, auth_token)
auth = (account_sid, auth_token)

# naacp_survey_http = "https://studio.twilio.com/v1/Flows/FW34e1b974dafc860cf1149869a6c04d1f/Executions"
# test_survey_http = "https://studio.twilio.com/v1/Flows/FW145b255594b997cb7d4ae5c8746fa176/Executions"

# numbers = ['+17138656269', '+15178031167']


def ensure_formatted(numbers):
    for n in numbers:
        yield n  # ensure +1[0-9]+ & len(n) == 12


def initiate_workflow(numbers, trigger, info=defaultdict(dict)):

    success, erred = [], []
    for number in ensure_formatted(numbers):

        body = {
            "To": number,
            "From": naacp_number,
            **(info[number])
        }

        # initiate text conversation in twilio studio
        resp = requests.post(trigger, auth=auth, data=body)

        if resp.status_code != 200:
            logging.log(logging.ERROR, resp.text)
            erred.append(number)
        else:
            success.append(number)

    return success, erred


def lookup_trigger(t):
    if t == "TEST":
        return "https://studio.twilio.com/v1/Flows/TEST"
    return ""