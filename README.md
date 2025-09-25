# 爬虫项目自动化部署方案

# SF Spider - 深孚爬虫自动化部署方案

本项目基于Scrapy框架开发，使用GitHub Actions和Supervisor实现爬虫的自动化部署和持续运行。项目采用分布式架构，通过Scrapy-Redis实现任务队列管理，支持Playwright和Httpx进行数据抓取。

## 环境准备

### 服务器端

**系统信息**：腾讯云 OpenCloudOS
**IP地址**：43.138.130.198
**用户**：root
**密码**：000578

1. 安装依赖
   ```bash
   # 更新系统包
   sudo yum update -y
   
   # 安装Python和pip
   sudo yum install python3 python3-pip -y
   
   # 安装Supervisor进程管理工具
   sudo yum install supervisor -y
   
   # 安装Git版本控制工具
   sudo yum install git -y
   
   # 更新pip到最新版本
   pip install --upgrade pip
   
   # 检查Supervisor是否正确安装并创建配置目录
   sudo mkdir -p /etc/supervisord.d/
   sudo touch /etc/supervisord.conf
   
   # 为OpenCloudOS系统创建Supervisor服务
   sudo tee /etc/systemd/system/supervisord.service << 'EOF'
   [Unit]
   Description=Supervisor process control system for UNIX
   Documentation=http://supervisord.org
   After=network.target
   
   [Service]
   Type=forking
   ExecStart=/usr/bin/supervisord -c /etc/supervisord.conf
   ExecReload=/usr/bin/supervisorctl reload
   ExecStop=/usr/bin/supervisorctl shutdown
   User=root
   
   [Install]
   WantedBy=multi-user.target
   EOF
   
   # 创建基本的Supervisor配置文件
   sudo tee /etc/supervisord.conf << 'EOF'
   [unix_http_server]
   file=/run/supervisord.sock   ; the path to the socket file
   
   [supervisord]
   logfile=/var/log/supervisord.log ; main log file; default $CWD/supervisord.log
   logfile_maxbytes=50MB        ; max main logfile bytes b4 rotation; default 50MB
   logfile_backups=10           ; # of main logfile backups; 0 means none, default 10
   loglevel=info                ; log level; default info; others: debug,warn,trace
   pidfile=/run/supervisord.pid ; supervisord pidfile; default supervisord.pid
   nodaemon=false               ; start in foreground if true; default false
   minfds=1024                  ; min. avail startup file descriptors; default 1024
   minprocs=200                 ; min. avail process descriptors;default 200
   
   [rpcinterface:supervisor]
   supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface
   
   [supervisorctl]
   serverurl=unix:///run/supervisord.sock ; use a unix:// URL  for a unix socket
   
   [include]
   files = /etc/supervisord.d/*.ini
   EOF
   
   # 设置Supervisor开机自启并启动服务
   sudo systemctl daemon-reload
   sudo systemctl enable supervisord
   sudo systemctl start supervisord
   
   # 验证Supervisor服务是否启动成功
   sudo systemctl status supervisord
   ```

2. 创建项目目录
   ```bash
   mkdir -p /opt/sf_spider
   cd /opt/sf_spider
   ```

3. 克隆仓库
   ```bash
   git clone https://github.com/68110923/sf_spider.git .
   ```

### GitHub配置

在GitHub仓库的`Settings > Secrets and variables > Actions`中添加以下Secret变量：

- `SERVER_IP`: 43.138.130.198
- `SERVER_USERNAME`: root
- `SSH_PRIVATE_KEY`: SSH私钥（用于连接服务器）
- `SERVER_PORT`: 22（默认SSH端口）
- `PROJECT_PATH`: /opt/sf_spider

## 项目结构

```
sf_spider/
├── .github/workflows/deploy.yml  # GitHub Actions工作流配置
├── gettnship/                    # 爬虫项目目录
│   ├── gettnship/                # 爬虫核心代码
│   │   ├── spiders/              # 爬虫实现
│   │   │   ├── shipments.py      # 运单信息爬虫
│   │   │   └── login.py          # 登录爬虫
│   │   ├── tasks/                # 任务管理模块
│   │   │   ├── login_add_tasks.py # 登录任务添加
│   │   │   └── shipments.py      # 运单任务管理
│   │   ├── items/                # 数据模型
│   │   ├── pipelines.py          # 数据处理管道
│   │   ├── settings.py           # 项目设置
│   │   ├── middlewares.py        # 中间件配置
│   └── scrapy.cfg                # Scrapy配置文件
├── sf_spider/                    # 项目基础配置和基类
│   ├── __init__.py               # 初始化文件
│   ├── actions/                  # 自定义操作模块
│   │   ├── httpx_actions.py      # Httpx相关操作
│   │   └── playwright_actions.py # Playwright相关操作
│   ├── base_spider.py            # 基础爬虫类
│   ├── dupefilters.py            # 去重过滤器
│   ├── items/                    # 数据模型
│   │   ├── items.py              # 项目数据项定义
│   │   └── models.py             # 数据模型定义
│   ├── middlewares.py            # 中间件
│   ├── pipelines.py              # 数据处理管道
│   └── settings.py               # 项目设置
├── requirements.txt              # 项目依赖
├── start_spider.sh               # 爬虫管理脚本
├── scrapy.cfg                    # 项目级Scrapy配置
└── README.md                     # 项目说明
```

