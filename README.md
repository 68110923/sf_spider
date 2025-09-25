# 爬虫项目自动化部署方案

本项目使用GitHub Actions和Supervisor实现爬虫的自动化部署和持续运行。

## 环境准备

### 服务器端

1. 安装依赖
   ```bash
   # 安装Python和pip
   sudo apt update
   sudo apt install python3 python3-venv python3-pip -y
   
   # 安装Supervisor
   sudo apt install supervisor -y
   
   # 启动Supervisor服务
   sudo systemctl enable supervisor
   sudo systemctl start supervisor
   
   # 安装git
   sudo apt install git -y
   ```

2. 创建项目目录
   ```bash
   mkdir -p /path/to/your/project
   cd /path/to/your/project
   ```

3. 克隆仓库
   ```bash
   git clone <your-repo-url> .
   ```

### GitHub配置

在GitHub仓库的`Settings > Secrets and variables > Actions`中添加以下Secret变量：

- `SERVER_IP`: 服务器IP地址
- `SERVER_USERNAME`: 服务器用户名
- `SSH_PRIVATE_KEY`: SSH私钥（用于连接服务器）
- `SERVER_PORT`: SSH端口（可选，默认22）
- `PROJECT_PATH`: 项目在服务器上的绝对路径

## 项目结构

```
sf_spider/
├── .github/workflows/deploy.yml  # GitHub Actions工作流配置
├── gettnship/                    # 爬虫项目目录
│   ├── gettnship/                # 爬虫代码
│   ├── scrapy.cfg                # Scrapy配置文件
│   └── requirements.txt          # 项目依赖
├── start_spider.sh               # 爬虫管理脚本
└── README.md                     # 项目说明
```

## 部署流程

1. 推送代码到GitHub仓库的`main`分支或合并PR到`main`分支
2. GitHub Actions会自动触发部署工作流
3. 工作流会通过SSH连接到服务器，执行以下操作：
   - 拉取最新代码
   - 创建并激活虚拟环境
   - 安装项目依赖
   - 安装Playwright浏览器
   - 配置Supervisor
   - 重启爬虫服务

## Supervisor管理

### 检查爬虫状态
```bash
# 使用Supervisor命令检查
sudo supervisorctl status gettnship_spider

# 或使用项目提供的脚本
./start_spider.sh status
```

### 手动管理爬虫
```bash
# 启动爬虫
./start_spider.sh start

# 停止爬虫
./start_spider.sh stop

# 重启爬虫
./start_spider.sh restart
```

### Supervisor配置说明

Supervisor配置文件位于`/etc/supervisor/conf.d/scrapy_spider.conf`，主要配置项：

```ini
[program:gettnship_spider]
directory=/path/to/your/project  # 项目路径
command=/path/to/your/project/.venv/bin/scrapy crawl gettnship_shipments -s DEBUG=False  # 启动命令
autostart=true  # 系统启动时自动启动
autorestart=true  # 进程意外退出时自动重启
startretries=3  # 启动失败时的重试次数
user=username  # 运行用户
redirect_stderr=true  # 错误输出重定向到标准输出
stdout_logfile=/path/to/your/project/logs/spider.log  # 日志文件路径
stdout_logfile_maxbytes=10MB  # 单个日志文件最大大小
stdout_logfile_backups=5  # 保留的旧日志文件数量
```

## 日志管理

爬虫日志存储在项目的`logs/spider.log`文件中，可以使用以下命令查看：

```bash
# 查看最新日志
tail -f logs/spider.log

# 查看完整日志
cat logs/spider.log
```

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
    # ...其他配置
)
```

### 修改数据库和Redis配置

在`gettnship/gettnship/settings.py`文件中修改数据库和Redis连接配置。

## 添加爬虫任务

使用`gettnship/gettnship/tasks/shipments.py`文件添加爬虫任务到Redis队列：

```bash
cd gettnship
python -m gettnship.tasks.shipments
```

## 常见问题解决

1. **连接服务器失败**
   - 检查`SERVER_IP`和`SERVER_PORT`是否正确
   - 确认`SSH_PRIVATE_KEY`是否具有服务器的访问权限
   - 检查服务器的防火墙设置

2. **依赖安装失败**
   - 确保服务器有足够的磁盘空间
   - 检查网络连接是否正常

3. **爬虫启动失败**
   - 检查Redis和数据库连接配置
   - 查看日志文件获取详细错误信息
   - 确认虚拟环境和依赖已正确安装

## 注意事项

1. 定期备份数据库和重要数据
2. 监控服务器资源使用情况
3. 根据实际需求调整爬虫的并发数和延迟时间
4. 如遇大规模爬虫任务，考虑使用分布式爬虫架构