# EDA и моделирование

Данная директория содержит ноутбук с исследованием и моделированием для задачи рекомендаций.
Эксперименты логировались в MLFLOW.


## Структура
- [`rec_sys.ipynb`](./rec_sys.ipynb) - Ноутбук содержит исследование данных и обучения моделей рекомендаций.
- [`assets`](./assets/) - Папка с артефактами, которые залогированы в `MLFLOW`.
- [`run_mlflow.sh`](./run_mlflow.sh) - Скрипт для запуска `MLFLOW` сервиса.


## Виртуальное окружение

Для того чтобы код заработал, нужно в корне проекта выполнить следующие команды и создать нужное виртуальное окружение:
```bash
sudo apt-get install python3.10-venv
python -m venv .venv_recsys
source .venv_recsys/bin/activate
pip install -r requirements.txt
```

Не забудьте заполнить файл [.env_example](../.env_example) и переименовать его в `.env`

## Запуск MLFLOW
```bash
cd recsys
sh run_mlflow_server.sh
```
Сервис должен развернутся по адресу: http://localhost:5000

## Запуск Jupyter ноутбука
```bash
jupyter notebook
```

## Какие важные модели и артефакты были сохранены в процессе исследования
- `top_popular.parquet` -  Top-100 айтемов (дефолтные рекомендации)
* `similar.parquet` - Похожие айтемы (online рекомендации)
* `candidates_train.parquet` - Кандидаты для тренировки ранжирующей модели
* `candidates_inference.parquet` - Кандидаты для ранжирования
* `catboost_model.cmb` - Лучшая ранжирующая модель


Файлы были сохранены в папке [postgres_data](../airflow_service/postgres_data/) для дальнейшего использования в Airflow дагах.