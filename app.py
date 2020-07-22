import json
import logging
from json import JSONDecodeError

from flask.logging import default_handler

from utils import handle_results

root = logging.getLogger()
root.addHandler(default_handler)

from flask import Flask, request
from models import Campaign, client

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
    data = json.loads(request.data)
    demo_campaign = Campaign.retrieve(data['flow_sid'])
    #
    demo_campaign.initiate(data['phone']) if demo_campaign else print("Could not find campaign: " + data['flow_sid'])
    return ''


@app.route("/test_initiate", methods=['POST'])
def test_initiate():
    flow_sid = json.loads(request.data).get('flow_sid')
    logging.log(logging.INFO, "Initiating: " + flow_sid)
    demo_campaign = Campaign.retrieve(flow_sid)

    demo_campaign.initiate()
    return ''


@app.route("/collect/<step>", methods=['GET', 'POST'])
def collect(step):
    app.logger.info("Collecting: " + step)
    try:
        flow_sid = request.values.get('flow_sid')
        execution_sid = request.values.get('execution_sid')
        context = client.studio.v1.flows(flow_sid).executions(execution_sid).execution_context().fetch()
    except JSONDecodeError:
        logging.log(logging.ERROR, "Could not read request data.")
        return '{"success": False}'

    handle_results(context)



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
