"""Главный скрипт"""
import requests
from requests.exceptions import ConnectionError
from fastapi import FastAPI
from prometheus_client import Counter, Gauge
from prometheus_fastapi_instrumentator import Instrumentator

from .constants import (
    OFFLINE_URL,
    EVENTS_URL,
    FEATURES_URL,
    RECS_OFFLINE_SERVICE_PORT,
    EVENTS_SERVICE_PORT,
    FEATURES_SERVICE_PORT,
)

headers = {"Content-type": "application/json", "Accept": "text/plain"}
recommendations_url = OFFLINE_URL + ":" + str(RECS_OFFLINE_SERVICE_PORT)
events_url = EVENTS_URL + ":" + str(EVENTS_SERVICE_PORT)
features_url = FEATURES_URL + ":" + str(FEATURES_SERVICE_PORT)

app = FastAPI(title="recommendations_main")

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Кастомные метрики для prometheus
counter_success_offline = Counter(
    name="counter_success_offline",
    documentation="Число успешных обращений к ручке офлайн рекомендаций",
)
counter_success_online = Counter(
    name="counter_success_online",
    documentation="Число успешных обращений к ручке онлайн рекомендаций",
)

gauge_personal_requests = Gauge(
    name="gauge_personal_requests",
    documentation="Число обращений к персональным рекомендациям",
)

gauge_default_requests = Gauge(
    name="gauge_default_requests",
    documentation="Число обращения к деволтным рекомендациям",
)


def dedup_ids(ids):
    """Removes duplicates from a list."""
    seen = set()
    ids = [id for id in ids if not (id in seen or seen.add(id))]

    return ids


@app.get("/stats")
async def stats():
    response = requests.get(recommendations_url + "/get_stats")

    return response.json()


@app.get("/healthy")
async def healthy():
    """Статус сервиса"""
    try:
        _ = requests.get(recommendations_url + "/healthy")
        _ = requests.get(events_url + "/healthy")
        _ = requests.get(features_url + "/healthy")
    except ConnectionError:
        return {"status": "unhealthy"}
    else:
        return {"status": "healthy"}


@app.post("/recommendations_offline")
async def recommendations_offline(user_id: int, k: int = 5):
    """Вывести к офлайн рекомендаций"""
    params = {"user_id": user_id, "k": k}
    response = requests.post(
        recommendations_url + "/get_recs", params=params, headers=headers
    )
    if response.status_code == 200:
        counter_success_offline.inc()
    response = response.json()

    endpoint_stats = await stats()
    gauge_personal_requests.set(endpoint_stats["request_personal_count"])
    gauge_default_requests.set(endpoint_stats["request_default_count"])

    return {"recs": response}


@app.post("/recommendations_online")
async def recommendations_online(user_id: int, k: int = 5, num_events: int = 3):
    """Вывести к онлайн рекомендаций основанных на последних онлайн событиях пользователя"""
    params = {"user_id": user_id, "k": num_events}
    response = requests.post(events_url + "/get", params=params, headers=headers)
    events = response.json()
    events = events["events"]

    items = []
    scores = []
    for item_id in events:
        params = {"item_id": item_id, "k": k}
        response = requests.post(
            features_url + "/similar_items", headers=headers, params=params
        )
        if response.status_code == 200:
            counter_success_online.inc()
        response = response.json()
        items += response["itemid_2"]
        scores += response["score"]
    combined = list(zip(items, scores))
    combined = sorted(combined, key=lambda x: x[1], reverse=True)
    combined = [item for item, _ in combined]

    combined = dedup_ids(combined)

    return {"recs": combined[:k]}


@app.post("/recommendations")
async def recommendations(user_id: int, k: int = 50):
    """Вывести смешанные рекомендации основанные на онлайн и офлайн истории"""

    result_online = await recommendations_online(user_id=user_id, k=k)
    result_offline = await recommendations_offline(user_id=user_id, k=k)

    if result_online["recs"] == []:
        return {"recs": result_offline["recs"]}

    recs_online = result_online["recs"]
    recs_offline = result_offline["recs"]

    recs_blended = []
    min_length = min(len(recs_offline), len(recs_online))
    for i in range(min_length):
        recs_blended.append(recs_online[i])
        recs_blended.append(recs_offline[i])

    recs_blended = dedup_ids(recs_blended)

    return {"recs": recs_blended[:k]}