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
    Integer,
)

CANDIDATES_INFERENCE_PATH = "./tmp/postgres_data/candidates_inference.parquet"


def create_table():
    """Инициализация таблицы в БД"""

    postgres_hook = PostgresHook("destination_db")

    db_conn = postgres_hook.get_sqlalchemy_engine()

    metadata = MetaData()

    candidates_inference_table = Table(
        "candidates_inference",
        metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),
        Column("rec_id", BigInteger),
        Column("user_id", BigInteger),
        Column("item_id", BigInteger),
        Column("als_score", Float),
        Column("category_id", Integer),
        Column("parent_id", Integer),
        Column("available", Integer),
        UniqueConstraint("rec_id", name="unique_rec_id_2_constraint"),
    )

    # Checking the existence of table in DB and adding a new table (if needed)
    if not inspect(db_conn).has_table(candidates_inference_table.name):
        metadata.create_all(db_conn)


def extract(**kwargs):
    """Загрузка файла в пандас дф"""

    data = pd.read_parquet(CANDIDATES_INFERENCE_PATH)

    ti = kwargs["ti"]
    ti.xcom_push("extracted_data", data)


def load(**kwargs):
    """загрузка данных в таблицу"""

    postgres_hook = PostgresHook("destination_db")

    ti = kwargs["ti"]
    data = ti.xcom_pull(task_ids="extract", key="extracted_data")

    postgres_hook.insert_rows(
        table="candidates_inference",
        replace=True,
        target_fields=data.columns.tolist(),
        replace_index=["rec_id"],
        rows=data.values.tolist(),
    )