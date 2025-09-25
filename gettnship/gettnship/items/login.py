# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import datetime

from sf_spider.items.items import BaseItem
from sf_spider.items.models import StringField, DateField, TextField


class GettnshipLoginItem(BaseItem):
    # 表名（必须配置）
    TABLE = 'sf_spider_gettnship_login'

    # 表结构配置
    AUTO_CREATE_TABLE = True  # 是否自动创建表
    ADD_AUTO_INCREMENT_ID = True  # 是否添加自增主键

    # 索引和约束配置
    INDEXES = ['cookies_update_time', 'username']
    UNIQUE_CONSTRAINTS = []
    
    # 字段定义
    cookies = TextField(blank=True, null=True,comment='登录后的cookies信息')
    cookies_update_time = StringField(max_length=100,blank=True, null=True, comment='cookies更新时间')
    password = StringField(max_length=100,blank=True, null=True, comment='登录密码')
    username = StringField(max_length=100,blank=True, null=True, comment='登录账号')