## 部署流程

1. 推送代码到GitHub仓库的`master`分支
2. GitHub Actions会自动触发部署工作流
3. 工作流会通过SSH连接到服务器，执行以下操作：
   - 验证GitHub Secrets配置
   - 拉取最新代码
   - 创建并激活虚拟环境
   - 更新pip版本
   - 安装项目依赖
   - 安装Playwright浏览器
   - 创建日志目录并设置权限
   - 配置Supervisor服务文件
   - 更新Supervisor配置并重启爬虫
   - 检查爬虫运行状态

## Supervisor管理

### 检查爬虫状态
```bash
# 使用Supervisor命令检查
sudo supervisorctl status gettnship_spider

# 或使用项目提供的脚本
cd /opt/sf_spider
./start_spider.sh status
```

### 手动管理爬虫
```bash
cd /opt/sf_spider

# 启动爬虫（通过Supervisor）
sudo supervisorctl start gettnship_spider

# 停止爬虫（通过Supervisor）
sudo supervisorctl stop gettnship_spider

# 重启爬虫（通过Supervisor）
sudo supervisorctl restart gettnship_spider

# 或使用项目脚本直接管理
./start_spider.sh start  # 直接启动（不通过Supervisor）
./start_spider.sh stop   # 直接停止（不通过Supervisor）
./start_spider.sh restart # 直接重启（不通过Supervisor）
```

### Supervisor配置说明

Supervisor配置文件位于`/etc/supervisord.d/scrapy_spider.ini`，主要配置项：

```ini
[program:gettnship_spider]
directory=/opt/sf_spider  # 项目路径
command=/opt/sf_spider/.venv/bin/python -m scrapy crawl gettnship_shipments -s DEBUG=False  # 启动命令
autostart=true  # 系统启动时自动启动
autorestart=true  # 进程意外退出时自动重启
startretries=3  # 启动失败时的重试次数
user=root  # 运行用户
redirect_stderr=true  # 错误输出重定向到标准输出
environment=PYTHONPATH=/opt/sf_spider  # 环境变量设置
stdout_logfile=/opt/sf_spider/logs/spider.log  # 日志文件路径
stdout_logfile_maxbytes=10MB  # 单个日志文件最大大小
stdout_logfile_backups=5  # 保留的旧日志文件数量
```

### 检查爬虫状态
```bash
cd /opt/sf_spider
./start_spider.sh status
```

### 手动管理爬虫
```bash
cd /opt/sf_spider

# 启动爬虫
./start_spider.sh start

# 停止爬虫
./start_spider.sh stop

# 重启爬虫
./start_spider.sh restart
```

## 日志管理

爬虫日志存储在项目的`logs/spider.log`文件中，可以使用以下命令查看：

```bash
# 查看最新日志
tail -f /opt/sf_spider/logs/spider.log

# 查看完整日志
cat /opt/sf_spider/logs/spider.log

# 查看最近100行日志
tail -n 100 /opt/sf_spider/logs/spider.log
```

日志文件会自动滚动，当达到10MB时会创建新的日志文件，最多保留5个备份日志。

## 自定义配置

### 修改爬虫参数

可以在`gettnship/gettnship/spiders/shipments.py`文件中修改爬虫的配置：

```python
custom_settings = dict(
    # 并发请求数
    CONCURRENT_REQUESTS=3,
    # 每个域名的并发请求数
    CONCURRENT_REQUESTS_PER_DOMAIN=1,
    # 下载延迟（秒）
    DOWNLOAD_DELAY=1,
    # Redis队列配置
    REDIS_KEYS_PREFIX='gettnship',
    REDIS_START_URLS_KEY='gettnship:start_urls',
    # ...其他配置
)
```

### 修改数据库和Redis配置

