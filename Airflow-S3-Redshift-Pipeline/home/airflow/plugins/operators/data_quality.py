from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 tables=[],
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id,
        self.tables = tables

    def execute(self, context):
        redshift_hook = PostgresHook(self.redshift_conn_id)
        for table in self.tables:
            self.log.info('DataQualityOperator has started for Table: {}'.format(table))
            records = redshift_hook.get_records(f"SELECT COUNT(*) FROM {table}")
            if len(records) < 1 or len(records[0]) < 1 :
                self.log.error('Data quality check error. Table {} returned no results'.format(table))
                raise ValueError('Data quality check error. {} returned no results'.format(table))
            num_records = records[0][0]
            if num_records < 1:
                self.log.error('Data quality check error. Table {} returned o rows'.format(table))
                raise ValueError('Data quality check error. {} contained 0 rows'.format(table))
                
            self.log.info('DataQualityOperator has ended successfully for Table: {}'.format(table))
                
             
       