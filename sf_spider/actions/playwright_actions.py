from playwright.async_api import Page
from typing import Union


class PlaywrightActions:
    async def wait(self, page: Page, *args, **kwargs):
        try:
            return await page.wait_for_selector(*args, **kwargs)
        except Exception as e:
            return None

    async def get_csrf_token(self, page: Page):
        """从页面中获取CSRF令牌"""
        try:
            # 尝试从meta标签中获取CSRF令牌
            csrf_token = await page.evaluate("""
                () => {
                    const meta = document.querySelector('meta[name="csrf-token"]');
                    if (meta) return meta.getAttribute('content');

                    // 尝试从cookie中获取CSRF令牌
                    const cookieValue = document.cookie.split(';').find(cookie => 
                        cookie.trim().startsWith('XSRF-TOKEN=') || 
                        cookie.trim().startsWith('csrf-token=') ||
                        cookie.trim().startsWith('CSRF_TOKEN=')
                    );
                    if (cookieValue) {
                        const token = cookieValue.split('=')[1].trim();
                        // 解码URL编码的token
                        try { return decodeURIComponent(token); } catch (e) { return token; }
                    }

                    // 尝试从表单隐藏字段中获取CSRF令牌
                    const formInput = document.querySelector('input[name="_token"], input[name="csrf-token"], input[name="csrf_token"]');
                    if (formInput) return formInput.value;

                    return null;
                }
            """)
            return csrf_token
        except Exception as e:
            print(f"获取CSRF令牌失败: {e}")
            return None

    async def simulate_human_behavior(self, page: Page):
        """模拟人类行为，如随机滚动、移动鼠标等"""
        import random

        # 随机等待一段时间
        await page.wait_for_timeout(random.randint(1000, 3000))

        # 随机滚动页面
        for _ in range(random.randint(1, 3)):
            scroll_height = await page.evaluate("document.body.scrollHeight")
            scroll_to = random.randint(0, scroll_height // 2)
            await page.evaluate(f"window.scrollTo(0, {scroll_to})")
            await page.wait_for_timeout(random.randint(500, 1500))

        # 随机移动鼠标
        await page.mouse.move(random.randint(100, 800), random.randint(100, 600))
        await page.wait_for_timeout(random.randint(300, 800))

    async def bypass_anti_scraping(self, page: Page):
        """执行一系列JS注入来绕过网站的反爬机制"""
        # 1. 覆盖Navigator.webdriver属性
        await page.evaluate("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """)

        # 2. 添加真实浏览器指纹特征
        await page.evaluate("""
        const originalQuery = window.navigator.permissions.query;
        Object.defineProperty(window.navigator.permissions, 'query', {
            value: (parameters) => {
                if (parameters.name === 'notifications') {
                    return Promise.resolve({ state: Notification.permission });
                }
                return originalQuery(parameters);
            }
        });

        // 3. 模拟真实用户的屏幕大小和设备信息
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });

        // 4. 移除自动化控制的痕迹
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en-US', 'en']
        });

        // 5. 防止检测无头浏览器
        Object.defineProperty(navigator, 'plugins', {
            get: () => [{
                name: 'Chrome PDF Plugin',
                filename: 'internal-pdf-viewer',
                description: 'Portable Document Format'
            }]
        });

        // 6. 模拟用户代理的硬件并发
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });

        // 7. 修复电池API模拟
        window.navigator.getBattery = async function() {
            return {
                level: 0.85,
                charging: false,
                chargingTime: Infinity,
                dischargingTime: 3600,
                addEventListener: function() {},
                removeEventListener: function() {}
            };
        };

        // 8. 添加document.referrer
        Object.defineProperty(document, 'referrer', {
            get: () => 'https://www.google.com/'
        });

        // 9. 模拟真实的触摸事件
        if (typeof window.ontouchstart === 'undefined') {
            window.ontouchstart = function() {};
        }
        """)

        # 10. 注入额外的浏览器指纹修改脚本到所有新页面
        await page.context.add_init_script("""
        // 禁用Chrome的自动填充功能
        delete window.chrome;

        // 添加window.scrollBy方法来模拟真实用户滚动
        window.__defineGetter__('scrollY', function() { 
            return document.documentElement.scrollTop; 
        });

        // 模拟真实的window.requestAnimationFrame
        const originalRequestAnimationFrame = window.requestAnimationFrame;
        window.requestAnimationFrame = function(callback) {
            return originalRequestAnimationFrame.call(window, callback);
        };

        // 模拟真实的WebGL指纹
        if (window.WebGLRenderingContext) {
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Mozilla';
                if (parameter === 37446) return 'Mozilla';
                if (parameter === 37447) return 'WebKit';
                return getParameter.apply(this, [parameter]);
            };
        }

        // 11. 处理CSRF令牌相关的安全策略
        Object.defineProperty(document, 'cookie', {
            get: function() {
                return Object.getOwnPropertyDescriptor(Object.getPrototypeOf(document), 'cookie').get.call(this);
            },
            set: function(value) {
                // 确保CSRF令牌cookie被正确设置
                Object.getOwnPropertyDescriptor(Object.getPrototypeOf(document), 'cookie').set.call(this, value);
            }
        });

        // 12. 模拟真实的网络请求超时
        XMLHttpRequest.prototype.send = new Proxy(XMLHttpRequest.prototype.send, {
            apply: function(target, thisArg, args) {
                // 保留原始行为
                return target.apply(thisArg, args);
            }
        });

        // 13. 添加更多的浏览器特征
        Object.defineProperty(navigator, 'vendor', {
            get: () => 'Google Inc.'
        });

        Object.defineProperty(navigator, 'appVersion', {
            get: () => '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
        });

        // 14. 模拟真实的鼠标移动
        if (window.MouseEvent) {
            const originalConstructor = window.MouseEvent;
            window.MouseEvent = function(type, eventInit) {
                // 添加更多真实的鼠标事件属性
                return new originalConstructor(type, eventInit);
            };
            window.MouseEvent.prototype = originalConstructor.prototype;
            window.MouseEvent.__proto__ = originalConstructor;
        }
        """)

        # 15. 启用网络请求监听，捕获并处理CSRF令牌
        await page.route('**', lambda route, request: route.continue_())

        # 16. 等待页面加载完成
        await page.wait_for_load_state('networkidle')

    async def playwright_auto_close(self, page: Page):
        """ 自动关闭多余的页面 """
        all_tabs = page.context.pages
        for tab in all_tabs[:-1]:
            await tab.close()

    @staticmethod
    def get_init_scripts(key: str=None) -> Union[str, dict]:
        """
        返回一组用于绕过网站防爬机制的JavaScript注入代码
        
        返回值:
            dict: 字典，键为功能点描述，值为对应的JavaScript代码字符串
        """
        # 收集所有防反爬JavaScript注入
        anti_bot_js_dict = {
            "修改navigator.webdriver属性（常用的爬虫检测点）": '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            ''',
            
            "修复navigator.permissions.query方法防止权限检测": '''
            const originalQuery = window.navigator.permissions.query;
            Object.defineProperty(window.navigator.permissions, 'query', {
                value: (parameters) => {
                    if (parameters.name === 'notifications') {
                        return Promise.resolve({ state: Notification.permission });
                    }
                    return originalQuery(parameters);
                }
            });
            ''',
            
            "模拟真实设备内存信息": '''
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
            ''',
            
            "设置多语言支持模拟真实用户": '''
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en-US', 'en']
            });
            ''',
            
            "模拟浏览器插件信息防止无头检测": '''
            Object.defineProperty(navigator, 'plugins', {
                get: () => [{
                    name: 'Chrome PDF Plugin',
                    filename: 'internal-pdf-viewer',
                    description: 'Portable Document Format'
                }]
            });
            ''',
            
            "模拟硬件并发核心数": '''
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });
            ''',
            
            "模拟电池API数据": '''
            window.navigator.getBattery = async function() {
                return {
                    level: 0.85,
                    charging: false,
                    chargingTime: Infinity,
                    dischargingTime: 3600,
                    addEventListener: function() {},
                    removeEventListener: function() {}
                };
            };
            ''',
            
            "设置文档来源引用": '''
            Object.defineProperty(document, 'referrer', {
                get: () => 'https://www.google.com/'
            });
            ''',
            
            "模拟触摸事件支持": '''
            if (typeof window.ontouchstart === 'undefined') {
                window.ontouchstart = function() {}
            }
            ''',
            
            "禁用Chrome自动填充功能": '''
            delete window.chrome;
            ''',
            
            "模拟真实滚动行为": '''
            window.__defineGetter__('scrollY', function() { 
                return document.documentElement.scrollTop; 
            });
            ''',
            
            "修复requestAnimationFrame方法": '''
            const originalRequestAnimationFrame = window.requestAnimationFrame;
            window.requestAnimationFrame = function(callback) {
                return originalRequestAnimationFrame.call(window, callback);
            };
            ''',
            
            "修改WebGL指纹特征": '''
            if (window.WebGLRenderingContext) {
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Mozilla';
                    if (parameter === 37446) return 'Mozilla';
                    if (parameter === 37447) return 'WebKit';
                    return getParameter.apply(this, [parameter]);
                };
            }
            ''',
            
            "处理Cookie安全策略": '''
            Object.defineProperty(document, 'cookie', {
                get: function() {
                    return Object.getOwnPropertyDescriptor(Object.getPrototypeOf(document), 'cookie').get.call(this);
                },
                set: function(value) {
                    // 确保CSRF令牌cookie被正确设置
                    Object.getOwnPropertyDescriptor(Object.getPrototypeOf(document), 'cookie').set.call(this, value);
                }
            });
            ''',
            
            "代理XMLHttpRequest.send方法": '''
            XMLHttpRequest.prototype.send = new Proxy(XMLHttpRequest.prototype.send, {
                apply: function(target, thisArg, args) {
                    // 保留原始行为
                    return target.apply(thisArg, args);
                }
            });
            ''',
            
            "设置浏览器厂商信息": '''
            Object.defineProperty(navigator, 'vendor', {
                get: () => 'Google Inc.'
            });
            ''',
            
            "模拟真实浏览器版本信息": '''
            Object.defineProperty(navigator, 'appVersion', {
                get: () => '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
            });
            ''',
            
            "模拟真实鼠标事件构造函数": '''
            if (window.MouseEvent) {
                const originalConstructor = window.MouseEvent;
                window.MouseEvent = function(type, eventInit) {
                    // 添加更多真实的鼠标事件属性
                    return new originalConstructor(type, eventInit);
                };
                window.MouseEvent.prototype = originalConstructor.prototype;
                window.MouseEvent.__proto__ = originalConstructor;
            }
            '''
        }
        if key:
            return anti_bot_js_dict[key]
        else:
            return anti_bot_js_dict
