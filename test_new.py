#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
獨立測試新版轉換邏輯
"""
import streamlit as st
from order_formatter import OrderFormatter
import re

st.set_page_config(page_title="測試轉換功能", layout="wide")

st.title("🧪 測試：轉換多行格式")

# 轉換函數（最新版本）
def convert_multi_line_format_v2(order_data):
    """轉換多行格式為 Tab 分隔格式 - v2.1"""
    lines = order_data.split('\n')
    orders = []
    current_order = []

    for i, line in enumerate(lines):
        line = line.strip()

        if not line:
            if current_order:
                filtered_order = [item for item in current_order if item]
                if filtered_order:
                    orders.append(filtered_order)
                current_order = []
            continue

        # 品項行識別（支援空格）
        is_item_line = bool(re.search(r'^[^\d]+\s*[xX×*]\s*\d+', line))

        if is_item_line and current_order:
            # 關鍵：使用 has_wish 檢查
            has_wish = any('願望' in item or '愿望' in item or '祈' in item for item in current_order)
            if has_wish:
                filtered_order = [item for item in current_order if item]
                if filtered_order:
                    orders.append(filtered_order)
                current_order = []

        current_order.append(line)

    if current_order:
        filtered_order = [item for item in current_order if item]
        if filtered_order:
            orders.append(filtered_order)

    # 轉換格式
    converted_orders = []
    for order_lines in orders:
        if len(order_lines) < 2:
            continue

        item = order_lines[0]
        main_person = "—"
        target_person = "—"
        wish = ""

        wish_index = -1
        for idx, line in enumerate(order_lines[1:], start=1):
            if '願望' in line or '祈' in line:
                wish_index = idx
                wish = line.replace('願望：', '').replace('願望:', '').strip()
                break

        person_lines = order_lines[1:wish_index] if wish_index > 0 else order_lines[1:]

        def parse_person(person_line):
            match = re.match(r'^(.+?)\s*(\d{4}[/\.\-]?\d{1,2}[/\.\-]?\d{1,2})$', person_line)
            if match:
                name = match.group(1).strip()
                birth = match.group(2).replace('/', '.').replace('-', '.')
                return f"{name}/{birth}"
            else:
                return person_line

        if len(person_lines) >= 1:
            main_person = parse_person(person_lines[0])
        if len(person_lines) >= 2:
            target_person = parse_person(person_lines[1])

        converted = f"{item}\t{main_person}\t{target_person}\t{wish}"
        converted_orders.append(converted)

    if not converted_orders:
        return None, len(orders)

    return '\n'.join(converted_orders), len(orders)

# UI
order_data = st.text_area("貼上訂單資料：", height=300)

if st.button("🔄 測試轉換（v2.1）", type="primary"):
    if not order_data.strip():
        st.error("請先輸入資料")
    else:
        result, orders_count = convert_multi_line_format_v2(order_data)

        if result:
            st.success(f"✅ 成功！解析 {orders_count} 組 → 轉換 {len(result.split(chr(10)))} 筆")

            # 展開統計
            formatter = OrderFormatter()
            formatter.load_data(result)
            expanded_count = len(formatter.expanded_orders)

            st.info(f"📊 展開後明細數：**{expanded_count} 筆**")

            if expanded_count == 194:
                st.balloons()
                st.success("🎉 正確！得到 194 筆明細")
            else:
                st.warning(f"⚠️ 預期 194 筆，實際 {expanded_count} 筆")

            # 顯示前3筆
            with st.expander("查看前3筆轉換結果"):
                for i, line in enumerate(result.split('\n')[:3], 1):
                    st.code(line)
        else:
            st.error("轉換失敗")
