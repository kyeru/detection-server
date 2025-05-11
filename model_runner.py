# Imports - Standard
from functools import partial
import datetime
import json
import logging

# Imports - Third-party
from kafka_utils import kafka_pub, kafka_sub
from kafka_utils.models import RequestMessage
# Imports - Local
from mocks import model_mock


logger = logging.getLogger(__name__)
task_status = 'WAITING'


def get_report_func(config):
    if config.report_type.lower() == 'file':
        logger.info(f'will write report to file {config.report_file_path}')
        output_file = open(config.report_file_path, 'w')
        return lambda report: \
            output_file.writelines([ report + '\n' ])
    else:    # config.report_type.lower() == 'kafka':
        logger.info(f'will write report to kafka topic {config.report_topic}')
        producer_config = kafka_pub.KafkaProducerConfig(
            bootstrap_servers=config.report_bootstrap_servers,
            value_type=config.report_value_type
        )
        producer = kafka_pub.get_producer(producer_config)
        key = config.name
        return lambda report: \
            kafka_pub.produce(producer, config.report_topic, key, report)


# 파일 내용으로 모델을 실행하고 결과를 반환
def run_loop_file_input(config):
    mode_name = config.name
    report_func = get_report_func(config)

    with open(config.request_file_path, 'r') as input_file:
        for message in input_file:
            global task_status
            task_status = 'RUNNING'
            try:
                report = run_model(model_name, json.loads(message))
                report_func(report)
            except Exception as e:
                logger.warn(f'exception occurred while model runs: {e}')
            task_status = 'WAITING'


# kafka 메시지로 모델을 실행하고 결과를 반환
def run_loop_kafka_input(config):
    consumer_config = kafka_sub.KafkaConsumerConfig(
        bootstrap_servers=config.request_bootstrap_servers,
        topic=config.request_topic,
        auto_offset_reset='latest',
        group_id='model-' + config.name,
        value_type=config.request_value_type
    )
    consumer = kafka_sub.get_consumer(consumer_config)

    model_name = config.name
    report_func = get_report_func(config)

    for message in consumer:
        global task_status
        task_status = 'RUNNING'
        try:
            consumer.commit()
            report = run_model(model_name, message.value)
            report_func(report)
        except Exception as e:
            logger.warn(f'exception occurred while model runs: {e}')
        task_status = 'WAITING'


def run(config):
    if config.request_type.lower() == 'file':
        logger.info(f'running with input from file {config.request_file_path}')
        run_loop_file_input(config)
    else:    # config.request_type.lower() == 'kafka'
        logger.info(f'running with input from kafka topic {config.request_topic}')
        run_loop_kafka_input(config)


# 모델 실행 후 결과 반환
# request_message는 json string이 아니라 dict object여야 함
def run_model(model_name, request_message_json):
    logger.info(f"Processing message: {request_message_json}")
    request_message = RequestMessage.parse_from_json(request_message_json)

    logger.info(f"request message parsed: {request_message}")
    # report에 모델 실행 결과 저장
    # 이 코드 라인에서 호출하는 실제 모델 함수로 바꿔야 한다.
    task_start_time = datetime.datetime.now().isoformat(timespec='milliseconds')
    logger.info(f"start running at {task_start_time}")
    status, model_result = model_mock.run_model(request_message)
    task_end_time = datetime.datetime.now().isoformat(timespec='milliseconds')
    logger.info(f"end running at {task_end_time}")

    # TODO 에러 발생시 처리 필요함
    report = make_report(request_message.token, model_name, status, task_start_time, task_end_time, model_result)
    logger.info(f'Report: {report}')
    return report


def make_report(token, model_name, status, task_start_time, task_end_time, model_result):
    report_template = '{ "token": "%s", "modelName": "%s", "status": "%s", "taskStartTime": "%s", "taskEndTime": "%s", "report": "%s" }'
    return report_template % (token, model_name, status, task_start_time, task_end_time, model_result)


def get_status():
    global task_status
    return task_status

