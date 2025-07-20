"""Сервис для симуляции новой истории"""
from fastapi import FastAPI


class EventStore:
    """Класс для добавления новой истории"""

    def __init__(self, max_events_per_user: int = 10):
        """Инициализация"""
        self.events = {}
        self.max_events_per_user = max_events_per_user

    def put(self, user_id: int, item_id: int):
        """Добавить новый эвент юзеру"""
        user_events = [] if self.events.get(user_id) is None else self.events[user_id]
        self.events[user_id] = [item_id] + user_events[:self.max_events_per_user]

    def get(self, user_id: int, k: int = 5):
        """Показать онлайн историю по юзеру"""
        user_events = self.events[user_id][:k] if user_id in self.events else []

        return user_events


event_store = EventStore()

app = FastAPI(title="events")


@app.get("/healthy")
async def healthy():
    """Статус сервиса"""
    return {"status": "healthy"}


@app.post("/put")
async def put(user_id: int, item_id: int):
    """Добавить эвент в историю (ручка)"""
    event_store.put(user_id, item_id)

    return {"result": "OK"}


@app.post("/get")
async def get(user_id: int, k: int):
    """Показать онлайн историю по юзеру (ручка)"""
    events = event_store.get(user_id, k)

    return {"events": events}