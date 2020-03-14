# 1 - Airflow-S3-Redshift-Pipeline

In this project the source data resides in S3 and needs to be processed in newly created data warehouse in Amazon Redshift.
The source datasets consist of JSON logs that tell about user activity in the application and JSON metadata about the songs the users listen to.

This project has the core concepts of Apache Airflow by creating own custom operators to perform tasks such as staging the data,
filling the data warehouse, and running checks on the data as the final step.

## Project Structure:

### SOURCE DATASETS:

Log data: s3://onur-s3-test-bucket/log_data

Song data: s3://onur-s3-test-bucket/song_data

### DAG:
Main component of the flow.
Source code: /home/airflow/dags/s3_to_redshift_dag.py

### OPERATORS:

### Stage Operator:
The stage operator loads JSON formatted files from S3 to Amazon Redshift staging tables.
The operator creates and runs a SQL COPY statement based on the parameters provided.
The operator's parameters specify where in S3 the file is loaded and what is the target table.
staging_events and staging_songs tables are the target tables in this project.
Source code: /home/airflow/plugins/operators/stage_redshift.py

### Fact and Dimension Operators:
With dimension and fact operators, we can utilize the provided SQL helper class to run data transformations.
Most of the logic is within the SQL transformations and the operator is expected to take as input a SQL statement and target database on which to run the query.

Dimension loads are often done with the truncate-insert pattern where the target table is emptied before the load.
We could also have a parameter that allows switching between insert modes when loading dimensions.
Fact tables are usually so massive that they should only allow append type functionality.
In this project Fact Table: songplays, Dimension Tables: artists, songs, users, time
Source code: /home/airflow/plugins/operators/load_fact.py
Source code: /home/airflow/plugins/operators/load_dimension.py


### Data Quality Operator
The final operator to create is the data quality operator, which is used to run checks on the data itself.
The operator's main functionality is to receive one or more SQL based test cases along with the expected results and execute the tests.
For each the test, the test result and expected result needs to be checked and if there is no match, the operator raises an exception and the task retries and fails eventually.

For example one test could be a SQL statement that checks if certain column contains NULL values by counting all the rows that have NULL in the column.
We do not want to have any NULLs so expected result would be 0 and the test would compare the SQL statement's outcome to the expected result.
Source code: /home/airflow/plugins/operators/data_quality.py
