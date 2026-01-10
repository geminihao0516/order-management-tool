#!/bin/bash
# 訂單整理工具 - GUI版本啟動腳本

# 切換到腳本所在目錄
cd "$(dirname "$0")"

# 清除 Python 緩存（確保使用最新代碼）
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# 啟動GUI程式
python3 order_formatter_gui.py
