#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試轉換多行格式的差異
"""
import re

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

    print(f"桌面版：解析出 {len(orders)} 筆訂單")
    return orders

def convert_web_version(order_data):
    """網頁版的轉換邏輯（當前版本）"""
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

    print(f"網頁版：解析出 {len(orders)} 筆訂單")
    return orders

# 讀取測試資料
try:
    with open('/Users/hao/Desktop/訂單整理工具/範例資料.txt', 'r', encoding='utf-8') as f:
        test_data = f.read()

    print("=" * 60)
    print("測試資料轉換比對")
    print("=" * 60)

    desktop_orders = convert_desktop_version(test_data)
    web_orders = convert_web_version(test_data)

    print("\n差異分析：")
    print(f"桌面版訂單數：{len(desktop_orders)}")
    print(f"網頁版訂單數：{len(web_orders)}")
    print(f"差異：{len(desktop_orders) - len(web_orders)} 筆")

    # 找出差異的訂單
    if len(desktop_orders) != len(web_orders):
        print("\n遺漏的訂單：")
        for i, order in enumerate(desktop_orders):
            if i >= len(web_orders) or order != web_orders[i]:
                print(f"\n訂單 {i+1}:")
                for line in order:
                    print(f"  {line}")

except FileNotFoundError:
    print("找不到範例資料.txt 檔案")
