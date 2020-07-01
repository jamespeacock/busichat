import logging
from settings import ACCOUNT_SID

from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse

# The session object makes use of a secret key.
SECRET_KEY = 'oJpcTZ1JLCGTbXlmxWpAjB1tljbKQLJW'
app = Flask(__name__)
# app.config.from_object(__name__)
# app.config.from_envvar('SETTINGS')
print(ACCOUNT_SID)

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

# Try adding your own number to this list!
callers = {
    "+7138656269": {"name": "Rey",
                    "census": True,
                    "registered": False,
                    "pledged": False,
                    "sent": "is_registered"
                    }
}


@app.route("/", methods=['GET', 'POST'])
def hello():
    """Respond with the number of text messages sent between two parties."""
    logging.log(logging.INFO, "Hit route /")
    # Increment the counter
    counter = session.get('counter', 0)
    counter += 1

    # Save the new counter value in the session
    session['counter'] = counter

    from_number = request.values.get('From')
    if from_number in callers:
        name = callers[from_number]
    else:
        name = "Friend"

    # Build our reply
    message = '{} has messaged {} {} times.' \
        .format(name, request.values.get('To'), counter)

    # Put it in a TwiML response
    resp = MessagingResponse()
    resp.message(message)

    return str(resp)


@app.route("/status", methods=['GET', 'POST'])
def status():
    logging.log(logging.INFO, "Status")
    logging.log(logging.INFO, request)
    # logging.log(logging.INFO, request.values)


@app.route("/collect", methods=['GET', 'POST'])
def collect():
    logging.log(logging.INFO, "Status")
    logging.log(logging.INFO, request)
    # logging.log(logging.INFO, request.values)



    return str("")


@app.route("/event/pre", methods=['GET', 'POST'])
def pre():
    """Respond with the number of text messages sent between two parties."""
    logging.log(logging.INFO, "Hit PRE EVENT /")
    logging.log(logging.INFO, request)
    # Increment the counter


@app.route("/event/post", methods=['GET', 'POST'])
def post():
    """Respond with the number of text messages sent between two parties."""
    logging.log(logging.INFO, "Hit PRE EVENT /")
    logging.log(logging.INFO, request)
    # Increment the counter


@app.route("/fallback", methods=['GET', 'POST'])
def fallback():
    """Respond with the number of text messages sent between two parties."""
    logging.log(logging.INFO, "Hit Fallback /")
    logging.log(logging.INFO, request)
    return str("")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='80')
