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

CANDIDATES_TRAIN_PATH = "./tmp/postgres_data/candidates_train.parquet"


def create_table():
    """Инициализация таблицы в БД."""

    postgres_hook = PostgresHook("destination_db")

    db_conn = postgres_hook.get_sqlalchemy_engine()

    metadata = MetaData()

    candidates_train_table = Table(
        "candidates_train",
        metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),
        Column("rec_id", BigInteger),
        Column("user_id", BigInteger),
        Column("item_id", BigInteger),
        Column("als_score", Float),
        Column("target", Integer),
        Column("category_id", Integer),
        Column("parent_id", Integer),
        Column("available", Integer),
        UniqueConstraint("rec_id", name="unique_rec_id_5_constraint"),
    )

    if not inspect(db_conn).has_table(candidates_train_table.name):
        metadata.create_all(db_conn)


def extract(**kwargs):
    """Загрузка трейн даты из файла"""

    data = pd.read_parquet(CANDIDATES_TRAIN_PATH)

    ti = kwargs["ti"]
    ti.xcom_push("extracted_data", data)


def load(**kwargs):
    """Загрузка данных в таблицу"""

    postgres_hook = PostgresHook("destination_db")

    ti = kwargs["ti"]
    data = ti.xcom_pull(task_ids="extract", key="extracted_data")

    postgres_hook.insert_rows(
        table="candidates_train",
        replace=True,
        target_fields=data.columns.tolist(),
        replace_index=["rec_id"],
        rows=data.values.tolist(),
    )