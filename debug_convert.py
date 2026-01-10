#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細調試轉換過程
"""
import re

def convert_with_debug(order_data, version_name):
    """帶調試輸出的轉換邏輯"""
    lines = order_data.split('\n')

    orders = []
    current_order = []
    skipped_orders = []  # 記錄被跳過的訂單

    print(f"\n{'='*60}")
    print(f"{version_name} - 開始解析")
    print(f"{'='*60}")
    print(f"總行數: {len(lines)}")

    for i, line in enumerate(lines):
        line = line.strip()

        if not line:
            if current_order:
                filtered_order = [item for item in current_order if item]
                if filtered_order:
                    orders.append(filtered_order)
                    print(f"第 {i} 行：空行，保存訂單 #{len(orders)}")
                current_order = []
            continue

        is_item_line = bool(re.search(r'[xX×*]\s*\d+', line))

        if is_item_line and current_order:
            # 這裡是關鍵：當遇到新品項行時，如何處理前一個訂單
            has_wish = any('願望' in item or '愿望' in item for item in current_order)

            if version_name == "桌面版":
                # 桌面版：只有有願望才保存
                if has_wish:
                    filtered_order = [item for item in current_order if item]
                    if filtered_order:
                        orders.append(filtered_order)
                        print(f"第 {i} 行：新品項行，保存前一訂單 #{len(orders)} (有願望)")
                    current_order = []
                else:
                    print(f"第 {i} 行：新品項行，跳過前一訂單 (無願望)")
                    skipped_orders.append(current_order.copy())
                    current_order = []
            else:
                # 網頁版：只要有2行以上就保存
                if len(current_order) >= 2:
                    filtered_order = [item for item in current_order if item]
                    if filtered_order:
                        orders.append(filtered_order)
                        print(f"第 {i} 行：新品項行，保存前一訂單 #{len(orders)} (>= 2行)")
                    current_order = []

        current_order.append(line)

    # 處理最後一筆訂單
    if current_order:
        filtered_order = [item for item in current_order if item]
        if filtered_order:
            orders.append(filtered_order)
            print(f"結尾：保存最後一筆訂單 #{len(orders)}")

    print(f"\n{version_name} 結果：")
    print(f"  成功解析：{len(orders)} 筆訂單")
    print(f"  跳過：{len(skipped_orders)} 筆訂單")

    if skipped_orders:
        print(f"\n被跳過的訂單：")
        for idx, order in enumerate(skipped_orders):
            print(f"  跳過 #{idx+1}:")
            for line in order:
                print(f"    {line}")

    return orders

# 提示用戶
print("請將您的多行格式資料貼到 input_data.txt 檔案中")
print("然後重新執行此腳本")

try:
    with open('/Users/hao/Desktop/訂單整理工具/input_data.txt', 'r', encoding='utf-8') as f:
        test_data = f.read()

    desktop_orders = convert_with_debug(test_data, "桌面版")
    web_orders = convert_with_debug(test_data, "網頁版")

    print(f"\n{'='*60}")
    print("比對結果")
    print(f"{'='*60}")
    print(f"桌面版：{len(desktop_orders)} 筆")
    print(f"網頁版：{len(web_orders)} 筆")
    print(f"差異：{abs(len(desktop_orders) - len(web_orders))} 筆")

except FileNotFoundError:
    print("\n請建立 input_data.txt 檔案，並貼上您的測試資料")
