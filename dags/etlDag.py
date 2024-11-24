from datetime import datetime,timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.dataRetrival import setTime,fetchFromApi
from src.clean import preProcessing
from src.transform import transformData
from src.pushToLake import pushToAzure
import pandas as pd

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
    rawData = fetchFromApi(startTime, endTime)
    return rawData

def preprocessData(**kwargs):
    taskInstance = kwargs['task_instance']
    rawData = taskInstance.xcom_pull(task_ids='fetchData')
    processedData = preProcessing(rawData)
    return processedData

def transformDataTask(**kwargs):
    taskInstance = kwargs['task_instance']
    processedData = taskInstance.xcom_pull(task_ids='preprocessData')
    encodedData, countData, scaler, encoder = transformData(processedData)
    return {'encodedData': encodedData, 'countData': countData}

def pushDataToAzure(**kwargs):
    taskInstance = kwargs['task_instance']
    transformedData = taskInstance.xcom_pull(task_ids='transformDataTask')
    countData = transformedData['countData']
    df = pd.DataFrame(countData)
    pushToAzure(df)

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