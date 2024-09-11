from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.http.operators.http import HttpOperator
import time

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2020, 1, 1),
    'retries': 1,
}

dag = DAG(
    'http_test_dag',
    default_args=default_args,
    description='A simple test DAG',
    schedule_interval=None,
)

def delay():
    time.sleep(10)

def log_response(response):
    print(response.text)
    return True

def print_credentials(response):
    # Parse the JSON response
    data = response.json()
    
    # Extract and print the username and password
    username = data.get("username")
    password = data.get("password")
    
    print(f"Username: {username}")
    print(f"Password: {password}")
    
    # Optionally, return True to indicate the task succeeded
    return True

delay_task = PythonOperator(
    task_id='delay_task',
    python_callable=delay,
)

task_get_op = HttpOperator(
    task_id="get_op",
    http_conn_id="my_http_connection",  # Reference to the HTTP connection
    method="GET",
    endpoint="/airflow/get",
    data={},
    response_check=print_credentials,
    dag=dag,
)

task_post_op = HttpOperator(
    task_id="post_op",
    http_conn_id="my_http_connection",
    endpoint="/airflow/post",
    headers={"Content-Type": "application/json"},
    data={},
    response_check=log_response,
    dag=dag,
)


#task flow
task_get_op >> delay_task >> task_post_op
