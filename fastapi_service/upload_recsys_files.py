import os
from dotenv import load_dotenv
import psycopg2 as psycopg
import pandas as pd

load_dotenv('../.env')

connection = {"sslmode": "require", "target_session_attrs": "read-write"}
postgres_credentials = {
    "host": os.getenv("DB_DESTINATION_HOST"),
    "port": os.getenv("DB_DESTINATION_PORT"),
    "dbname": os.getenv("DB_DESTINATION_NAME"),
    "user": os.getenv("DB_DESTINATION_USER"),
    "password": os.getenv("DB_DESTINATION_PASSWORD"),
}
connection.update(postgres_credentials)

def extract_table(
    table_name: str, connection: dict[str, str] = connection
) -> pd.DataFrame:
    """Выгрузить таблицу из PG в pd.DataFrame"""
    with psycopg.connect(**connection) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {table_name}")
            data = cur.fetchall()
            columns = [col[0] for col in cur.description]

    extracted_table = pd.DataFrame(data, columns=columns)

    return extracted_table


if __name__ == "__main__":
    PATH = './recommendations/'
    TABLES = ['default_recs', 'online_recs', 'candidates_ranked']

    for tbl in TABLES:
        df = extract_table(table_name=tbl)
        df.to_parquet(PATH + tbl + '.parquet')
        print(f"Файл {tbl + '.parquet'} загружен в папку {PATH}")




