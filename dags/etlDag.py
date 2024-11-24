import sys
import os
from datetime import datetime,timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import dataRetrival
import clean
import transform
import pushToLake

defaultArgs = {
    'owner': 'Oshith Roshantha',
    'start_date': datetime(2024, 11, 24),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'etl_Pipeline',
    default_args=defaultArgs,
    description='ETL Pipeline for Earthquake Data',
    schedule_interval=timedelta(hours=1),
    catchup=False,
)

def setTime(executionDate, prevExecutionDate, **kwargs):
    if prevExecutionDate is None:
        startTime = executionDate - timedelta(days=365 * 3)
    else:
        startTime = prevExecutionDate
    endTime = executionDate
    return startTime, endTime

def fetchData(**kwargs):
    executionDate = kwargs['execution_date']
    prevExecutionDate = kwargs.get('prev_execution_date')
    startTime, endTime = setTime(executionDate, prevExecutionDate, **kwargs)
    rawData = dataRetrival.fetchFromApi(startTime, endTime)
    return rawData

def preprocessData(**kwargs):
    taskInstance = kwargs['task_instance']
    rawData = taskInstance.xcom_pull(task_ids='fetchData')
    processedData = clean.preProcessing(rawData)
    return processedData

def transformDataTask(**kwargs):
    taskInstance = kwargs['task_instance']
    processedData = taskInstance.xcom_pull(task_ids='preprocessData')
    
    previousTransformData = taskInstance.xcom_pull(task_ids='transformDataTask', key='return_value')
    scaler = previousTransformData['scalar'] if previousTransformData and 'scalar' in previousTransformData else None
    encoder = previousTransformData['encoder'] if previousTransformData and 'encoder' in previousTransformData else None
    
    encodedData,  scaler, encoder = transform.transformData(processedData, scaler, encoder)
    return {'encodedData': encodedData, 'scalar': scaler, 'encoder':encoder}

def pushDataToAzure(**kwargs):
    taskInstance = kwargs['task_instance']
    transformedData = taskInstance.xcom_pull(task_ids='transformDataTask')
    pushToLake.pushToAzure(transformedData['encodedData'])

taskFetchData = PythonOperator(
    task_id='fetchData',
    python_callable=fetchData,
    provide_context=True,
    dag=dag,
)

taskPreprocessData = PythonOperator(
    task_id='preprocessData',
    python_callable=preprocessData,
    provide_context=True,
    dag=dag,
)

taskTransformData = PythonOperator(
    task_id='transformDataTask',
    python_callable=transformDataTask,
    provide_context=True,
    dag=dag,
)

taskPushDataToAzure = PythonOperator(
    task_id='pushDataToAzure',
    python_callable=pushDataToAzure,
    provide_context=True,
    dag=dag,
)

taskFetchData >> taskPreprocessData >> taskTransformData >> taskPushDataToAzure