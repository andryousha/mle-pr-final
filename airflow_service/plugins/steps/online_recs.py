import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import (
    Column,
    Float,
    BigInteger,
    MetaData,
    Table,
    UniqueConstraint,
    inspect,
)

ONLINE_RECS_PATH = "./tmp/postgres_data/similar.parquet"


def create_table():
    """Инициализация таблицы в БД."""

    postgres_hook = PostgresHook("destination_db")

    db_conn = postgres_hook.get_sqlalchemy_engine()

    metadata = MetaData()

    online_recs_table = Table(
        "online_recs",
        metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),
        Column("rec_id", BigInteger),
        Column("itemid_1", BigInteger),
        Column("itemid_2", BigInteger),
        Column("score", Float),
        UniqueConstraint("rec_id", name="unique_rec_id_3_constraint"),
    )

    if not inspect(db_conn).has_table(online_recs_table.name):
        metadata.create_all(db_conn)


def extract(**kwargs):
    """Загрузка файла в пандас дф"""

    data = pd.read_parquet(ONLINE_RECS_PATH)

    ti = kwargs["ti"]
    ti.xcom_push("extracted_data", data)


def load(**kwargs):
    """загрузка данных в таблицу"""

    postgres_hook = PostgresHook("destination_db")

    ti = kwargs["ti"]
    data = ti.xcom_pull(task_ids="extract", key="extracted_data")

    postgres_hook.insert_rows(
        table="online_recs",
        replace=True,
        target_fields=data.columns.tolist(),
        replace_index=["rec_id"],
        rows=data.values.tolist(),
    )