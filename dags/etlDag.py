from datetime import datetime,timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from src import dataRetrival,clean,transform,pushToLake

defaultArgs = {
    'owner': 'Oshith Roshantha',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'earthquake_etl_pipeline',
    default_args=defaultArgs,
    start_date=datetime(2024, 11, 26),
    description='ETL Pipeline for Earthquake Data',
    schedule_interval=timedelta(hours=1),
    catchup=True,
)

def fetchData(**kwargs):
    executionDate = kwargs['execution_date']
    prevExecutionDate = kwargs.get('prev_execution_date')
    dataRetrival.fetchFromApi(prevExecutionDate,executionDate)

def preprocessData():
    clean.fetchFromAzure()

def transformData():
    status=transform.downloadParquetFromAzure()
    return status 

def pushToProduction(**kwargs):
    taskInstance = kwargs['task_instance']
    previousTaskStatus = taskInstance.xcom_pull(task_ids='transformDataTask')
    if previousTaskStatus == 0:
        print("No data to push to Production")
    else:
        pushToLake.pushToProduction()

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
    task_id='transformData',
    python_callable=transformData,
    provide_context=True,
    dag=dag,
)

taskPushToProduction = PythonOperator(
    task_id='pushToProduction',
    python_callable=pushToProduction,
    provide_context=True,
    dag=dag,
)

taskFetchData >> taskPreprocessData >> taskTransformData >> taskPushToProduction