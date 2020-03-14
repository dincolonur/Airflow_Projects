from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 sql_query="",
                 table="",
                 is_truncate="",
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.sql_query = sql_query
        self.table = table
        self.is_truncate = is_truncate

    def execute(self, context):
        self.log.info('LoadDimensionOperator has started for Table: {}'.format(self.table))
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        if self.is_truncate:
            redshift.run('TRUNCATE TABLE {}'.format(self.table))
        redshift.run(self.sql_query)
        self.log.info('LoadDimensionOperator has ended successfully for Table: {}'.format(self.table))
