from config import *
from datetime import timedelta
from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.providers.ssh.hooks.ssh import SSHHook

import os
os.chdir(AIRFLOW_EC2_USER_FILE_PATH)  

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': AIRFLOW_START_DATE , 
    'email': [AIRFLOW_EMIAL],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('todaysoutfit_production', default_args=default_args, schedule_interval=timedelta(days=1))

# ec2-crawler-men
wear_crawler_men = SSHHook(
    remote_host = EC2_WEAR_CRAWLER_MEN_HOST,
    username = EC2_USERNAME,
    key_file = EC2_WEAR_CRAWLER_MEN_KEY_FILE,
    port = EC2_PORT
)

# ec2-crawler-women
wear_crawler_women = SSHHook(
    remote_host = EC2_WEAR_CRAWLER_WOMEN_HOST,
    username = EC2_USERNAME,
    key_file = EC2_WEAR_CRAWLER_WOMEN_KEY_FILE,
    port = EC2_PORT
)

# ec2-datapipeline/etl
data_pipeline = SSHHook(
    remote_host = EC2_ETL_HOST,
    username = EC2_USERNAME,
    key_file = EC2_ETL_KEY_FILE,
    port = EC2_PORT
)


# start web crawler
crawler_1_1= SSHOperator(
    task_id="wear_crawler_checknew_kol_men",
    ssh_hook=wear_crawler_men,
    ssh_conn_id='ssh_wear',
    command='source wear_crawler_11_checknew_kol_men.sh ',
    dag=dag
)

crawler_1_2= SSHOperator(
    task_id="wear_crawler_checknew_kol_women",
    ssh_hook=wear_crawler_women,
    ssh_conn_id='ssh_wear',
    command='source wear_crawler_12_checknew_kol_women.sh ',
    dag=dag
)


crawler_2_1= SSHOperator(
    task_id="wear_crawler_checknew_outfit_men",
    ssh_hook=wear_crawler_men,
    ssh_conn_id='ssh_wear',
    command='source wear_crawler_21_checknew_outfit_men.sh ',
    dag=dag
)

crawler_2_2= SSHOperator(
    task_id="wear_crawler_checknew_outfit_women",
    ssh_hook=wear_crawler_women,
    ssh_conn_id='ssh_wear',
    command='source wear_crawler_22_checknew_outfit_women.sh ',
    dag=dag
)

# start datapipeline
datapipeline_1_1= SSHOperator(
    task_id="wear_kol",
    ssh_hook=data_pipeline,
    ssh_conn_id='ssh_wear',
    command='source wear_get_insert_11_kol.sh ',
    dag=dag
)

datapipeline_2_1= SSHOperator(
    task_id="wear_outfit",
    ssh_hook=data_pipeline,
    ssh_conn_id='ssh_wear',
    command='source wear_get_insert_21_outfit.sh ',
    dag=dag
)

datapipeline_2_2= SSHOperator(
    task_id="wear_product",
    ssh_hook=data_pipeline,
    ssh_conn_id='ssh_wear',
    command='source wear_get_insert_22_product.sh ',
    dag=dag
)

datapipeline_3_1= SSHOperator(
    task_id="wear_match",
    ssh_hook=data_pipeline,
    ssh_conn_id='ssh_wear',
    command='source wear_get_insert_31_match.sh ',
    dag=dag
)

datapipeline_3_2= SSHOperator(
    task_id="wordcloud",
    ssh_hook=data_pipeline,
    ssh_conn_id='ssh_wear',
    command='source wordcloud.sh ',
    dag=dag
)

datapipeline_4_1= SSHOperator(
    task_id="wear_user",
    ssh_hook=data_pipeline,
    ssh_conn_id='ssh_wear',
    command='source wear_get_insert_41_user.sh ',
    dag=dag
)

datapipeline_5_1= SSHOperator(
    task_id="wear_like_rating",
    ssh_hook=data_pipeline,
    ssh_conn_id='ssh_wear',
    command='source wear_get_insert_51_like_rating.sh ',
    dag=dag
)

datapipeline_5_2= SSHOperator(
    task_id="wear_comment_rating",
    ssh_hook=data_pipeline,
    ssh_conn_id='ssh_wear',
    command='source wear_get_insert_52_comment_rating.sh ',
    dag=dag
)


datapipeline_6_1= SSHOperator(
    task_id="knn_recommendation",
    ssh_hook=data_pipeline,
    ssh_conn_id='ssh_wear',
    command='source knn_recommendation.sh ',
    dag=dag
)

datapipeline_7_1= SSHOperator(
    task_id="latest_data_record",
    ssh_hook=data_pipeline,
    ssh_conn_id='ssh_wear',
    command='source latest_data_record.sh ',
    dag=dag
)


crawler_1_1 >> crawler_2_1 >> datapipeline_1_1 >> datapipeline_2_1 >> datapipeline_3_1 >>datapipeline_4_1 >>datapipeline_5_1 >> datapipeline_6_1 >> datapipeline_7_1
crawler_1_2 >> crawler_2_2 >> datapipeline_1_1 >> datapipeline_2_2 >> datapipeline_3_1 >>datapipeline_4_1 >>datapipeline_5_2 >> datapipeline_6_1 >> datapipeline_7_1
crawler_1_1 >> crawler_2_1 >> datapipeline_1_1 >> datapipeline_2_1 >> datapipeline_3_2
crawler_1_2 >> crawler_2_2 >> datapipeline_1_1 >> datapipeline_2_1 >> datapipeline_3_2