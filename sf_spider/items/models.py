# db_fields.py
from datetime import datetime
import re
from scrapy import Field
from sf_spider.items.items import BaseItem


class ValidationError(Exception):
    """字段验证错误"""
    pass


class BaseField(Field):
    """基础字段类，支持通用约束和验证功能"""
    def __init__(self, required=False, default=None, default_factory=None,
                 type=None, max_length=None, comment="", validators=None, **kwargs):
        super().__init__(**kwargs)
        self['required'] = required
        self['default'] = default
        self['default_factory'] = default_factory
        self['type'] = type
        self['max_length'] = max_length
        self['comment'] = comment
        self['validators'] = validators or []
    
    def validate(self, value):
        """验证字段值是否符合定义的约束"""
        # 检查必填字段
        if self['required'] and value is None:
            raise ValidationError(f"字段值不能为空")
        
        # 允许None值通过（除非是必填字段）
        if value is None:
            return None
        
        # 检查类型约束
        if self['type'] and not isinstance(value, self['type']):
            raise ValidationError(f"字段值类型应为{self['type'].__name__}，实际为{type(value).__name__}")
        
        # 检查最大长度（仅对字符串类型有效）
        if self['max_length'] and isinstance(value, str) and len(value) > self['max_length']:
            raise ValidationError(f"字段值长度不能超过{self['max_length']}个字符")
        
        # 执行自定义验证器
        for validator in self['validators']:
            value = validator(value)
        
        return value


class StringField(BaseField):
    """字符串字段，适用于存储文本数据"""
    def __init__(self, **kwargs):
        super().__init__(type=str, **kwargs)


class IntField(BaseField):
    """整数字段，适用于存储整数数值"""
    def __init__(self, **kwargs):
        super().__init__(type=int, **kwargs)


class IntegerField(IntField):
    pass


class FloatField(BaseField):
    """浮点数字段，适用于存储带有小数的数值"""
    def __init__(self, **kwargs):
        super().__init__(type=float, **kwargs)


class BooleanField(BaseField):
    """布尔值字段，适用于存储真/假值"""
    def __init__(self, **kwargs):
        super().__init__(type=bool, **kwargs)


class DatetimeField(BaseField):
    """日期时间字段，适用于存储日期和时间"""
    def __init__(self, auto_now=False, auto_now_add=False, format=None, parser_func=None, **kwargs):
        default_factory = None
        if auto_now or auto_now_add:
            default_factory = datetime.utcnow
        
        super().__init__(
            type=datetime,
            default_factory=default_factory,
            **kwargs
        )
        
        self['format'] = format
        self['auto_now'] = auto_now
        self['auto_now_add'] = auto_now_add
        self['parser_func'] = parser_func
    
    def validate(self, value):
        """扩展基类验证方法，增加字符串日期时间解析功能"""
        # 如果值为None或已经是日期时间类型，直接调用基类验证
        if value is None or isinstance(value, self['type']):
            return super().validate(value)
        
        # 如果值是字符串并且提供了解析函数，使用解析函数解析
        if isinstance(value, str) and self['parser_func']:
            try:
                parsed_value = self['parser_func'](value)
                # 验证解析后的值是否为预期类型
                if not isinstance(parsed_value, self['type']):
                    raise ValidationError(f"解析后的值类型应为{self['type'].__name__}，实际为{type(parsed_value).__name__}")
                return parsed_value
            except Exception as e:
                raise ValidationError(f"日期时间解析失败: {str(e)}")
        
        # 其他情况调用基类验证（会进行类型检查）
        return super().validate(value)


class ListField(BaseField):
    """列表字段，适用于存储一组有序数据"""
    def __init__(self, item_type=None, **kwargs):
        super().__init__(type=list, **kwargs)
        self['item_type'] = item_type
    
    def validate(self, value):
        """扩展基类验证方法，增加列表项类型验证"""
        value = super().validate(value)
        
        # 如果值为None或没有指定列表项类型，则不需要进一步验证
        if value is None or not self['item_type']:
            return value
        
        # 验证列表中的每个元素类型
        for i, item in enumerate(value):
            if not isinstance(item, self['item_type']):
                raise ValidationError(f"列表项[{i}]类型应为{self['item_type'].__name__}，实际为{type(item).__name__}")
        
        return value


class DictField(BaseField):
    """字典字段，适用于存储键值对数据"""
    def __init__(self, schema=None, **kwargs):
        super().__init__(type=dict, **kwargs)
        self['schema'] = schema  # schema可以是一个字典，定义每个键的预期类型
    
    def validate(self, value):
        """扩展基类验证方法，增加字典键值类型验证"""
        value = super().validate(value)
        
        # 如果值为None或没有指定schema，则不需要进一步验证
        if value is None or not self['schema']:
            return value
        
        # 验证字典中的每个键值对类型
        for key, expected_type in self['schema'].items():
            if key in value and not isinstance(value[key], expected_type):
                raise ValidationError(
                    f"字典键'{key}'的值类型应为{expected_type.__name__}，实际为{type(value[key]).__name__}")
        
        return value


class EmailField(StringField):
    """电子邮件字段，验证字符串是否为有效的电子邮件地址"""
    def __init__(self, **kwargs):
        # 添加电子邮件格式验证器
        validators = kwargs.pop('validators', [])
        validators.append(self._validate_email_format)
        
        super().__init__(validators=validators, **kwargs)
    
    def _validate_email_format(self, value):
        """验证电子邮件格式是否有效"""
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, value):
            raise ValidationError(f"'{value}'不是有效的电子邮件地址")
        return value


