import json

from utils import handle_results

SURVEY_DATA = {
    "recipient": "+15178031167",
    "questions": [
        {
            "name": "census_question",
            "response": "Yes",
        }
    ]
}


def test_parse_flow():
    flow_data = json.load(open('tests/data/flowdata.json'))
    desired_info = handle_results(flow_data)
    assert desired_info == SURVEY_DATA

