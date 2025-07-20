import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import (
    Column,
    BigInteger,
    MetaData,
    Table,
    UniqueConstraint,
    inspect,
    Integer,
)

DEFAULT_RECS_PATH = "./tmp/postgres_data/top_popular.parquet"


def create_table():
    """Инициализация таблицы в БД"""

    postgres_hook = PostgresHook("destination_db")

    db_conn = postgres_hook.get_sqlalchemy_engine()

    metadata = MetaData()

    default_recs_table = Table(
        "default_recs",
        metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),
        Column("rec_id", BigInteger),
        Column("item_id", BigInteger),
        Column("items_cnt", Integer),
        Column("item_id_encoded", Integer),
        UniqueConstraint("rec_id", name="unique_rec_id_1_constraint"),
    )

    if not inspect(db_conn).has_table(default_recs_table.name):
        metadata.create_all(db_conn)


def extract(**kwargs):
    """Загрузка файла в пандас дф"""
    data = pd.read_parquet(DEFAULT_RECS_PATH)
    ti = kwargs["ti"]
    ti.xcom_push("extracted_data", data)


def load(**kwargs):
    """загрузка данных в таблицу"""
    postgres_hook = PostgresHook("destination_db")

    ti = kwargs["ti"]
    data = ti.xcom_pull(task_ids="extract", key="extracted_data")

    postgres_hook.insert_rows(
        table="default_recs",
        replace=True,
        target_fields=data.columns.tolist(),
        replace_index=["rec_id"],
        rows=data.values.tolist(),
    )