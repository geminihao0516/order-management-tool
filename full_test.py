#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整測試：轉換 + 展開
"""
import re
from order_formatter import OrderFormatter

def convert_desktop_version(order_data):
    """桌面版的轉換邏輯"""
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

        is_item_line = bool(re.search(r'[xX×*]\s*\d+', line))

        if is_item_line and current_order:
            has_wish = any('願望' in item or '愿望' in item for item in current_order)
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

    return '\n'.join(converted_orders)

def convert_web_version(order_data):
    """網頁版的轉換邏輯"""
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

        is_item_line = bool(re.search(r'[xX×*]\s*\d+', line))

        if is_item_line and current_order:
            if len(current_order) >= 2:
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

    return '\n'.join(converted_orders)

# 讀取測試資料
with open('/Users/hao/Desktop/訂單整理工具/input_data.txt', 'r', encoding='utf-8') as f:
    test_data = f.read()

print("=" * 60)
print("完整測試：轉換 + 展開")
print("=" * 60)

# 桌面版
desktop_converted = convert_desktop_version(test_data)
formatter_desktop = OrderFormatter()
formatter_desktop.load_data(desktop_converted)
desktop_details_count = len(formatter_desktop.expanded_orders)

# 網頁版
web_converted = convert_web_version(test_data)
formatter_web = OrderFormatter()
formatter_web.load_data(web_converted)
web_details_count = len(formatter_web.expanded_orders)

print(f"\n桌面版：")
print(f"  訂單數：{len(formatter_desktop.orders)}")
print(f"  明細數（展開後）：{desktop_details_count}")

print(f"\n網頁版：")
print(f"  訂單數：{len(formatter_web.orders)}")
print(f"  明細數（展開後）：{web_details_count}")

print(f"\n差異：")
print(f"  訂單數差異：{abs(len(formatter_desktop.orders) - len(formatter_web.orders))}")
print(f"  明細數差異：{abs(desktop_details_count - web_details_count)}")

# 如果有差異，輸出轉換結果
if desktop_details_count != web_details_count:
    print("\n=== 桌面版轉換結果 ===")
    print(desktop_converted)
    print("\n=== 網頁版轉換結果 ===")
    print(web_converted)
