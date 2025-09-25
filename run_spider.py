#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬虫Python启动脚本

这个脚本使用纯Python实现，避免依赖shell环境，解决服务器无法使用shell脚本的问题。
提供与start_spider.sh相同的功能：start/stop/restart/status
"""

import os
import sys
import time
import subprocess
import signal
import psutil  # 需要安装：pip install psutil


class SpiderManager:
    """爬虫管理器类，提供启动、停止、重启和查看状态功能"""
    
    def __init__(self):
        # 获取项目根路径
        self.project_path = os.path.dirname(os.path.abspath(__file__))
        # 设置PYTHONPATH环境变量，确保能找到sf_spider模块
        os.environ['PYTHONPATH'] = self.project_path + ':' + os.environ.get('PYTHONPATH', '')
        # 虚拟环境Python路径
        self.venv_python = os.path.join(self.project_path, '.venv', 'bin', 'python')
        # 爬虫命令
        self.spider_command = [
            self.venv_python,
            '-m', 'scrapy', 'crawl', 'gettnship_shipments',
            '-s', 'DEBUG=False'
        ]
        # 爬虫工作目录
        self.spider_dir = os.path.join(self.project_path, 'gettnship')
        # 爬虫进程标识
        self.spider_process_name = 'scrapy crawl gettnship_shipments'
        # 日志目录
        self.log_dir = os.path.join(self.project_path, 'logs')
        
    def start(self):
        """启动爬虫"""
        print("启动爬虫...")
        
        # 检查爬虫是否已经在运行
        if self._is_spider_running():
            print("爬虫已经在运行中，无需再次启动。")
            return
        
        # 确保日志目录存在
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            print(f"创建日志目录: {self.log_dir}")
        
        try:
            # 在后台启动爬虫并将输出重定向到日志文件
            log_file = os.path.join(self.log_dir, 'gettnship_shipments.log')
            with open(log_file, 'a', encoding='utf-8') as f:
                # 创建子进程运行爬虫
                subprocess.Popen(
                    self.spider_command,
                    cwd=self.spider_dir,
                    stdout=f,
                    stderr=f,
                    start_new_session=True  # 创建新的会话，确保进程在脚本退出后继续运行
                )
                print(f"爬虫已启动，日志输出到: {log_file}")
                # 短暂等待，确保进程有时间启动
                time.sleep(1)
                # 验证启动是否成功
                if self._is_spider_running():
                    print("爬虫启动成功!")
                else:
                    print("爬虫启动失败，请查看日志文件。")
        except Exception as e:
            print(f"启动爬虫时发生错误: {e}")
    
    def stop(self):
        """停止爬虫"""
        print("停止爬虫...")
        
        # 查找并终止爬虫进程
        spider_pids = self._get_spider_pids()
        
        if not spider_pids:
            print("没有找到运行中的爬虫进程。")
            return
        
        for pid in spider_pids:
            try:
                # 发送终止信号
                os.kill(pid, signal.SIGTERM)
                print(f"已向进程 {pid} 发送终止信号")
            except Exception as e:
                print(f"终止进程 {pid} 时发生错误: {e}")
        
        # 等待进程结束
        time.sleep(2)
        
        # 检查是否还有剩余进程
        remaining_pids = self._get_spider_pids()
        if not remaining_pids:
            print("所有爬虫进程已停止。")
        else:
            print(f"仍有 {len(remaining_pids)} 个爬虫进程未停止: {remaining_pids}")
    
    def restart(self):
        """重启爬虫"""
        print("重启爬虫...")
        self.stop()
        # 等待一段时间确保进程完全停止
        time.sleep(3)
        self.start()
    
    def status(self):
        """查看爬虫状态"""
        print("爬虫状态...")
        
        if self._is_spider_running():
            pids = self._get_spider_pids()
            print(f"爬虫正在运行，进程ID: {pids}")
        else:
            print("爬虫未运行")
    
    def _is_spider_running(self):
        """检查爬虫是否正在运行"""
        return len(self._get_spider_pids()) > 0
    
    def _get_spider_pids(self):
        """获取所有爬虫进程的PID"""
        pids = []
        try:
            # 使用psutil查找包含指定命令的进程
            for proc in psutil.process_iter(['pid', 'cmdline']):
                try:
                    # 检查进程命令行是否包含爬虫命令
                    if self.spider_process_name in ' '.join(proc.info['cmdline']):
                        pids.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            print(f"获取进程列表时发生错误: {e}")
        return pids


def main():
    """主函数，处理命令行参数"""
    manager = SpiderManager()
    
    if len(sys.argv) < 2:
        print("用法: python run_spider.py {start|stop|restart|status}")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'start':
        manager.start()
    elif command == 'stop':
        manager.stop()
    elif command == 'restart':
        manager.restart()
    elif command == 'status':
        manager.status()
    else:
        print(f"未知命令: {command}")
        print("用法: python run_spider.py {start|stop|restart|status}")
        sys.exit(1)


if __name__ == '__main__':
    main()