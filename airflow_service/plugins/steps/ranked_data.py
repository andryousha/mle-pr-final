import pandas as pd
import numpy as np
from airflow.providers.postgres.hooks.postgres import PostgresHook
from catboost import CatBoostClassifier, Pool
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

MODEL_PATH = "./tmp/postgres_data/catboost_model.cbm"


def create_table():
    """Инициализация таблицы в БД."""

    postgres_hook = PostgresHook("destination_db")

    db_conn = postgres_hook.get_sqlalchemy_engine()

    metadata = MetaData()

    candidates_ranked_table = Table(
        "candidates_ranked",
        metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),
        Column("rec_id", BigInteger),
        Column("user_id", BigInteger),
        Column("item_id", BigInteger),
        Column("als_score", Float),
        Column("category_id", Integer),
        Column("parent_id", Integer),
        Column("available", Integer),
        Column("cb_score", Float),
        Column("rank", Integer),
        UniqueConstraint("rec_id", name="unique_rec_id_4_constraint"),
    )

    if not inspect(db_conn).has_table(candidates_ranked_table.name):
        metadata.create_all(db_conn)


def extract_candidates_train(**kwargs):
    """Получение train даты из БД."""
    postgres_hook = PostgresHook("destination_db")

    db_conn = postgres_hook.get_conn()

    sql = """
    SELECT *
    FROM candidates_train;
    """

    candidates_train = pd.read_sql(sql, db_conn)
    db_conn.close()

    ti = kwargs["ti"]
    ti.xcom_push("extracted_training_data", candidates_train)


def extract_candidates_inference(**kwargs):
    """Получение кандидатов инференса"""
    postgres_hook = PostgresHook("destination_db")

    db_conn = postgres_hook.get_conn()

    sql = """
    SELECT *
    FROM candidates_inference;
    """

    candidates_inference = pd.read_sql(sql, db_conn)
    db_conn.close()

    ti = kwargs["ti"]
    ti.xcom_push("extracted_inference_data", candidates_inference)


def train_model_infer(**kwargs):
    """Тренировка модели и предсказание"""

    model = CatBoostClassifier()
    model.load_model(MODEL_PATH)

    ti = kwargs["ti"]
    candidates_train = ti.xcom_pull(
        task_ids="extract_candidates_train", key="extracted_training_data"
    )

    features = ["als_score", "category_id", "parent_id", "available"]
    cat_features = ["category_id", "parent_id"]
    target = ["target"]

    train_data = Pool(
        data=candidates_train[features],
        label=candidates_train[target],
        cat_features=cat_features,
    )

    model.fit(train_data)

    candidates_inference = ti.xcom_pull(
        task_ids="extract_candidates_inference", key="extracted_inference_data"
    )

    inf_data = Pool(data=candidates_inference[features], cat_features=cat_features)
    predictions = model.predict_proba(inf_data)
    candidates_inference["cb_score"] = predictions[:, 1]

    candidates_inference_ranked = candidates_inference.sort_values(
        by=["user_id", "cb_score"], ascending=[True, False]
    )

    candidates_inference_ranked["rank"] = (
        candidates_inference_ranked.groupby("user_id").cumcount() + 1
    )
    candidates_inference_ranked = candidates_inference_ranked.reset_index(drop=True)

    ti.xcom_push("ranked_data", candidates_inference_ranked)


def load(**kwargs):
    """Запись отранжированных предсказаний в БД"""

    postgres_hook = PostgresHook("destination_db")

    ti = kwargs["ti"]
    data = ti.xcom_pull(task_ids="train_model_infer", key="ranked_data")

    postgres_hook.insert_rows(
        table="candidates_ranked",
        replace=True,
        target_fields=data.columns.tolist(),
        replace_index=["rec_id"],
        rows=data.values.tolist(),
    )