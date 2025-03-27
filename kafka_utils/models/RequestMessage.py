# Imports - Standard
import json
from datetime import datetime

# Imports - Third-party
from pydantic import BaseModel, Field

# Imports - Local
from . import (
    MSG_KEY_TIMESTAMP, MSG_KEY_USER, MSG_KEY_DATA,
    MSG_KEY_MODEL_NAME_CAMEL, MSG_KEY_VALUE)


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
            MSG_KEY_USER: self.user,
            MSG_KEY_DATA: json.dumps(self.data)
        }
        return json.dumps(msg)


if __name__ == '__main__':
    model_name = 'SELab.Fixer'
    message = RequestMessage(
        model_name=model_name,
        value={
            'waiting': 10,
            'data': 'Hello, from SELab producer for `request` topic! for `selab.fixer` model'
        }
    )
    print(f'{message.jsonify()!r}')
