from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                                LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries

default_args = {
    'owner': 'onur_dincol',
    'start_date': datetime(2019, 1, 12),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'email_on_retry': False
}

dag = DAG('s3_to_redshift_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 * * * *',
          max_active_runs=1
        )

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    provide_context=True,
    table="staging_events",
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    s3_bucket="onur-s3-test-bucket",
    s3_key="log_data",
    region="us-west-2",
    file_format="JSON",
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    provide_context=True,
    table="staging_songs",
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    s3_bucket="onur-s3-test-bucket",
    s3_key="song_data",
    region="us-west-2",
    data_format="JSON",
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    provide_context=True,
    redshift_conn_id='redshift',
    sql_query=SqlQueries.songplay_table_insert
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    table='users',
    is_truncate='true',
    redshift_conn_id='redshift',
    sql_query=SqlQueries.user_table_insert
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    table='songs',
    is_truncate='true',
    redshift_conn_id='redshift',
    sql_query=SqlQueries.song_table_insert
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    table='artists',
    is_truncate='true',
    redshift_conn_id='redshift',
    sql_query=SqlQueries.artist_table_insert
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    table='time',
    is_truncate='true',
    redshift_conn_id='redshift',
    sql_query=SqlQueries.time_table_insert
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    redshift_conn_id='redshift',
    tables=["songplay", "users", "song", "artist", "time"]
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)


start_operator >> [stage_songs_to_redshift, stage_events_to_redshift]
[stage_events_to_redshift, stage_songs_to_redshift] >> load_songplays_table
load_songplays_table >> [load_user_dimension_table, load_song_dimension_table, load_artist_dimension_table,
                           load_time_dimension_table] >> run_quality_checks
run_quality_checks >> end_operator
