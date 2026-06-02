#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
訂單資料整理工具 - Streamlit 網頁版
"""

import streamlit as st
import streamlit.components.v1 as components
from order_formatter import OrderFormatter
from version import APP_RELEASE_DATE, APP_RELEASE_NOTE, APP_VERSION
from datetime import datetime
import re
import html

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
        # 匹配：品項名 + 可選空格 + x/X/×/* + 可選空格 + 數字
        # 必須是行的主要內容，不是生日或其他格式
        is_item_line = bool(re.search(r'^[^\d]+\s*[xX×*]\s*\d+', line))

        # 如果當前行是品項行，且已經有資料在 current_order 中
        # 表示這是新訂單的開始，需要先保存前一筆訂單
        if is_item_line and current_order:
            # 檢查 current_order 是否已經是完整訂單（至少有願望行）
            has_wish = any('願望' in item or '愿望' in item or '祈' in item or '蠟燭' in item for item in current_order)
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

        # 查找願望行的位置（支援「願望」「祈」「蠟燭」等開頭）
        for idx, line in enumerate(order_lines[1:], start=1):
            if '願望' in line or '祈' in line or '蠟燭' in line:
                wish_index = idx
                # 處理願望的第一行
                wish_first = line.replace('願望：', '').replace('願望:', '')
                wish_first = wish_first.replace('蠟燭：', '').replace('蠟燭:', '').strip()
                
                # 收集願望後續的多行內容（直到遇到下一筆訂單的品項行或結束）
                wish_lines = [wish_first]
                for extra_idx in range(idx + 1, len(order_lines)):
                    extra_line = order_lines[extra_idx].strip()
                    # 檢查是否為新訂單的品項行（停止收集）
                    if re.search(r'^[^\d]+\s*[xX×*]\s*\d+', extra_line):
                        break
                    wish_lines.append(extra_line)
                
                wish = ' '.join(wish_lines)
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

    # 調試信息 - 版本標記
    result = '\n'.join(converted_orders)
    st.info(f"🔍 版本 {APP_VERSION} | 解析: {len(orders)} 組 → 轉換: {len(converted_orders)} 筆")
    st.success(f"✅ 成功轉換 {len(converted_orders)} 筆訂單！")

    # 調試：顯示前3筆
    with st.expander("🔍 查看前3筆轉換結果"):
        for i, line in enumerate(result.split('\n')[:3], 1):
            st.code(f"{i}. {line}", language="text")

    return result

# 設定頁面配置
st.set_page_config(
    page_title="訂單資料整理工具",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自訂 CSS 樣式 - 現代設計系統
st.markdown("""
<style>
    /* === 設計系統變數 === */
    :root {
        --color-primary: #667eea;
        --color-primary-dark: #5a67d8;
        --color-secondary: #48bb78;
        --color-accent: #ed8936;
        --color-background: #f7fafc;
        --color-text: #2d3748;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
        --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
        --radius-md: 0.5rem;
        --radius-lg: 1rem;
    }
    
    /* === 主標題 - 漸層動畫 === */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 1.5rem 0;
        animation: fadeInDown 0.6s ease-out;
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* === 副標題 === */
    .subtitle {
        text-align: center;
        color: #718096;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    
    /* === 按鈕樣式 === */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-md);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* === 下載按鈕 === */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    /* === 成功提示框 === */
    .success-box {
        padding: 1rem 1.5rem;
        border-radius: var(--radius-md);
        background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%);
        border-left: 4px solid #48bb78;
        color: #22543d;
        margin: 1rem 0;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* === 資訊提示框 === */
    .info-box {
        padding: 1rem 1.5rem;
        border-radius: var(--radius-md);
        background: linear-gradient(135deg, #bee3f8 0%, #90cdf4 100%);
        border-left: 4px solid #4299e1;
        color: #2a4365;
        margin: 1rem 0;
    }
    
    /* === Tab 樣式 === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-md) var(--radius-md) 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    /* === Metric 卡片 === */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: var(--color-primary);
    }
    
    /* === 文字區域 === */
    .stTextArea textarea {
        border-radius: var(--radius-md);
        border: 2px solid #e2e8f0;
        transition: border-color 0.2s;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--color-primary);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# 主標題
