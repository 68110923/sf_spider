import json
import time
from datetime import datetime

import httpx
import scrapy
from playwright.async_api import Page

from sf_spider.actions.httpx_actions import HttpxAction
from sf_spider.actions.playwright_actions import PlaywrightActions
from sf_spider.base_spider import BaseSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from gettnship.items.login import GettnshipLoginItem


class GettnshipLoginSpider(BaseSpider, PlaywrightActions, HttpxAction):
    name = "gettnship_login"  # 爬虫名
    redis_key = "gettnship_login:queue"  # 监听的Redis队列键名

    custom_settings = dict(
        ITEM_PIPELINES={
            'gettnship.pipelines.GettnshipLoginPipeline': 300,
        },
        # 并发请求数
        CONCURRENT_REQUESTS=1,
        # 每个域名的并发请求数
        CONCURRENT_REQUESTS_PER_DOMAIN=1,
        # 下载延迟（秒）
        DOWNLOAD_DELAY=1,
    )

    def __init__(self, *args, **kwargs):
        BaseSpider.__init__(self, *args, **kwargs)
        HttpxAction.__init__(self, *args, **kwargs)

    def debug_task(self):
        task = {
            "redis_key": "gettnship_login:queue",
            "config_key": "gettnship_user_money",
            "batch_id": int(time.time()),
        }
        return task

    def start_task(self, task):
        meta = dict(
            task=task,
            playwright=True,    # 启用 Playwright 下载器
            playwright_include_page=True,   # 包含 Playwright 页面对象
            playwright_context_args=dict(
                init_scripts=[],
            ),
            playwright_page_methods=[],   # 定义 Playwright 页面对象的方法,可以写登录逻辑
        )
        yield scrapy.Request(
            url='https://www.gettnship.com/home',
            meta=meta,
            callback=self.parse,
            dont_filter=True, # 不过滤重复请求
        )

    async def parse(self, response):
        task = response.meta['task']
        page = response.meta['playwright_page']
        try:
            page: Page
            self.client_async.auth = httpx.BasicAuth('sf_spider', 'q1515311352.')
            user = await self.async_get_config(task['config_key'])
            self.logger.debug(f'开始注入,{str(datetime.now())}')
            await self.bypass_anti_scraping(page)
            self.logger.debug(f'注入完成,{str(datetime.now())}')
            if user.get('cookies'):
                self.logger.info("尝试使用保存的cookies登录")
                await page.context.add_cookies(user['cookies'])
                await page.reload(wait_until='networkidle')
            login_success_xpath = '.gts-user-email'
            status = await self.wait(page, login_success_xpath, timeout=1000 * 1)
            if not status:
                self.logger.info("cookies不可用，尝试账号登录")
                await page.fill('#email', user['username'])
                await page.fill('#password', user['password'])
                await page.click('#submitBtn')
                status = await self.wait(page, login_success_xpath, timeout=1000 * 20)
            if not status:
                raise ValueError(f'登陆失败')
            # 登录成功，保存cookies
            self.logger.debug('登陆成功')
            all_cookie = await page.context.cookies()

            # 过滤掉不需要的cookie，只保留重要的cookie
            cookies = []
            for cookie in all_cookie:
                # 排除临时会话cookie（名称类似N5tBhma9nPBKuhe6eu4DTacUmWkHKvD07z8XhAAz这种长随机字符串）
                if len(cookie['name']) < 30 or cookie['name'] in ['session', 'auth', 'token', 'remember']:
                    cookies.append(cookie)

            self.logger.debug(f'过滤前cookie数量: {len(all_cookie)}, 过滤后cookie数量: {len(cookies)}')

            user['cookies'] = cookies
            user['cookies_update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 更新用户配置
            await self.async_update_config(config_key=task['config_key'], value=user)

            # 输出结果
            user['cookies'] = json.dumps(user['cookies'], ensure_ascii=False, indent=2)
            yield GettnshipLoginItem(**user)
        except Exception as e:
            raise ValueError(f'登录失败: {e}')
        finally:
            self.logger.error(f'关闭浏览器,{str(datetime.now())}')
            await page.context.browser.close()

if __name__ == '__main__':
    settings = get_project_settings()
    # settings.update(dict(
    #     DEBUG=True,
    # ))
    process = CrawlerProcess(settings)
    process.crawl(GettnshipLoginSpider)
    process.start()
