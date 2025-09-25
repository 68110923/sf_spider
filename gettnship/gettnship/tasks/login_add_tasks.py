import json
import redis
from datetime import datetime


class LoginTaskManager:
    def __init__(self, host='43.138.130.198', port=6379, db=0, password='000578'):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True  # 自动将bytes转为str
        )

    def add_task(self, redis_key, task):
        print(f'redis_key: {redis_key}, task: {task}')
        self.redis_client.lpush(redis_key, json.dumps(task, ensure_ascii=False))



if __name__ == '__main__':
    task_manager = LoginTaskManager()
    task = {
        'spider_name': 'gettnship_login',
        'url': 'https://www.gettnship.com/login',
        'config_key': 'gettnship_user_money',
        'datetime': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    }
    task_manager.add_task('gettnship_login:queue', task)
