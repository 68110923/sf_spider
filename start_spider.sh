#!/bin/bash

# 爬虫启动脚本

# 设置项目路径
export PROJECT_PATH="$(cd "$(dirname "$0")" && pwd)"

# 设置PYTHONPATH环境变量，确保Python能找到sf_spider模块
export PYTHONPATH="$PROJECT_PATH:$PYTHONPATH"

# 激活虚拟环境
source $PROJECT_PATH/.venv/bin/activate

case "$1" in
  start)
    echo "启动爬虫..."
    cd $PROJECT_PATH/gettnship
    scrapy crawl gettnship_shipments -s DEBUG=False
    ;;
  stop)
    echo "停止爬虫..."
    pkill -f "scrapy crawl gettnship_shipments"
    ;;
  restart)
    echo "重启爬虫..."
    $0 stop
    sleep 2
    $0 start
    ;;
  status)
    echo "爬虫状态..."
    ps aux | grep -v grep | grep "scrapy crawl gettnship_shipments"
    if [ $? -eq 0 ]; then
      echo "爬虫正在运行"
    else
      echo "爬虫未运行"
    fi
    ;;
  *)
    echo "用法: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac

exit 0