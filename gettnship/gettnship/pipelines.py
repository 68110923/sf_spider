# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from sf_spider.pipelines import UniversalPostgreSQLPipeline


class GettnshipLoginPipeline(UniversalPostgreSQLPipeline):
    BATCH_SIZE = 1  # 批量插入大小


class GettnshipBatchPipeline(UniversalPostgreSQLPipeline):
    BATCH_SIZE = 100  # 批量插入大小
