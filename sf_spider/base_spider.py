# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import json

import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy.utils.project import get_project_settings

# 根据开关动态选择父类（RedisSpider或普通Spider）
settings = get_project_settings()
if settings.get("DEBUG"):
    __BaseSpider = scrapy.Spider
else:
    __BaseSpider = RedisSpider


class BaseSpider(__BaseSpider):
    def debug_task(self):
        """调试任务，需要重写"""
        raise NotImplementedError('debug_task方法需要重写')

    def start_task(self, task):
        """开始任务，需要重写"""
        raise NotImplementedError('start_task方法需要重写')

    # 新增：替代start_requests的异步方法start()
    async def start(self):
        """Scrapy 2.13+ 推荐的异步启动方法"""
        if self.settings.get('DEBUG'):
            debug_task = self.debug_task()
            for req in self.start_task(debug_task):
                yield req
        else:
            # 调用父类的start()方法（兼容RedisSpider）
            async for req in super().start():
                yield req

    # 被start()替代的start_requests方法
    # def start_requests(self):
    #     """处理初始请求（适用于本地Spider）"""
    #     if self.settings.get('DEBUG'):
    #         debug_task = self.debug_task()
    #         yield from self.start_task(debug_task)
    #     else:
    #         yield from super().start_requests()

    def make_request_from_data(self, data):
        """处理Redis中的任务（适用于RedisSpider）"""
        task = json.loads(data.decode('utf-8'))
        for req in self.start_task(task):
            yield req
        # yield from self.start_task(task)
