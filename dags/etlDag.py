from datetime import datetime,timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from src import dataRetrival,clean,transform,pushToLake


defaultArgs = {
    'owner': 'Oshith Roshantha',
    'start_date': datetime(2024, 11, 24),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'etl_PipelineV50',
    default_args=defaultArgs,
    description='ETL Pipeline for Earthquake Data',
    schedule_interval=timedelta(hours=1),
    catchup=False,
)

def fetchData(**kwargs):
    executionDate = kwargs['execution_date']
    prevExecutionDate = kwargs.get('prev_execution_date')
    if prevExecutionDate is None:
        startTime = executionDate - timedelta(days=365 * 3)
    else:
        startTime = prevExecutionDate
    dataRetrival.fetchFromApi(startTime, executionDate)

def preprocessData():
    clean.fetchFromAzure()

def transformDataTask():
    status=transform.downloadParquetFromAzure()
    return status 

def pushDataToAzure(**kwargs):
    taskInstance = kwargs['task_instance']
    previousTaskStatus = taskInstance.xcom_pull(task_ids='transformDataTask')
    if previousTaskStatus == 0:
        print("No data to push to Azure")
    else:
        pushToLake.pushToAzure(transformedData)

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