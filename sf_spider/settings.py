# 并发请求数
CONCURRENT_REQUESTS = 4
# 每个域名的并发请求数
CONCURRENT_REQUESTS_PER_DOMAIN = 2
# 下载延迟（秒）
DOWNLOAD_DELAY = 1
# 调试模式
DEBUG = False

# 1. 替换调度器：使用 Scrapy-Redis 分布式调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 2. 替换去重器：使用 Redis 集合存储去重指纹
# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
DUPEFILTER_CLASS = "sf_spider.dupefilters.JSONTaskDupeFilter"

# 3. Redis 连接配置（根据你的 Redis 服务器修改）
REDIS_URL = 'redis://:000578@43.138.130.198:6379/0'
REDIS_HOST = '43.138.130.198'   # Redis 主机地址（分布式部署时填 Redis 服务器 IP）
REDIS_PORT = 6379           # Redis 端口
REDIS_DB = 0                # Redis 数据库编号（默认 0）
REDIS_PASSWORD = "000578"  # 如有密码，取消注释并填写

# PostgreSQL配置
POSTGRESQL_HOST = '43.138.130.198'  # PostgreSQL主机地址
POSTGRESQL_PORT = 5432        # PostgreSQL端口
POSTGRESQL_DATABASE = 'sf_erp'  # 数据库名
POSTGRESQL_USER = 'postgres'  # 用户名
POSTGRESQL_PASSWORD = '000578'  # 密码，需要替换为实际密码

# 4. 可选：任务队列空时不停止爬虫（持续监听新任务）
SCHEDULER_IDLE_BEFORE_CLOSE = 0  # 0 表示永不关闭

# 5. 可选：批量从 Redis 获取任务（减少 Redis 访问压力）
SCHEDULER_BATCH_SIZE = 5    # 每次取 5 条任务

# 6. 可选：将爬取结果存入 PostgreSQL（需启用对应管道）
ITEM_PIPELINES = {
    # 'scrapy_redis.pipelines.RedisPipeline': 300,  # 结果存入 Redis 列表
    'sf_spider.pipelines.UniversalPostgreSQLPipeline': 300,
}

# 启用 Playwright 下载处理器
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
PLAYWRIGHT_BROWSER_TYPE = "chromium"  # 使用的浏览器（chromium/firefox/webkit）
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,  # 本地调试时设为 False 显示浏览器窗口，生产环境设为 True 无头模式
    "args": ["--start-maximized"],  # 浏览器启动参数（如最大化窗口）
}