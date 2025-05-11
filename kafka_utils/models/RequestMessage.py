# Imports - Standard
import json
from datetime import datetime

# Imports - Third-party
from pydantic import BaseModel, Field

# Imports - Local
from . import (
    MSG_KEY_TIMESTAMP,
    MSG_KEY_TOKEN,
    MSG_KEY_USER,
    MSG_KEY_MODEL_NAME_CAMEL,
    MSG_KEY_DATA,
    MSG_KEY_VALUE
)


class RequestMessage(BaseModel):
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(timespec='milliseconds') + 'Z',
        description='The timestamp of the request message created'
    )

    token: str = Field(
        description='Unique token generated for reqeuest'
    )

    user: str = Field(
        default='SELab.Tester',
        description='The user who requested the model'
    )

    model_name: str = Field(
        alias=MSG_KEY_MODEL_NAME_CAMEL,
        description='The name of the model to request'
    )

    value: dict = Field(
        description='The payload to request'
    )

    def __init__(self, **kwargs):
        if 'model_name' in kwargs:
            kwargs[MSG_KEY_MODEL_NAME_CAMEL] = kwargs.pop('model_name')
        super().__init__(**kwargs)

    @property
    def data(self) -> dict:
        return {
                MSG_KEY_MODEL_NAME_CAMEL: self.model_name,
                MSG_KEY_VALUE: json.dumps(self.value)
            }

    def jsonify(self) -> str:
        msg = {
            MSG_KEY_TIMESTAMP: self.timestamp,
            MSG_KEY_TOKEN: self.token,
            MSG_KEY_USER: self.user,
            MSG_KEY_MODEL_NAME_CAMEL: self.model_name,
            MSG_KEY_VALUE: json.dumps(self.value)
        }
        return json.dumps(msg)


def parse_from_json(request_message):
    if isinstance(request_message, dict):
        pass
    elif isinstance(request_message, str):
        try:
            request_message = json.loads(request_message)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid request message type: {type(request_message)}")
    else:
        raise ValueError(f"Invalid request message type: {type(request_message)}")

    return RequestMessage(
        timestamp = request_message[MSG_KEY_TIMESTAMP],
        token = str(request_message[MSG_KEY_TOKEN]),
        user = str(request_message[MSG_KEY_USER]),
        #model_name = str(request_message[MSG_KEY_MODEL_NAME_CAMEL]),
        model_name = 'model',
        #value = str(json.loads(request_message[MSG_KEY_VALUE]))
        value = {}
    )


if __name__ == '__main__':
    # serde test
    message = RequestMessage(
        timestamp='2025-01-01T00:00:00.000Z',
        token='test-token',
        user='test-user',
        model_name='SELab.Fixer',
        value={
            'waiting': 10,
            'data': 'Hello, from SELab producer for `request` topic! for `selab.fixer` model'
        }
    )
    print(f'{message.jsonify()!r}')

