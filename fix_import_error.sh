#!/bin/bash

# 修复sf_spider模块导入错误的脚本
# 这个脚本设置正确的PYTHONPATH，确保Python能找到sf_spider模块

# 获取当前脚本所在目录的父目录（项目根目录）
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

# 设置PYTHONPATH环境变量，包含项目根目录
# 这样Python就能找到sf_spider模块
PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
export PYTHONPATH

# 显示当前设置的PYTHONPATH，用于调试
echo "PYTHONPATH设置为: $PYTHONPATH"

# 提供使用说明
cat << EOF

使用方法:

1. 确保脚本有执行权限:
   chmod +x fix_import_error.sh

2. 运行爬虫前先source这个脚本:
   source fix_import_error.sh
   然后再运行爬虫命令

3. 或者直接使用这个脚本来运行爬虫:
   ./fix_import_error.sh python -m scrapy crawl gettnship_shipments -s DEBUG=True

EOF

# 如果有额外参数，则执行这些参数（比如直接运行爬虫命令）
if [ $# -gt 0 ]; then
    echo "执行命令: $@"
    exec "$@"
fi