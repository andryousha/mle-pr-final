# Пайплайн обработки данных через Airflow
 

## Структура модуля

- [`config`](./config/) - конфигурация Airflow
- [`dags`](./dags/) - папка с дагами Airflow
- [`logs`](./logs/) - папка с логами Airflow
- [`plugins`](./plugins/) - дополнительные модули для работы дагов
- [`Dockerfile`](./Dockerfile) - докерфайл
- [`docker-compose.yaml`](./docker-compose.yaml) - файл для удобного разворачивания и запуска Airflow
- [`requirements-airflow.txt`](./requirements-airflow.txt) - файл с зависимостями
-  [`postgres_data`](./postgres_data/) - папка с файлами для загрузки в Postgres через Airflow.

## Airflow

Чтобы запустить Airflow необходимо:

1. Сохранить свой id в .env. внутри папки `airflow_service`

```bash
cd airflow_service
echo -e "\nAIRFLOW_UID=$(id -u)" >> .env
```
2. Инициализировть airflow

```bash
docker compose up airflow-init
```

3. Сделать очистку кэша

```bash
docker compose down --volumes --remove-orphans
```

4. Запустить билд

```bash
docker compose up --build
```

5. Заполнить `destination_db` в интерфейсе (`localhost:8080`) в разделе connections

Дефолтный логин пароль: `airflow`/`airflow`

6. Как остановить сервис?

```bash
cd airflow_service
docker compose down
```

### Описание Dag'ов

- [`dags`](./dags/) - папка со скриптами дагов.

- [`load_default_recs.py`](./dags/load_default_recs.py) - Загрузка дефолтных рекомендаций в Postgres
- [`load_online_recs.py`](./dags/load_online_recs.py) - Загрузка онлайн рекомендаций в Postgres
- [`load_candidates_train.py`](./dags/load_candidates_train.py) - Загрузка train кандидатов в Postgres
- [`load_candidates_inference.py`](./dags/load_candidates_inference.py) - Загрузка тестовых кандидатов в Postgres
- [`load_candidates_ranked.py`](./dags/load_candidates_ranked.py) - Тренировка модели на train кандидатах и инференс ранжирование на тестовых кандидатах

### Описание Plugin'ов 

- [`steps`](./plugins/steps) - папка с дополнительными скриптами для дагов

- [`default_recs.py`](./plugins/steps/default_recs.py) - Загрузка дефолтных рекомендаций в Postgres
| [`online_recs.py`](./plugins/steps/online_recs.py) - Загрузка онлайн рекомендаций в Postgres
| [`training_data.py`](./plugins/steps/training_data.py) - Загрузка train кандидатов в Postgres
| [`inference_data.py`](./plugins/steps/inference_data.py) - Загрузка тестовых кандидатов в Postgres
| [`ranked_data.py`](./plugins/steps/ranked_data.py) - Тренировка модели на train кандидатах и инференс ранжирование на тестовых кандидатах
| [`messages.py`](./plugins/steps/messages.py) - Коллбэки для использование аалертинга через бота в Телеграм