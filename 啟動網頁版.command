#!/bin/bash
# 訂單整理工具 - Streamlit 網頁版啟動腳本

# 切換到腳本所在目錄
cd "$(dirname "$0")"

echo "🚀 正在啟動訂單整理工具網頁版..."
echo ""

# 啟動 Streamlit
streamlit run app.py
