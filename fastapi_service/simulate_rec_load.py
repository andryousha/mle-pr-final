"""Симуляция нагрузки на сервис"""
import time

import numpy as np

from test_service import send_test_request


if __name__ == "__main__":
    # Юзеры с первональной историей
    user_ids_personal_history = [1150086, 962631, 1073958, 388200, 530559]
    # Рандомные бзеры
    user_ids_random = np.random.choice(1000, 3, replace=False).tolist()
    # Соберем всех вмесие
    user_ids = user_ids_personal_history + user_ids_random
    np.random.shuffle(user_ids)

    # Running a series of requests
    for user_id in user_ids:
        user_params = {"user_id": user_id, "k": 5}
        res = send_test_request(
            params=user_params,
            url="http://0.0.0.0:8000",
            endpoint="/recommendations",
        )
        time.sleep(5)