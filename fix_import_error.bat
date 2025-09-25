@echo off

REM 修复sf_spider模块导入错误的脚本
REM 这个脚本设置正确的PYTHONPATH，确保Python能找到sf_spider模块

REM 获取当前脚本所在目录（项目根目录）
SET PROJECT_ROOT=%~dp0
REM 移除末尾的反斜杠
SET PROJECT_ROOT=%PROJECT_ROOT:~0,-1%

REM 设置PYTHONPATH环境变量，包含项目根目录
REM 这样Python就能找到sf_spider模块
SET PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%

REM 显示当前设置的PYTHONPATH，用于调试
ECHO PYTHONPATH设置为: %PYTHONPATH%

REM 提供使用说明
ECHO.
ECHO 使用方法:
ECHO.
ECHO 1. 直接运行这个脚本设置PYTHONPATH:
ECHO    fix_import_error.bat
ECHO    然后再运行爬虫命令
ECHO.
ECHO 2. 或者使用这个脚本来运行爬虫:
ECHO    fix_import_error.bat run python -m scrapy crawl gettnship_shipments -s DEBUG=True
ECHO.

REM 如果第一个参数是run，则执行后面的命令
IF "%1"=="run" (
    SHIFT
    ECHO 执行命令: %*
    CALL %*
)