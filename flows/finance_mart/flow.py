from prefect import flow, task, get_run_logger
from utils import prefect_custom_blocks, extraction_load as el
import random
import subprocess
from datetime import datetime
from prefect.runtime import flow_run, task_run
from prefect.task_runners import SequentialTaskRunner
import time

ERROR_RATE = 1/4

def generate_random_error():
    assert random.random() >= ERROR_RATE

class DataExtractionError(Exception):
    """A custom exception"""
    pass

class DataLoadingError(Exception):
    """A custom exception"""
    pass

class DataTransformationError(Exception):
    """A custom exception"""
    pass

class DataQualityTestError(Exception):
    """A custom exception"""
    pass

def generate_etl_flow_run_name():
    flow_name = flow_run.flow_name
    parameters = flow_run.parameters
    data_mart_name = parameters["config"]["data_mart_name"]
    current_datetime_str = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{flow_name}-{data_mart_name}-at-{current_datetime_str}"

def generate_etl_task_run_name():
    task_name = task_run.task_name
    parameters = task_run.parameters
    data_mart_name = parameters["config"]["data_mart_name"]
    current_datetime_str = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{task_name}-{data_mart_name}-at-{current_datetime_str}"


@task(retries=3, retry_delay_seconds=[1, 10, 100], tags=['extract-task'], task_run_name=generate_etl_task_run_name)
def extract_data(config: dict):
    logger = get_run_logger()
    try:
        time.sleep(random.randint(2, 8))
        generate_random_error()
    except:
        logger.error(f'There was a problem extracting data from ....')
        raise DataExtractionError("There was a problem extracting data from ....")
    finally:
        logger.info(f"Data extraction task finished for {config['data_mart_name']}")


@task(retries=3, retry_delay_seconds=[1, 2, 3], tags=['load-task'], task_run_name=generate_etl_task_run_name)
def load_data(data, config: dict):
    try:
        logger = get_run_logger()
        time.sleep(random.randint(2, 8)) # fake processing time
        generate_random_error()
    except:
        logger.error(f'There was a problem loading data into ....')
        raise DataLoadingError("There was a problem loading data into ....")
    finally:
        logger.info(f"Data loading task finished for {config['data_mart_name']}")

@task(retries=3, retry_delay_seconds=[1, 2, 3], tags=['dbt-run-task'], task_run_name=generate_etl_task_run_name)
def run_dbt_models(data_mart_name: str, config: dict):
    try:
        logger = get_run_logger()
        generate_random_error()
        process = subprocess.run(["dbt", "run", "--models", f"transformation.{data_mart_name}.models.*"], capture_output=True)
        logger.info('stdout:', process.stdout.decode())
    except:
        logger.error(f'There was a problem running DBT models for {data_mart_name}')
        raise DataTransformationError(f"There was a problem running DBT models for {data_mart_name}")
    finally:
        logger.info(f"Dbt models run task finished for {config['data_mart_name']}")


@task(retries=3, retry_delay_seconds=[1, 2, 3], tags=['dbt-tests-task'], task_run_name=generate_etl_task_run_name)
def run_dbt_tests(data_mart_name: str, config: dict):
    try:
        logger = get_run_logger()
        generate_random_error()
        subprocess.run(["dbt", "test", "--models", f"transformation.{data_mart_name}.tests.*"])
    except:
        logger.error(f"There was a problem running DBT tests for {data_mart_name}")
        raise DataQualityTestError(f"There was a problem running DBT tests for {data_mart_name}")
    finally:
        logger.info(f"Dbt tests task finished for {config['data_mart_name']}")



@flow(flow_run_name=generate_etl_flow_run_name, task_runner=SequentialTaskRunner())
def extract_and_load_job(config: dict):
    data_mart_name = config["data_mart_name"]
    logger = get_run_logger()
    logger.info(f'Starting extract_and_load_job for data mart: {data_mart_name}')
    extraction_task = extract_data(config)
    logger.info('Data extraction completed')
    load_data(extraction_task, config)
    logger.info(f'Finished extract_and_load_job for data mart: {data_mart_name}')

@flow(flow_run_name=generate_etl_flow_run_name, task_runner=SequentialTaskRunner())
def transformation_job(config: dict):
    data_mart_name = config["data_mart_name"]
    logger = get_run_logger()
    logger.info(f'Starting transformation_job for data mart: {data_mart_name}')
    run_dbt_models(data_mart_name, config)
    logger.info('DBT models run completed')
    run_dbt_tests(data_mart_name, config)
    logger.info('DBT tests run completed')
    logger.info(f'Finished transformation_job for data mart: {data_mart_name}')

@flow(flow_run_name=generate_etl_flow_run_name)
def run_etl_job(config: dict = {"data_mart_name": "finance_mart"}):
    data_mart_name = config["data_mart_name"]
    logger = get_run_logger()
    logger.info(f'Starting run_etl_job for data mart: {data_mart_name}')
    extract_and_load_job(config)
    transformation_job(config)
    logger.info(f'Finished run_etl_job for data mart: {data_mart_name}')

if __name__ == '__main__':
    run_etl_job.serve(name="finance-etl")
