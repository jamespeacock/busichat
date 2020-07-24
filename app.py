import json
import traceback
from json import JSONDecodeError
from _logger import root

from utils import handle_results

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


@app.route("/initiate", methods=['POST'])
def initiate():
    try:
        data = json.loads(request.data)
        demo_campaign = Campaign.retrieve(data['flow_sid'])
        ids = demo_campaign.initiate(data['phone']) if demo_campaign else print("Could not find campaign: " + data['flow_sid'])
        root.logger.info("started campaign for:" + str(ids))
        return {'ids': ids}
    except Exception:
        root.logger.error(traceback.format_exc())
    return {'error': traceback.format_exc()}


@app.route("/test_initiate", methods=['POST'])
def test_initiate():
    flow_sid = json.loads(request.data).get('flow_sid')
    root.info("Initiating: " + flow_sid)
    demo_campaign = Campaign.retrieve(flow_sid)

    demo_campaign.initiate()
    return ''


@app.route("/collect/<step>", methods=['GET', 'POST'])
def collect(step):
    root.info("Collecting: " + step)
    try:
        flow_sid = request.values.get('flow_sid')
        execution_sid = request.values.get('execution_sid')
        root.info("Fetching context for execution: " + execution_sid)
        context = client.studio.v1.flows(flow_sid).executions(execution_sid).execution_context().fetch()
    except JSONDecodeError:
        root.error("Could not read request data.")
        return '{"success": False}'

    handle_results(context)

    return '{"success": True}'


@app.route("/fallback", methods=['GET', 'POST'])
def fallback():
    """Respond with the number of text messages sent between two parties."""
    root.info.info("Hit Fallback /")
    root.info(request.values)
    return str("")


@app.route("/error", methods=["POST"])
def error():
    root.info("Hit Error endpoint.")
    root.info(request.values)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='80')
