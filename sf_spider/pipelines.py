import psycopg2
import psycopg2.extras
from datetime import datetime
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings


class UniversalPostgreSQLPipeline:
    # 配置常量
    BATCH_SIZE = 100  # 批量插入大小
    batch_data = {}   # 按表名存储批量数据: {table_name: [data1, data2...]}

    # Python类型到PostgreSQL类型的映射（支持长度限制）
    TYPE_MAPPING = {
        str: lambda max_len: f"varchar({max_len})" if max_len else "text",
        int: "integer",
        float: "numeric",
        bool: "boolean",
        list: lambda max_len: f"jsonb",
        dict: lambda max_len: f"jsonb",
        datetime: "timestamp with time zone",
        type(None): None  # None值应映射为None，这样在数据库中会存储为NULL而不是字符串'None'
    }

    def __init__(self):
        """初始化Pipeline，设置数据库连接配置"""
        self.settings = get_project_settings()
        self.conn = None  # 数据库连接对象
        self.cur = None   # 数据库游标对象

    def open_spider(self, spider):
        """爬虫启动时建立数据库连接"""
        try:
            # 连接数据库，使用settings中的配置
            self.conn = psycopg2.connect(
                host=self.settings.get('POSTGRESQL_HOST', 'localhost'),
                port=self.settings.get('POSTGRESQL_PORT', 5432),
                dbname=self.settings.get('POSTGRESQL_DATABASE'),
                user=self.settings.get('POSTGRESQL_USER'),
                password=self.settings.get('POSTGRESQL_PASSWORD'),
                options=f"-c search_path={self.settings.get('POSTGRESQL_SCHEMA', 'public')}"
            )
            # 使用DictCursor便于通过字段名访问数据
            self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            spider.logger.info("PostgreSQL连接成功")
        except Exception as e:
            spider.logger.error(f"PostgreSQL连接失败: {str(e)}")
            raise

    def process_item(self, item, spider):
        """处理单个Item，验证字段并加入批量队列"""
        # 检查Item是否实现了必要的数据库配置接口
        if not self._is_valid_database_item(item):
            spider.logger.debug("跳过未实现数据库配置接口的Item")
            return item

        # 验证表名配置
        table_name = item.TABLE
        if not table_name:
            raise DropItem("Item的TABLE属性未配置")

        # 验证字段约束（类型、长度、必填项）
        try:
            item_dict = self._validate_item_fields(item)
        except ValueError as e:
            raise DropItem(f"字段验证失败: {str(e)}")

        if not item_dict:
            raise DropItem("Item没有有效字段")

        # 根据Item配置处理表结构
        if item.AUTO_CREATE_TABLE:
            self._ensure_table_structure(item, item_dict, spider)

        # 缓存数据到批量队列
        self._cache_batch_data(table_name, item_dict)

        return item

    def _is_valid_database_item(self, item):
        """检查Item是否实现了必要的数据库配置属性"""
        required_attrs = ['TABLE', 'AUTO_CREATE_TABLE', 'ADD_AUTO_INCREMENT_ID', 'INDEXES', 'UNIQUE_CONSTRAINTS']
        return all(hasattr(item, attr) for attr in required_attrs)

    def _validate_item_fields(self, item):
        """验证Item字段的类型、长度和必填项"""
        validated_data = {}

        for field_name in item.fields:
            field = item.fields[field_name]
            value = item.get(field_name)

            # 处理默认值和必填项
            if value is None:
                if field.get('required', False):
                    raise ValueError(f"字段 {field_name} 为必填项")
                # 应用默认值
                if 'default' in field:
                    value = field['default']
                elif 'default_factory' in field:
                    value = field['default_factory']()
                else:
                    continue  # 非必填且无默认值，跳过

            # 验证并尝试转换类型
            expected_type = field.get('type')
            if expected_type and not isinstance(value, expected_type):
                # 首先检查是否有自定义的解析函数
                parser_func = field.get('parser_func')
                if parser_func and isinstance(value, str):
                    try:
                        value = parser_func(value)
                        # 验证解析后的值是否为预期类型
                        if not isinstance(value, expected_type):
                            raise ValueError(f"解析后的值类型应为{expected_type.__name__}，实际为{type(value).__name__}")
                    except Exception as e:
                        raise ValueError(f"字段 {field_name} 解析失败: {str(e)}")
                else:
                    # 尝试直接类型转换
                    try:
                        value = expected_type(value)
                    except (ValueError, TypeError):
                        raise ValueError(
                            f"字段 {field_name} 类型错误，预期 {expected_type.__name__}，实际 {type(value).__name__}"
                        )

            # 验证长度限制
            max_length = field.get('max_length')
            if max_length:
                if isinstance(value, (str, list, dict)) and len(value) > max_length:
                    raise ValueError(
                        f"字段 {field_name} {'长度' if isinstance(value, str) else '元素数量'}超过限制，最大 {max_length}，实际 {len(value)}"
                    )

            validated_data[field_name] = value

        return validated_data

    def _get_pg_type(self, item, field_name, value):
        """根据字段定义获取PostgreSQL类型（支持长度限制）"""
        field = item.fields.get(field_name, {})
        field_type = field.get('type', type(value))
        max_length = field.get('max_length')

        # 获取类型映射器
        type_mapper = self.TYPE_MAPPING.get(field_type, 'text')  # 默认使用text类型

        # 处理带长度参数的类型
        if callable(type_mapper):
            pg_type = type_mapper(max_length)
            # 替换占位符为字段名（用于CHECK约束）
            if '{}' in pg_type:
                pg_type = pg_type.format(field_name)
            return pg_type
        return type_mapper

    def _ensure_table_structure(self, item, item_dict, spider):
        """确保表结构完整（表、字段、索引、约束）"""
        table_name = item.TABLE
        try:
            # 检查表是否存在
            self.cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table_name,))
            table_exists = self.cur.fetchone()[0]

            # 表不存在则创建
            if not table_exists:
                self._create_table(item, item_dict, spider)
            else:
                # 表存在则添加缺失字段
                self._add_missing_fields(item, table_name, item_dict, spider)

            # 处理索引和约束
            self._create_indexes_and_constraints(item, spider)

        except Exception as e:
            self.conn.rollback()
            spider.logger.error(f"表结构处理失败: {str(e)}")

    def _create_table(self, item, item_dict, spider):
        """创建新表（包含字段长度约束）"""
        table_name = item.TABLE
        columns_def = []
        comments = []

        # 构建字段定义和收集注释
        for field_name in item_dict:
            value = item_dict[field_name]
            pg_type = self._get_pg_type(item, field_name, value)
            columns_def.append(f"{field_name} {pg_type}")
            
            # 收集字段注释
            comment = item.fields[field_name].get('comment', '')
            if comment:
                comments.append((field_name, comment.replace("'", "''")))

        # 添加自增主键
        if item.ADD_AUTO_INCREMENT_ID:
            columns_def.append("id SERIAL PRIMARY KEY")

        columns_def.reverse()
        # 创建表
        create_sql = f"CREATE TABLE {table_name} ({', '.join(columns_def)})"
        self.cur.execute(create_sql)
        
        # 添加字段注释
        for field_name, comment in comments:
            comment_sql = f"COMMENT ON COLUMN {table_name}.{field_name} IS '{comment}'"
            self.cur.execute(comment_sql)
            
        self.conn.commit()
        spider.logger.info(f"已创建表: {table_name}")

    def _add_missing_fields(self, item, table_name, item_dict, spider):
        """添加表中缺失的字段"""
        # 获取现有字段
        self.cur.execute(f"""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = %s
        """, (table_name,))
        existing_fields = [row[0] for row in self.cur.fetchall()]

        # 添加缺失字段
        for field_name in item_dict:
            if field_name not in existing_fields:
                value = item_dict[field_name]
                pg_type = self._get_pg_type(item, field_name, value)
                comment = item.fields[field_name].get('comment', '')
                
                # 添加字段
                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {field_name} {pg_type}"
                self.cur.execute(alter_sql)
                
                # 添加注释
                if comment:
                    comment_sql = f"COMMENT ON COLUMN {table_name}.{field_name} IS '{comment}'"
                    self.cur.execute(comment_sql)
                    
                self.conn.commit()
                spider.logger.info(f"表 {table_name} 已添加字段: {field_name}")

    def _create_indexes_and_constraints(self, item, spider):
        """创建索引和联合唯一约束"""
        table_name = item.TABLE

        # 创建普通索引
        for field in item.INDEXES:
            index_name = f"idx_{table_name}_{field}"
            self.cur.execute(f"""
                SELECT EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = %s AND tablename = %s
                )
            """, (index_name, table_name))
            if not self.cur.fetchone()[0]:
                self.cur.execute(f"CREATE INDEX {index_name} ON {table_name} ({field})")
                self.conn.commit()
                spider.logger.info(f"已创建索引: {index_name}")

        # 创建联合唯一约束
        for constraint in item.UNIQUE_CONSTRAINTS:
            # 处理约束配置
            if isinstance(constraint, list):
                fields = constraint
                constraint_name = f"uk_{table_name}_{'_'.join(fields)}"
            elif isinstance(constraint, dict):
                fields = constraint["fields"]
                constraint_name = constraint["name"]
            else:
                spider.logger.warning(f"无效的约束配置: {constraint}")
                continue

            # 检查约束是否已存在
            self.cur.execute(f"""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.table_constraints 
                    WHERE constraint_name = %s AND table_name = %s
                )
            """, (constraint_name, table_name))
            if not self.cur.fetchone()[0]:
                fields_str = ", ".join(fields)
                self.cur.execute(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} UNIQUE ({fields_str})")
                self.conn.commit()
                spider.logger.info(f"已创建联合唯一约束: {constraint_name}")

    def _cache_batch_data(self, table_name, item_dict):
        """缓存批量数据并在达到阈值时插入"""
        # 初始化表的批量数据列表
        if table_name not in self.batch_data:
            self.batch_data[table_name] = []
        
        # 添加数据到批量队列
        self.batch_data[table_name].append(item_dict)

        # 达到批次大小时执行插入
        if len(self.batch_data[table_name]) >= self.BATCH_SIZE:
            self._batch_insert(table_name)

    def _batch_insert(self, table_name):
        """执行批量插入操作"""
        if not self.batch_data[table_name]:
            return

        try:
            data_list = self.batch_data[table_name]
            fields = data_list[0].keys()
            field_names = ", ".join(fields)
            placeholders = ", ".join([f"%({k})s" for k in fields])

            # 执行批量插入
            query = f"INSERT INTO {table_name} ({field_names}) VALUES ({placeholders})"
            psycopg2.extras.execute_batch(self.cur, query, data_list)
            self.conn.commit()
            
            # 清理批量数据
            self.batch_data[table_name] = []
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"批量插入失败: {str(e)}")

    def close_spider(self, spider):
        """关闭爬虫时提交剩余数据并关闭数据库连接"""
        # 提交所有剩余的批量数据
        for table_name in self.batch_data:
            if self.batch_data[table_name]:
                try:
                    self._batch_insert(table_name)
                    spider.logger.info(f"爬虫结束，提交剩余数据: {table_name} {len(self.batch_data[table_name])}条")
                except Exception as e:
                    spider.logger.error(f"剩余数据提交失败: {str(e)}")

        # 关闭数据库连接
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()