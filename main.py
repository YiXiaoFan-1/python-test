import sys
import os

# 将当前目录添加到系统路径，确保能找到 legacy_projects 包
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from legacy_projects.mobile_click import AutoClickerApp
except ImportError:
    # 如果直接导入失败，尝试作为普通脚本运行时的路径处理
    from mobile_click import AutoClickerApp

if __name__ == '__main__':
    AutoClickerApp().run()
