
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


# This could be utilized to fetch raw execution data from the api
def handle_results(flow_data):
    res = {
        PHONE: flow_data.context[CONTACT][CHANNEL][ADDRESS],
        FLOW_SID: flow_data.flow_sid,
        EID: flow_data.execution_sid,
        CAMPAIGN: flow_data.context[FLOW][DATA][CAMPAIGN]
    }
    completed_record = AnswerRecord(res, initiating=False)
    campaign = Campaign.retrieve(flow_sid=completed_record.flow_sid)
    if not campaign:
        return {"error": "Could not find campaign for this flow_sid."}

    flow_responses = flow_data.context['widgets']

    for q in campaign.questions:
        q_data = flow_responses[q] if q in flow_responses else None
        if not q_data:
            continue
        completed_record.questions[q] = q_data[IN][BODY]

    campaign.update_record(completed_record)

    return True



