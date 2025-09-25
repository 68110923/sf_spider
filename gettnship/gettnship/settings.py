from sf_spider.settings import *


BOT_NAME = "gettnship"

# 爬虫模块
SPIDER_MODULES = ["gettnship.spiders"]
# 爬虫模块
NEWSPIDER_MODULE = "gettnship.spiders"

ADDONS = {}

# 并发请求数
CONCURRENT_REQUESTS = 18
# 每个域名的并发请求数
CONCURRENT_REQUESTS_PER_DOMAIN = 6
# 下载延迟（秒）
DOWNLOAD_DELAY = 1