class URLField(StringField):
    """URL字段，验证字符串是否为有效的URL地址"""
    def __init__(self, **kwargs):
        # 添加URL格式验证器
        validators = kwargs.pop('validators', [])
        validators.append(self._validate_url_format)
        
        super().__init__(validators=validators, **kwargs)
    
    def _validate_url_format(self, value):
        """验证URL格式是否有效"""
        pattern = r"^(https?://)?(www\\.)?[a-zA-Z0-9-]+(\\.[a-zA-Z0-9-]+)+(/\S*)?$"
        if not re.match(pattern, value):
            raise ValidationError(f"'{value}'不是有效的URL地址")
        return value


class ChoiceField(BaseField):
    """选项字段，验证值是否在指定的选项列表中"""
    def __init__(self, choices=None, **kwargs):
        if choices is None:
            raise ValueError("必须提供选项列表")
        
        # 添加选项验证器
        validators = kwargs.pop('validators', [])
        validators.append(lambda v: self._validate_choice(v, choices))
        
        super().__init__(validators=validators, **kwargs)
        self['choices'] = choices
    
    def _validate_choice(self, value, choices):
        """验证值是否在选项列表中"""
        if value not in choices:
            raise ValidationError(f"值'{value}'不在有效选项列表中: {choices}")
        return value


class LengthField(StringField):
    """长度限制字段，扩展字符串字段以支持最小和最大长度限制"""
    def __init__(self, min_length=None, max_length=None, **kwargs):
        # 添加长度验证器
        validators = kwargs.pop('validators', [])
        validators.append(lambda v: self._validate_length(v, min_length, max_length))
        
        super().__init__(max_length=max_length, validators=validators, **kwargs)
        self['min_length'] = min_length
    
    def _validate_length(self, value, min_length, max_length):
        """验证字符串长度是否在指定范围内"""
        if min_length is not None and len(value) < min_length:
            raise ValidationError(f"字段值长度不能少于{min_length}个字符")
        if max_length is not None and len(value) > max_length:
            raise ValidationError(f"字段值长度不能超过{max_length}个字符")
        return value


class CharField(StringField):
    """字符字段，与StringField功能相同，用于兼容性"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)



class TextField(BaseField):
    """文本字段，适用于存储较长的文本数据"""
    def __init__(self, **kwargs):
        super().__init__(type=str, **kwargs)


class DateField(BaseField):
    """日期字段，适用于存储日期（不包含时间）"""
    def __init__(self, auto_now=False, auto_now_add=False, format=None, parser_func=None, **kwargs):
        from datetime import date
        default_factory = None
        if auto_now or auto_now_add:
            default_factory = date.today
        
        super().__init__(
            type=date,
            default_factory=default_factory,
            **kwargs
        )
        
        self['format'] = format
        self['auto_now'] = auto_now
        self['auto_now_add'] = auto_now_add
        self['parser_func'] = parser_func
    
    def validate(self, value):
        """扩展基类验证方法，增加字符串日期解析功能"""
        # 如果值为None或已经是日期类型，直接调用基类验证
        if value is None or isinstance(value, self['type']):
            return super().validate(value)
        
        # 如果值是字符串并且提供了解析函数，使用解析函数解析
        if isinstance(value, str) and self['parser_func']:
            try:
                parsed_value = self['parser_func'](value)
                # 验证解析后的值是否为预期类型
                if not isinstance(parsed_value, self['type']):
                    raise ValidationError(f"解析后的值类型应为{self['type'].__name__}，实际为{type(parsed_value).__name__}")
                return parsed_value
            except Exception as e:
                raise ValidationError(f"日期解析失败: {str(e)}")
        
        # 其他情况调用基类验证（会进行类型检查）
        return super().validate(value)


# 创建DateTimeField的大写版本作为别名，以保持与其他ORM框架的兼容性
DateTimeField = DatetimeField


# 示例：使用基础类定义具体的Item类
class ExampleModelItem(BaseItem):
    """示例模型Item，展示如何使用字段类定义数据模型"""
    # 表名（必须配置）
    TABLE = 'example_table'

    # 表结构配置
    AUTO_CREATE_TABLE = True  # 是否自动创建表
    ADD_AUTO_INCREMENT_ID = True  # 是否添加自增主键

    # 索引和约束配置
    INDEXES = ['name', 'created_at']  # 普通索引字段
    UNIQUE_CONSTRAINTS = [['unique_id']]  # 唯一约束
    
    # 字段定义
    unique_id = StringField(max_length=100, comment='唯一标识符')
    name = StringField(max_length=200, comment='名称')
    description = StringField(max_length=500, comment='描述', allow_null=True)
    value = FloatField(comment='数值')
    is_active = BooleanField(default=True, comment='是否活跃')
    created_at = DatetimeField(auto_now_add=True, comment='创建时间')
    updated_at = DatetimeField(auto_now=True, comment='更新时间')
    tags = ListField(item_type=str, comment='标签列表')
    metadata = DictField(comment='元数据')
    email = EmailField(comment='电子邮件地址')
    website = URLField(comment='网站URL')
    status = ChoiceField(choices=['active', 'inactive', 'pending'], comment='状态')