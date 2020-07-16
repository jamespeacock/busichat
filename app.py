import json
import logging
from json import JSONDecodeError

from flask.logging import default_handler

from utils import handle_results, extract_answers

root = logging.getLogger()
root.addHandler(default_handler)

from flask import Flask, request
from models import Campaign


SECRET_KEY = 'oJpcTZ1JLCGTbXlmxWpAjB1tljbKQLJW'


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('SETTINGS')

IS_REGISTERED = "IS_REGISTERED"
CONFIRM_REGISTERED = "CONFIRM_REGISTERED"
DID_CENSUS = "DID_CENSUS"
CONFIRMED_CENSUS = "CONFIRMED_CENSUS"
SHARED_PLEDGE = "SHARED_PLEDGE"


STATES = [
    IS_REGISTERED,
    CONFIRM_REGISTERED,
    DID_CENSUS,
    CONFIRMED_CENSUS,
    SHARED_PLEDGE
]


@app.route("/status", methods=['GET', 'POST'])
def status():
    logging.log(logging.INFO, "Status")
    logging.log(logging.INFO, request)


@app.route("/initiate", methods=['POST'])
def initiate():
    flow_sid = request.values.get('flow_sid')
    logging.log(logging.INFO, "Initiating: " + flow_sid)
    demo_campaign = Campaign.retrieve(flow_sid)

    demo_campaign.initiate()

@app.route("/collect/<step>", methods=['GET', 'POST'])
def collect(step):
    app.logger.info(step)
    logging.log(logging.INFO, request)
    # logging.log(logging.INFO, request.values)
    # Take responses from Twilio Studio & save directly
    # TODO extract YES/NO census info / Zipcode info /
    try:
        data = json.loads(request.data)
    except JSONDecodeError:
        logging.log(logging.ERROR, "Could not read request data.")
        return '{"success": False}'

    res = extract_answers(data["widgets"])
    handle_results(res, )

    #Lookup MySheet by Flow ID
    # dbo.get_sheet(data['FLOW_SID'])
    #Lookup row in MySheet by ExecutionID
    res["execution_id"] = data["execution_id"]
    #Insert into cell by column==question & row=eid_match



    return '{"success": True}'



@app.route("/fallback", methods=['GET', 'POST'])
def fallback():
    """Respond with the number of text messages sent between two parties."""
    app.logger.info("Hit Fallback /")
    logging.log(logging.INFO, request)
    return str("")


@app.route("/error", methods=["POST"])
def error():
    logging.log(logging.INFO, request)



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='80')
