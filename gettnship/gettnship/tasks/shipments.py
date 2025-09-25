import json
import redis
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
    "shipping_zip_code": "87012"
  },
  {
    "shipping_zip_code": "29591"
  },
  {
    "shipping_zip_code": "34109"
  },
  {
    "shipping_zip_code": "24073"
  },
  {
    "shipping_zip_code": "35170"
  },
  {
    "shipping_zip_code": "38080"
  },
  {
    "shipping_zip_code": "92881"
  },
  {
    "shipping_zip_code": "70543"
  },
  {
    "shipping_zip_code": "92583"
  },
  {
    "shipping_zip_code": "11510"
  },
  {
    "shipping_zip_code": "59500"
  },
  {
    "shipping_zip_code": "20105"
  },
  {
    "shipping_zip_code": "94538"
  },
  {
    "shipping_zip_code": "62919"
  },
  {
    "shipping_zip_code": "13850"
  },
  {
    "shipping_zip_code": "30315"
  },
  {
    "shipping_zip_code": "55414"
  },
  {
    "shipping_zip_code": "34120"
  },
  {
    "shipping_zip_code": "84073"
  },
  {
    "shipping_zip_code": "02090"
  },
  {
    "shipping_zip_code": "76557"
  },
  {
    "shipping_zip_code": "34288"
  },
  {
    "shipping_zip_code": "07631"
  },
  {
    "shipping_zip_code": "77494"
  },
  {
    "shipping_zip_code": "02904"
  },
  {
    "shipping_zip_code": "22554"
  },
  {
    "shipping_zip_code": "54000"
  },
  {
    "shipping_zip_code": "83600"
  }
]
    for org in org_ls:
        task = {
            'spider_name': 'gettnship_shipments',
            'config_key': 'gettnship_user_money',
            'carrier': 'ups-v2',

            'zip_code': org['shipping_zip_code'],
            'start_date_1': str(datetime.today().date() - timedelta(days=3)),
            'start_date_2': str(datetime.today().date()),
            'datetime': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        }
        task_manager.add_task('gettnship_shipments:queue', task)
