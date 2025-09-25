# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import datetime

from dateutil import parser

from sf_spider.items.items import BaseItem
from sf_spider.items import models


class GettnshipShipmentsItem(BaseItem):
    # 表名（必须配置）
    TABLE = 'sf_spider_shipment'

    # 表结构配置
    # AUTO_CREATE_TABLE = False  # 是否自动创建表
    # ADD_AUTO_INCREMENT_ID = False  # 是否添加自增主键

    # 索引和约束配置
    # INDEXES = ['label_created', 'expected_delivery', 'carrier']
    # UNIQUE_CONSTRAINTS = [['tracking_number', 'hash_id']]  # 运单号和哈希ID组合唯一
    parser_func_datetime = lambda str_data: parser.parse(str_data) if str_data else None
    parser_func_date = lambda str_data: parser.parse(str_data).date() if str_data else None

    hash_id = models.CharField(max_length=248, unique=True, default='', verbose_name='哈希ID')
    platform = models.CharField(max_length=32, blank=True, null=True, verbose_name='平台')
    carrier = models.CharField(max_length=32, blank=True, null=True, verbose_name='承运商')
    label_created = models.DateTimeField(blank=True, null=True, verbose_name='标签创建时间', parser_func=parser_func_datetime)
    expected_delivery = models.DateField(blank=True, null=True, verbose_name='预计送达时间', parser_func=parser_func_date)
    zip_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='收件人邮编')

    tracking_number_reality = models.CharField(max_length=50, blank=True, null=True, verbose_name='运单号(实际)')
    tracking_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='运单号')
    shipped_date = models.DateTimeField(blank=True, null=True, verbose_name='发货时间', parser_func=parser_func_datetime)
    weight = models.CharField(max_length=50, blank=True, null=True, verbose_name='重量')
    update_date = models.DateTimeField(blank=True, null=True, verbose_name='更新时间', parser_func=parser_func_datetime)
    status_category = models.CharField(max_length=50, blank=True, null=True, verbose_name='物流状态分类')
    status = models.CharField(max_length=50, blank=True, null=True, verbose_name='物流状态')
    origin_state = models.CharField(max_length=50, blank=True, null=True, verbose_name='出发州/省')
    origin_country = models.CharField(max_length=50, blank=True, null=True, verbose_name='出发国家')
    origin_city = models.CharField(max_length=100, blank=True, null=True, verbose_name='出发城市')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')
    destination_state = models.CharField(max_length=50, blank=True, null=True, verbose_name='目的州/省')
    destination_city = models.CharField(max_length=100, blank=True, null=True, verbose_name='目的城市')
    dest_country = models.CharField(max_length=50, blank=True, null=True, verbose_name='目的国家')
    delivery_proof = models.CharField(max_length=255, blank=True, null=True, verbose_name='送达证明')
    class_of_mail_code = models.CharField(max_length=100, blank=True, null=True, verbose_name='邮件类别代码')




