import json
from datetime import datetime, timedelta

import httpx
import scrapy
from playwright.async_api import Page

from sf_spider.actions.httpx_actions import HttpxAction
from sf_spider.actions.playwright_actions import PlaywrightActions
from sf_spider.base_spider import BaseSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from gettnship.items.shipments import GettnshipShipmentsItem


class GettnshipShipmentsSpider(BaseSpider, PlaywrightActions, HttpxAction):
    name = "gettnship_shipments"  # 爬虫名
    redis_key = "gettnship_shipments:queue"  # 监听的Redis队列键名

    custom_settings = dict(
        # 并发请求数
        CONCURRENT_REQUESTS=15,
        # 每个域名的并发请求数
        CONCURRENT_REQUESTS_PER_DOMAIN=5,
        # 下载延迟（秒）
        DOWNLOAD_DELAY=0,
        ITEM_PIPELINES={
            # 使用批量处理功能的Pipeline
            'gettnship.pipelines.GettnshipBatchPipeline': 300,
        }
    )

    def __init__(self, *args, **kwargs):
        BaseSpider.__init__(self, *args, **kwargs)
        HttpxAction.__init__(self, *args, **kwargs)

    def debug_task(self):
        task = {
            'batch_id': int(int(datetime.now().strftime('%Y%m%d%H%M')) / 10),
            'config_key': 'gettnship_user_money',
            'carrier': 'ups-v2',

            'zip_code': '34109',
            'start_date_1': str(datetime.today().date() - timedelta(days=3)),
            'start_date_2': str(datetime.today().date()),
        }
        return task

    def start_task(self, task:dict):
        meta = dict(
            task=task,
        )
        self.client.auth = httpx.BasicAuth('sf_spider', 'q1515311352.')
        user = self.get_config(task['config_key'])
        if task.get('carrier') == 'ups-v2':
            yield scrapy.Request(
                url=f'https://www.gettnship.com/ajax-pool-synchronized-shipments?carrier=ups-v2&searchby=zip_code&shipped_from={task['start_date_1']}&shipped_to={task['start_date_2']}&shipped_from2=0&shipFromCountry=us&shipFromState=ANY&showPreshipment=0&zip={task["zip_code"]}',
                method='GET',
                meta=meta,
                cookies=user.get('cookies', []),
                headers={
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                },
                callback=self.parse,
                # dont_filter=True,  # 开启不过滤
            )
        elif task.get('carrier') == 'usps':
            yield scrapy.Request(
                url=f'https://www.gettnship.com/ajax-pool-synchronized-shipments?carrier=usps&searchby=zip_code&shipped_from=2025-09-19&shipped_to=2025-09-20&shipped_from2=0&shipFromCountry=us&shipFromState=ANY&showPreshipment=0&zip=32404',
                meta=meta,
                callback=self.parse,
                dont_filter=False,  # 不过滤重复请求
            )
        else:
            raise ValueError(f'不支持的carrier: {task.get("carrier")}')

    async def parse(self, response):
        task = response.meta['task']
        data = json.loads(response.text)
        shipments = data.get('data', {}).get('data', [])
        for shipment in shipments:
            shipment.update(
                zip_code=task['zip_code'],
                batch_id=task['batch_id'],
            )
            yield GettnshipShipmentsItem(**shipment)


if __name__ == '__main__':
    settings = get_project_settings()
    # settings.update(dict(
    #     DEBUG=True,
    # ))
    process = CrawlerProcess(settings)
    process.crawl(GettnshipShipmentsSpider)
    process.start()
