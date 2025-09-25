import json
import hashlib
from scrapy_redis.dupefilter import RFPDupeFilter


class JSONTaskDupeFilter(RFPDupeFilter):
    """
    基于完整JSON任务体的去重过滤器
    适用于从Redis中获取的JSON格式任务
    """

    def request_fingerprint(self, request):
        """
        重写生成指纹的方法：
        1. 从请求的meta中获取原始任务数据
        2. 对完整任务数据进行哈希生成唯一标识
        """
        # 获取原始任务数据（假设任务数据存储在meta的'task'字段中）
        task_data = request.meta.get('task')

        if task_data:
            # 将任务数据转换为排序后的JSON字符串（确保字典顺序不影响去重）
            # sort_keys=True 保证不同顺序的相同键值对被视为相同
            task_str = json.dumps(
                task_data,
                sort_keys=True,
                ensure_ascii=False
            ).encode('utf-8')

            # 对JSON字符串进行MD5哈希，生成唯一指纹
            return hashlib.md5(task_str).hexdigest()
        else:
            # 如果没有任务数据，使用默认的URL指纹生成方式
            return super().request_fingerprint(request)
