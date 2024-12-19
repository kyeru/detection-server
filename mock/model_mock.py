import json
import time


def run_model(request_message):
    if isinstance(request_message, dict):
        pass
    elif isinstance(request_message, str):
        try:
            request_message = json.loads(request_message)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid request message type: {type(request_message)}")
    else:
        raise ValueError(f"Invalid request message type: {type(request_message)}")
    
    token = request_message.get('token', 'unsafe_token')
    report_template = '''
    {
        "modelName": "mock",
        "token": "%s",
        "report": "report"
    }
    '''
    time.sleep(3)
    return report_template % token
