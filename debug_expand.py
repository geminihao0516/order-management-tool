#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試展開邏輯差異
"""
from order_formatter import OrderFormatter

# 讀取範例資料
with open('/Users/hao/Desktop/訂單整理工具/範例資料.txt', 'r', encoding='utf-8') as f:
    test_data = f.read()

# 使用 auto_test.py 中的轉換函數
import re

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
        is_item_line = bool(re.search(r'^[^\d]+\s*[xX×*]\s*\d+', line))

        # 如果當前行是品項行，且已經有資料在 current_order 中
        if is_item_line and current_order:
            # 檢查 current_order 是否已經是完整訂單（至少有願望行）
            has_wish = any('願望' in item or '愿望' in item or '祈' in item for item in current_order)
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

        # 找到主要人物（姓名 生日）
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
        return None

    return '\n'.join(converted_orders)

# 轉換
converted = convert_multi_line_format(test_data)
print(f"轉換後訂單數：{len(converted.split(chr(10)))} 筆\n")

# 使用 OrderFormatter 展開
formatter = OrderFormatter()
formatter.load_data(converted)

print(f"展開後明細數：{len(formatter.expanded_orders)} 筆\n")

# 顯示每個品項的數量
from collections import Counter
item_counts = Counter()
for order in formatter.expanded_orders:
    item_counts[order['品項']] += 1

print("各品項明細數量：")
for item, count in sorted(item_counts.items()):
    print(f"  {item}: {count} 筆")