st.markdown(f'<div class="main-header">📋 訂單資料整理工具 {APP_VERSION}</div>', unsafe_allow_html=True)
st.markdown("**自動展開品項 • 雙欄排版 • 統計分析 • 差異比對**")
st.warning(
    f"🔥 新版本 {APP_VERSION} - {APP_RELEASE_NOTE}！"
    " 如果看不到此訊息，請刷新頁面（Ctrl+F5 或 Cmd+Shift+R）"
)
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

    # 顯示轉換成功訊息
    if st.session_state.get('conversion_done', False):
        st.success("✅ 轉換完成！資料已更新到輸入框中，現在可以點擊「📊 生成報表」")
        st.session_state.conversion_done = False

    # 轉換多行格式按鈕
    col_convert1, col_convert2, col_convert3 = st.columns([1, 1, 2])
    with col_convert1:
        if st.button("🔄 轉換多行格式", use_container_width=True, help="將多行格式轉換為 Tab 分隔格式"):
            if not order_data.strip():
                st.error("❌ 請先輸入資料！")
            else:
                converted_data = convert_multi_line_format(order_data)
                if converted_data:
                    # 儲存轉換結果
                    st.session_state.converted_result = converted_data
                else:
                    st.error("❌ 轉換失敗，請檢查資料格式")

    # 顯示轉換結果
    if 'converted_result' in st.session_state and st.session_state.converted_result:
        st.success("✅ 轉換完成！請複製下方結果，貼回上面的輸入框，然後點擊「📊 生成報表」")

        # 一鍵複製按鈕
        import json
        escaped_converted = json.dumps(st.session_state.converted_result)[1:-1]
        copy_converted_html = f"""
        <div style="margin-bottom: 10px;">
            <button onclick="copyConverted()" id="copyConvertedBtn" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                font-size: 15px;
                font-weight: 600;
                cursor: pointer;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                transition: all 0.3s ease;
            ">
                <span style="font-size: 18px;">📋</span>
                一鍵複製轉換結果
            </button>
            <span id="copyConvertedStatus" style="
                margin-left: 15px;
                color: #48bb78;
                font-weight: 600;
                opacity: 0;
                transition: opacity 0.3s ease;
            ">✅ 已複製到剪貼簿！</span>
        </div>
        <style>
            #copyConvertedBtn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
            }}
            #copyConvertedBtn:active {{
                transform: translateY(-1px);
            }}
        </style>
        <script>
            function copyConverted() {{
                const text = "{escaped_converted}";
                navigator.clipboard.writeText(text).then(function() {{
                    const status = document.getElementById('copyConvertedStatus');
                    status.style.opacity = '1';
                    setTimeout(function() {{
                        status.style.opacity = '0';
                    }}, 2500);
                }}, function(err) {{
                    alert('複製失敗：' + err);
                }});
            }}
        </script>
        """
        components.html(copy_converted_html, height=60)

        st.text_area(
            "轉換結果（請複製）：",
            value=st.session_state.converted_result,
            height=200,
            key="converted_output"
        )
        if st.button("🗑️ 清除轉換結果", use_container_width=True):
            del st.session_state.converted_result
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
            st.subheader("📋 訂單明細表")
            st.caption("使用說明：直接複製以下內容即可")
            
            # 使用更安全的轉義方式
            import json
            escaped_content = json.dumps(st.session_state.plain_details)[1:-1]  # 移除首尾引號
            
            copy_button_html = f"""
            <div style="margin-bottom: 15px;">
                <button onclick="copyToClipboard()" id="copyBtn" style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border: none;
                    color: white;
                    padding: 12px 24px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    border-radius: 10px;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                    transition: all 0.3s ease;
                ">
                    <span style="font-size: 20px;">📋</span>
                    一鍵複製全部內容
                </button>
                <span id="copyStatus" style="
                    margin-left: 15px;
                    color: #48bb78;
                    font-weight: 600;
                    opacity: 0;
                    transition: opacity 0.3s ease;
                ">✅ 已複製到剪貼簿！</span>
            </div>
            <style>
                #copyBtn:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
                }}
                #copyBtn:active {{
                    transform: translateY(-1px);
                }}
            </style>
            <script>
                function copyToClipboard() {{
                    const text = "{escaped_content}";
                    navigator.clipboard.writeText(text).then(function() {{
                        const status = document.getElementById('copyStatus');
                        status.style.opacity = '1';
                        setTimeout(function() {{
                            status.style.opacity = '0';
                        }}, 2500);
                    }}, function(err) {{
                        alert('複製失敗：' + err);
                    }});
                }}
            </script>
            """
            components.html(copy_button_html, height=70)
            
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

    st.markdown(f"""
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

    - **版本**：{APP_VERSION} (網頁版)
    - **更新日期**：{APP_RELEASE_DATE}

    ---

    💬 如有問題或建議，歡迎透過 GitHub Issues 回報
    """)

# 頁腳
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 1rem;'>
    <p>訂單資料整理工具 {APP_VERSION} | 使用 Streamlit 構建</p>
</div>
""".format(APP_VERSION=APP_VERSION), unsafe_allow_html=True)
