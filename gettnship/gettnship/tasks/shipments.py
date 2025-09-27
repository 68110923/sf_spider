import redis
import redis
import json
from datetime import datetime, timedelta


class ShipmentsManager:
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
    task_manager = ShipmentsManager()
    org_ls = [
  {
    "shipping_zip_code": "70810"
  },
  {
    "shipping_zip_code": "95060"
  },
  {
    "shipping_zip_code": "21214"
  }
]
    for org in org_ls:
        task = {
          'batch_id': int(datetime.now().strftime('%Y%m%d%H'))-1,
          'spider_name': 'gettnship_shipments',
            'config_key': 'gettnship_user_money',
            'carrier': 'ups-v2',

            'zip_code': org['shipping_zip_code'],
            'start_date_1': str(datetime.today().date() - timedelta(days=3)),
            'start_date_2': str(datetime.today().date()),

        }
        task_manager.add_task('gettnship_shipments:queue', task)