在`gettnship/gettnship/settings.py`文件中修改数据库和Redis连接配置：

```python
# Redis配置
REDIS_HOST = 'localhost'  # Redis主机地址
REDIS_PORT = 6379         # Redis端口
REDIS_DB = 0              # Redis数据库
REDIS_PASSWORD = ''       # Redis密码（如果有）

# 数据库配置（如果使用）
# DATABASE_URL = 'postgresql://user:password@localhost/dbname'

# 爬虫设置
ROBOTSTXT_OBEY = False
COOKIES_ENABLED = True
DOWNLOAD_TIMEOUT = 30
```

### 环境变量配置

可以在Supervisor配置文件中添加环境变量：

```ini
[program:gettnship_spider]
# ...其他配置
environment=PYTHONPATH=/opt/sf_spider,
            REDIS_HOST='localhost',
            REDIS_PORT='6379',
            DEBUG='False'```

## 添加爬虫任务

使用`gettnship/gettnship/tasks/shipments.py`文件添加爬虫任务到Redis队列：

### 方法一：直接运行任务管理脚本
```bash
cd /opt/sf_spider/gettnship
python -m gettnship.tasks.shipments
```

### 方法二：自定义任务参数
您可以修改`shipments.py`文件中的任务参数，或者在外部调用时传递参数。以下是任务管理类的主要方法：

```python
class ShipmentsManager:
    def __init__(self):
        # 初始化Redis连接
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            password=None
        )
        self.redis_key = 'gettnship:start_urls'  # Redis队列键名
    
    def add_task(self, task_data):
        """添加任务到Redis队列"""
        # 将任务数据序列化并添加到队列
        self.redis_client.lpush(self.redis_key, json.dumps(task_data, ensure_ascii=False))
```

### 示例：添加自定义任务
```python
from gettnship.tasks.shipments import ShipmentsManager

# 创建任务管理器实例
manager = ShipmentsManager()

# 准备任务数据
custom_task = {
    'waybill_number': 'SF1234567890123',  # 运单号
    'search_date': '2023-10-15',         # 查询日期
    'priority': 'high'                   # 优先级
}

# 添加任务到队列
manager.add_task(custom_task)```

## 常见问题解决

### 1. GitHub Actions部署失败

**问题**：GitHub Actions工作流执行失败
**解决方案**：
- 检查`SERVER_IP`、`SERVER_USERNAME`和`SSH_PRIVATE_KEY`等GitHub Secrets是否正确配置
- 确认服务器的SSH端口是否开放（默认22）
- 查看GitHub Actions日志获取详细错误信息

### 2. Supervisor管理问题

**问题**：Supervisor无法启动爬虫或爬虫频繁重启
**解决方案**：
- 检查Supervisor配置文件中的项目路径和命令是否正确
- 确认日志文件目录存在且有写入权限：`mkdir -p /opt/sf_spider/logs && chmod 775 /opt/sf_spider/logs`
- 查看Supervisor日志：`cat /var/log/supervisor/supervisord.log`
- 重新加载Supervisor配置：`sudo supervisorctl reread && sudo supervisorctl update`

### 3. 爬虫执行错误

**问题**：爬虫运行但无法正常抓取数据
**解决方案**：
- 检查Redis连接配置是否正确
- 查看爬虫日志：`tail -f /opt/sf_spider/logs/spider.log`
- 确认Playwright浏览器是否正确安装：`cd /opt/sf_spider && .venv/bin/python -m playwright install`
- 检查网络连接和目标网站是否可访问

### 4. 依赖安装问题

**问题**：pip安装依赖时出现错误
**解决方案**：
- 更新pip版本：`pip install --upgrade pip`
- 检查服务器网络连接和PyPI源是否可访问
- 尝试使用国内镜像源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

## 注意事项

1. **数据安全**：定期备份数据库和重要数据，建议使用定时任务自动备份
2. **资源监控**：定期监控服务器CPU、内存和磁盘使用情况，避免资源耗尽
3. **性能调优**：根据服务器配置和网络情况，合理调整爬虫的并发数和延迟时间
4. **分布式扩展**：如遇大规模爬虫任务，可考虑使用Scrapy-Redis分布式架构，多服务器协同工作
5. **版本管理**：所有代码修改应通过git进行版本控制，避免直接在服务器上修改代码
6. **安全防护**：注意保护服务器密码、数据库连接信息和API密钥等敏感信息，避免泄露
7. **日志管理**：定期清理旧日志文件，避免占用过多磁盘空间
8. **错误处理**：实现完善的错误处理机制，确保爬虫遇到异常时能够优雅地处理并记录