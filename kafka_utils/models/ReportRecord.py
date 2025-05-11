# Imports - Standard
import json
from datetime import datetime

# Imports - Third-party
from pydantic import BaseModel, Field

# Imports - Local
from . import (
    MSG_KEY_MODEL_NAME_CAMEL,
    MSG_KEY_MODEL_NAME,
    MSG_KEY_REPORT,
    MSG_KEY_TIMESTAMP,
    MSG_TIMESTAMP_FORMAT,
    MSG_KEY_PAYLOAD,
    MSG_KEY_TOKEN,
    MSG_KEY_STATUS,
    MSG_KEY_TASK_START_TIME,
    MSG_KEY_TASK_START_TIME_CAMEL,
    MSG_KEY_TASK_END_TIME,
    MSG_KEY_TASK_END_TIME_CAMEL,
    ENCODING_UTF8,
)

# Constants
MSG_KEY_REPORTS = 'reports'

# lambda function
json_deserializer = lambda x: json.loads(x.decode(ENCODING_UTF8))


class Report(BaseModel):
#    model_name: str = Field(
#        alias=MSG_KEY_MODEL_NAME_CAMEL,
#        description='The name of the model that generated the report.',
#    )

    payload: dict = Field(
        description='The payload of the report.',
    )

    def __init__(self, **kwargs):
        # Check if model_name is required
#        if MSG_KEY_MODEL_NAME_CAMEL not in kwargs and MSG_KEY_MODEL_NAME not in kwargs:
#            raise ValueError('`model_name` is required')
#        elif MSG_KEY_MODEL_NAME in kwargs:
#            kwargs[MSG_KEY_MODEL_NAME_CAMEL] = kwargs[MSG_KEY_MODEL_NAME]

        # Check if report is required
        if MSG_KEY_REPORT in kwargs:
            payload = kwargs[MSG_KEY_REPORT]
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    # If it's not a JSON string, wrap it in a dict with 'value' key
                    payload = dict(value=payload)

            kwargs[MSG_KEY_PAYLOAD] = payload
        else:
            raise ValueError('`report` is required')

        # Initialize the model
        super().__init__(**kwargs)

    @property
    def timestamp_str(self) -> str:
        return self.payload[MSG_KEY_TIMESTAMP].isoformat(timespec='milliseconds') + 'Z'

    @property
    def timestamp(self) -> datetime:
        if self.payload is not None and MSG_KEY_TIMESTAMP in self.payload:
            return datetime.strptime(self.payload[MSG_KEY_TIMESTAMP], MSG_TIMESTAMP_FORMAT)
        else:
            old_timestamp = '1970-01-01T00:00:00.000Z'
            return datetime.strptime(old_timestamp, MSG_TIMESTAMP_FORMAT)


class ReportRecord(BaseModel):
    token: str = Field(
        description='Token for the request.',
    )

    model_name: str = Field(
        alias=MSG_KEY_MODEL_NAME_CAMEL,
        description='The name of the model that generated the report.',
    )

    status: bool = Field(
        description='Task success / fail'
    )

    task_start_time: str = Field(
        alias=MSG_KEY_TASK_START_TIME_CAMEL,
        description='ISO format timestamp when model started the task.'
    )

    task_end_time: str = Field(
        alias=MSG_KEY_TASK_END_TIME_CAMEL,
        description='ISO format timestamp when model finished the task.'
    )

    #reports: dict[int, Report]
    reports: dict[str, str]

    def __init__(self, **kwargs):
        if MSG_KEY_MODEL_NAME_CAMEL not in kwargs and MSG_KEY_MODEL_NAME not in kwargs:
            raise ValueError('`model_name` is required')
        elif MSG_KEY_MODEL_NAME in kwargs:
            kwargs[MSG_KEY_MODEL_NAME_CAMEL] = kwargs[MSG_KEY_MODEL_NAME]

        if MSG_KEY_TASK_START_TIME in kwargs:
            kwargs[MSG_KEY_TASK_START_TIME_CAMEL] = kwargs[MSG_KEY_TASK_START_TIME]
        if MSG_KEY_TASK_END_TIME in kwargs:
            kwargs[MSG_KEY_TASK_END_TIME_CAMEL] = kwargs[MSG_KEY_TASK_END_TIME]

        #kwargs[MSG_KEY_REPORTS] = self.load_reports(kwargs[MSG_KEY_REPORTS])
        super().__init__(**kwargs)

    def load_reports(self, reports: list[dict]) -> dict[int, Report]:
        reports_dict = {
            report_idx: Report(**report)
            for report_idx, report in enumerate(reports, 1)
        }

        # Sort reports by report.timestamp
        has_timestamp_in_any_report = any(
            MSG_KEY_REPORT in report and MSG_KEY_TIMESTAMP in report[MSG_KEY_REPORT]
            for report in reports)
        if has_timestamp_in_any_report:
            reports_dict = {
                report_idx: report
                for report_idx, report in enumerate(
                    sorted(reports_dict.values(), key=lambda x: x.timestamp, reverse=True),
                    1)
            }

        return reports_dict

    def jsonify(self) -> str:
        msg = {
            MSG_KEY_TOKEN: self.token,
            MSG_KEY_MODEL_NAME_CAMEL: self.model_name,
            MSG_KEY_STATUS: self.status,
            MSG_KEY_TASK_START_TIME_CAMEL: self.task_start_time,
            MSG_KEY_TASK_END_TIME_CAMEL: self.task_end_time,
            MSG_KEY_REPORTS: json.dumps(self.reports)
        }
        return json.dumps(msg)


if __name__ == '__main__':
    # serde test
    message = ReportRecord(
        token='test-token',
        model_name='test-model',
        status=True,
        task_start_time='2025-04-01T12:00:00.000Z',
        task_end_time='2025-04-01T12:00:10.000Z',
        reports={
            'payload': "test-payload"
        }
    )
    print(f'{message.jsonify()!r}')

