#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
訂單資料整理工具 - Streamlit 網頁版
"""

import streamlit as st
from order_formatter import OrderFormatter
from datetime import datetime
import io
import re

# 轉換多行格式為 Tab 分隔格式
def convert_multi_line_format(order_data):
    """轉換多行格式為 Tab 分隔格式"""
    lines = order_data.split('\n')

    # 解析多行格式
    orders = []
    current_order = []

    for i, line in enumerate(lines):
        line = line.strip()

        if not line:
            # 遇到空行表示一筆訂單結束
            if current_order:
                filtered_order = [item for item in current_order if item]
                if filtered_order:
                    orders.append(filtered_order)
                current_order = []
            continue

        # 檢查是否為新訂單的品項行（包含 x數量 或 *數量 格式）
        is_item_line = bool(re.search(r'[xX×*]\s*\d+', line))

        # 如果當前行是品項行，且已經有資料在 current_order 中
        # 表示這是新訂單的開始，需要先保存前一筆訂單
        if is_item_line and current_order:
            # 檢查 current_order 是否已經是完整訂單（至少有願望行）
            has_wish = any('願望' in item or '愿望' in item for item in current_order)
            if has_wish:
                # 保存前一筆訂單
                filtered_order = [item for item in current_order if item]
                if filtered_order:
                    orders.append(filtered_order)
                current_order = []

        # 非空行加入當前訂單
        current_order.append(line)

    # 處理最後一筆訂單
    if current_order:
        filtered_order = [item for item in current_order if item]
        if filtered_order:
            orders.append(filtered_order)

    # 轉換格式
    converted_orders = []

    for order_lines in orders:
        if len(order_lines) < 2:
            continue

        # 第1行：品項
        item = order_lines[0]

        # 找到主要人物（姓名 生日）- 通常是第2行或第3行
        main_person = "—"
        target_person = "—"
        wish = ""

        # 從第二行開始查找
        person_index = 1
        wish_index = -1

        # 查找願望行的位置
        for idx, line in enumerate(order_lines[1:], start=1):
            if '願望' in line or '祈' in line:
                wish_index = idx
                wish = line.replace('願望：', '').replace('願望:', '').strip()
                break

        # 在願望之前的行中找人物資料
        person_lines = order_lines[1:wish_index] if wish_index > 0 else order_lines[1:]

        # 解析人物資料的輔助函數
        def parse_person(person_line):
            """解析人物資料，返回格式化的字符串"""
            # 嘗試匹配 "姓名 生日" 或 "姓名生日" 格式
            # 支援多種日期格式：1988/6/30, 1988.6.30, 1988-6-30
            match = re.match(r'^(.+?)\s*(\d{4}[/\.\-]?\d{1,2}[/\.\-]?\d{1,2})$', person_line)
            if match:
                name = match.group(1).strip()
                birth = match.group(2).replace('/', '.').replace('-', '.')
                return f"{name}/{birth}"
            else:
                # 如果匹配失敗，返回原字符串
                return person_line

        # 解析人物資料
        if len(person_lines) >= 1:
            # 第一個人物（主要人物）
            main_person = parse_person(person_lines[0])

        if len(person_lines) >= 2:
            # 第二個人物（對象）
            target_person = parse_person(person_lines[1])

        # 組合成 Tab 分隔格式
        converted = f"{item}\t{main_person}\t{target_person}\t{wish}"
        converted_orders.append(converted)

    if not converted_orders:
        st.error("❌ 無法解析資料格式！請確認資料是多行格式。")
        return None

    st.success(f"✅ 成功轉換 {len(converted_orders)} 筆訂單！")
    return '\n'.join(converted_orders)

# 設定頁面配置
st.set_page_config(
    page_title="訂單資料整理工具",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂 CSS 樣式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    .stDownloadButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 主標題
st.markdown('<div class="main-header">📋 訂單資料整理工具</div>', unsafe_allow_html=True)
st.markdown("**自動展開品項 • 雙欄排版 • 統計分析 • 差異比對**")
st.divider()

# 側邊欄 - 使用說明
with st.sidebar:
    st.header("📖 使用說明")
    st.markdown("""
    ### 快速開始
    1. 在主畫面輸入或貼上訂單資料
    2. 點擊「🚀 生成報表」
    3. 選擇需要的格式下載或複製

    ### 資料格式
    **方式一：Tab 分隔**
    ```
    品項<Tab>姓名/生日<Tab>對象/生日<Tab>願望
    ```

    **方式二：多行格式**
    ```
    品項x數量
    姓名 生日
    對象 生日
    願望：內容
    ```

    ### 品項格式
    - `鬼王x3` - 單一品項
    - `鬼王x2+三鬼頭x4` - 多個品項

    ### 特色功能
    - ✅ 自動品項展開
    - ✅ 自動統計數量和金額
    - ✅ 支援參考數據比對
    - ✅ 異常訂單檢測
    """)

    st.divider()
    st.info("💡 提示：建議從 Excel 複製貼上，會自動保留 Tab 分隔")

# 主要內容區
tab1, tab2, tab3 = st.tabs(["📝 訂單輸入", "📊 報表結果", "ℹ️ 關於"])

with tab1:
    st.header("訂單資料輸入")

    # 訂單資料輸入
    if 'order_data' not in st.session_state:
        st.session_state.order_data = ""

    order_data = st.text_area(
        "訂單資料：",
        value=st.session_state.order_data,
        height=300,
        placeholder="請貼上訂單資料...\n\n格式：品項<Tab>姓名/生日<Tab>對象/生日<Tab>願望",
        help="支援 Tab 分隔格式或多行格式",
        key="order_input"
    )

    # 更新 session state
    st.session_state.order_data = order_data

    # 轉換多行格式按鈕
    col_convert1, col_convert2, col_convert3 = st.columns([1, 1, 2])
    with col_convert1:
        if st.button("🔄 轉換多行格式", use_container_width=True, help="將多行格式轉換為 Tab 分隔格式"):
            if not order_data.strip():
                st.error("❌ 請先輸入資料！")
            else:
                converted_data = convert_multi_line_format(order_data)
                if converted_data:
                    st.session_state.order_data = converted_data
                    st.rerun()

    # 參考數據輸入
    with st.expander("🔍 參考數據比對（選填）"):
        st.markdown("**格式範例：**")
        st.code("87支鬼王、101支三鬼頭\n或\n鬼王 87 支、三鬼頭 101 支")

        reference_data = st.text_area(
            "參考數據：",
            height=100,
            placeholder="例如：87支鬼王、101支三鬼頭",
            help="用於比對統計數量是否正確"
        )

    # 生成報表按鈕
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("🚀 生成報表", type="primary", use_container_width=True)

# 處理報表生成
if generate_button:
    if not order_data.strip():
        st.error("❌ 請先輸入訂單資料！")
    else:
        try:
            with st.spinner("🔄 處理中..."):
                # 建立 formatter 並載入資料
                formatter = OrderFormatter()
                formatter.load_data(order_data)

                # 檢查是否成功載入
                if len(formatter.orders) == 0:
                    st.error("❌ 無法解析訂單資料！請檢查資料格式。")
                else:
                    # 儲存到 session state
                    st.session_state.formatter = formatter
                    st.session_state.reference_data = reference_data.strip() if reference_data else None

                    # 生成報表
                    st.session_state.full_report = formatter.generate_full_report(st.session_state.reference_data)
                    st.session_state.plain_details = formatter.generate_plain_details()
                    st.session_state.plain_statistics = formatter.generate_plain_statistics()

                    st.success(f"✅ 報表生成成功！共處理 {len(formatter.orders)} 筆訂單，展開為 {len(formatter.expanded_orders)} 筆明細")

                    # 切換到結果頁籤
                    st.info("👉 請切換到「📊 報表結果」頁籤查看")

        except Exception as e:
            st.error(f"❌ 處理失敗：{str(e)}")

with tab2:
    st.header("報表結果")

    if 'formatter' not in st.session_state:
        st.info("👈 請先在「📝 訂單輸入」頁籤輸入資料並生成報表")
    else:
        formatter = st.session_state.formatter

        # 摘要資訊
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 總訂單數", f"{len(formatter.orders)} 筆")
        with col2:
            st.metric("📋 總品項數", f"{len(formatter.expanded_orders)} 支")
        with col3:
            st.metric("🏷️ 品項種類", f"{len(formatter.item_stats)} 種")
        with col4:
            total_amount = sum(formatter.item_amounts.values())
            st.metric("💰 總金額", f"${total_amount}")

        if formatter.anomalies:
            st.warning(f"⚠️ 發現 {len(formatter.anomalies)} 筆異常訂單")

        st.divider()

        # 下載按鈕
        st.subheader("📥 下載報表")

        col1, col2, col3 = st.columns(3)

        with col1:
            # 完整報表下載
            filename = f"訂單報表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            st.download_button(
                label="📄 下載完整報表",
                data=st.session_state.full_report,
                file_name=filename,
                mime="text/markdown",
                use_container_width=True
            )

        with col2:
            # 純明細下載
            st.download_button(
                label="📋 下載純明細（Tab分隔）",
                data=st.session_state.plain_details,
                file_name=f"訂單明細_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True,
                help="橫向格式，適合貼到 Excel"
            )

        with col3:
            # 純統計下載
            st.download_button(
                label="📊 下載品項統計表",
                data=st.session_state.plain_statistics,
                file_name=f"品項統計_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.divider()

        # 顯示報表內容
        st.subheader("📊 報表預覽")

        # 使用 tabs 顯示不同內容
        preview_tab1, preview_tab2, preview_tab3, preview_tab4 = st.tabs([
            "完整報表", "訂單明細", "品項統計", "異常訂單"
        ])

        with preview_tab1:
            st.markdown(st.session_state.full_report)

        with preview_tab2:
            st.text(st.session_state.plain_details)
            st.info("💡 可直接複製貼到 Excel，會自動分欄")

        with preview_tab3:
            st.text(st.session_state.plain_statistics)

        with preview_tab4:
            if formatter.anomalies:
                for anomaly in formatter.anomalies:
                    st.error(f"""
                    **訂單編號：** {anomaly['original_index']}
                    **品項：** {anomaly['items']}
                    **主要人物：** {anomaly['main_person']}
                    **問題：** 重複品項 - {', '.join(anomaly['duplicates'])}
                    **統計：** {', '.join([f"{name}×{qty}" for name, qty in anomaly['item_totals'].items()])}
                    """)
            else:
                st.success("✅ 未發現異常訂單！")

with tab3:
    st.header("關於本工具")

    st.markdown("""
    ### 🎯 功能特色

    - **自動品項展開**：將 `鬼王x3` 自動展開為 3 筆獨立明細
    - **智慧統計**：自動統計各品項數量和金額
    - **格式轉換**：支援多種輸入格式，自動識別
    - **異常檢測**：自動檢測重複品項等異常情況
    - **參考比對**：可與參考數據比對，確認統計正確性
    - **多種輸出**：提供完整報表、純明細、統計表等多種格式

    ### 📋 支援的輸入格式

    #### 格式一：Tab 分隔（推薦）
    ```
    鬼王x2+三鬼頭x4    王小明 1990/5/20    李美麗 1992/8/15    願望：事業順利
    ```

    #### 格式二：多行格式
    ```
    鬼王x2+三鬼頭x4
    王小明 1990/5/20
    李美麗 1992/8/15
    願望：事業順利
    ```

    ### 💡 使用技巧

    1. **從 Excel 複製資料**：直接從 Excel 複製會保留 Tab 分隔，無需手動調整
    2. **品項格式靈活**：支援 `鬼王x3`、`鬼王 x 3`、`鬼王*3` 等多種寫法
    3. **多品項支援**：可用 `+`、`、`、`,` 分隔多個品項
    4. **參考數據比對**：用於驗證統計結果，支援 `87支鬼王` 或 `鬼王 87 支` 格式

    ### 🔧 技術資訊

    - **開發語言**：Python 3
    - **網頁框架**：Streamlit
    - **核心功能**：order_formatter.py

    ### 📝 版本資訊

    - **版本**：v2.0 (網頁版)
    - **更新日期**：2025-12-01

    ---

    💬 如有問題或建議，歡迎透過 GitHub Issues 回報
    """)

# 頁腳
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 1rem;'>
    <p>訂單資料整理工具 v2.0 | 使用 Streamlit 構建</p>
</div>
""", unsafe_allow_html=True)
