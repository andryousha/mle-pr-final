# FastAPI сервис рекомендаций

Данный модуль содержит в себе сервис рекомендаций, тесты для сервиса и систему монииторинга метрик.


## Как запустить сервис?

- Необходимо заполнить файл [.env_example](../.env_example) и переименовать его в `.env`.

- В рамках модуля [airflow_service](../airflow_service) мы записали в PG три таблицы, которые понадобятся нам в 
процессе рекомендаций:
  - `default_recs`
  - `online_recs`
  - `candidates_ranked`

- Для работы сервиса нужно скачать их в папку `recommendation` c помощью скрипта [upload_recsys_files.py](./upload_recsys_files.py).   
- ```bash
  cd fastapi_service
  python upload_recsys_files.py
  ```

- Далее можно начать разворачивать сервис:
- ```bash
  docker compose up --build
  ```

- Произойдет запуск сервисов:
  - Главный сервис рекомендаций  - http://localhost:8000
  - Сервис офлайн рекомендаций   - http://localhost:8001
  - Сервис для обработки событий - http://localhost:8002
  - Сервис онлайн рекомендаций   - http://localhost:8003
  - Grafana                      - http://localhost:3000
  - Prometheus                   - http://localhost:9090

- Чтобы остановить сервис нужно выполнит команду:
- ```bash
  docker compose down
  ```


## Тесты для рекомендательных сервисов
Чтобы протестировать сервис нужно воспользоваться файлом [test_service.py](./test_service.py).   
Логи тестирования пишутся в файл [test_service.log](./test_service.log).

Команда для запуска тестов:
```bash
python test_service.py
```

Также можно провести симуляцию нагрузки на сервис с помощью скрипта [simulate_rec_load.py](./simulate_rec_load.py).

```bash
python simulate_rec_load.py
```

## Система мониторинга

В проекте для мониторинга метрик используется Grafana и Prometheus.

Код дашборда можно импортровать в Grafana c помощью файлы [dashboard.json](./dashboard.json).  
Скриншот примера дашборда можно увидеть [тут](./dashboard.png)

- Запустите `python fix_datasource_uid.py` чтобы использовать `dashboard.json` в своем Grafana.

## Используемые метрики мониторинга

- Инфраструктурные метрики
  - RAM Usage (MB
  - CPU Usage change (%/min)
- Бизнес метрики
  - Number of successful connections to online/offline recommendation services
  - Number of requests to personal recommendations
  - Number of requests to default recommendations
- Сервисные метрики
  - Request duration change (%/min)