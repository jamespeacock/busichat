from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse

# The session object makes use of a secret key.
SECRET_KEY = 'oJpcTZ1JLCGTbXlmxWpAjB1tljbKQLJW'
app = Flask(__name__)
app.config.from_object(__name__)

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
    print("Hit route /")
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
    print(request)
    print(request.values)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='80')
