# db_base.py
from scrapy import Item
from dateutil import parser


class BaseItem(Item):
    """基础数据库Item类，定义通用配置属性"""
    # 以下属性需要在子类中具体定义
    TABLE = None  # 表名
    AUTO_CREATE_TABLE = False  # 是否自动创建表
    ADD_AUTO_INCREMENT_ID = False  # 是否添加自增主键
    INDEXES = []  # # 普通索引字段列表，如 ["field1", "field2"]
    UNIQUE_CONSTRAINTS = []  # 联合唯一约束，格式：[["f1","f2"], {"name": "...", "fields": [...]}]

    def get_field_type(self, field_name):
        """获取字段声明的类型"""
        return self.fields[field_name].get('type')

    def get_field_comment(self, field_name):
        """获取字段注释"""
        return self.fields[field_name].get('comment', '')

