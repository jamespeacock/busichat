

from models import CAMPAIGN, PHONE, Campaign, EID, FLOW_SID, AnswerRecord

CONTEXT = "context"
WIDGETS = "widgets"
CONTACT = "contact"
CHANNEL = "channel"
ADDRESS = "address"
FLOW = "flow"
DATA = "data"
IN = "inbound"
OUT = "outbound"
FROM = "From"
BODY = "Body"


def lookup_template(test):
    if test == "TEST":
        return {
            "qs": [
                "completed_census",
                "completed_registration"
            ]
        }


def extract_answers(data):
    return data


# This could be utilized to fetch raw execution data from the api
def handle_results(flow_data):

    res = {
        PHONE: flow_data[CONTEXT][CONTACT][CHANNEL][ADDRESS],
        FLOW_SID: flow_data[FLOW_SID],
        EID: flow_data[EID],
        CAMPAIGN: flow_data[CONTEXT][FLOW][DATA]
    }
    completed_record = AnswerRecord(res, initiating=False)
    campaign = Campaign.retrieve(flow_sid=completed_record.flow_sid)
    if not campaign:
        return {"error": "Could not find campaign for this flow_sid."}

    flow_responses = flow_data[CONTEXT][WIDGETS]

    for q in campaign.questions:
        q_data = flow_responses[q] if q in flow_responses else None
        if not q_data:
            continue

        completed_record.questions[q] = q_data[IN][BODY]

    campaign.update_record(completed_record)

    return True



