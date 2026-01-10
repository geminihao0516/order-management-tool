#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接測試 app.py 中的轉換函數
"""
import sys
sys.path.insert(0, '/Users/hao/Desktop/訂單整理工具')

# 讀取並執行 app.py 中的轉換函數
import re

# 從 app.py 複製轉換函數（實際運行的版本）
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
            # 如果 current_order 至少有 2 行（品項 + 至少一個人物/願望），就保存
            if len(current_order) >= 2:
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
        return None

    return '\n'.join(converted_orders)

# 測試
from order_formatter import OrderFormatter

with open('/Users/hao/Desktop/訂單整理工具/input_data.txt', 'r', encoding='utf-8') as f:
    test_data = f.read()

print("測試 app.py 中實際的轉換函數：")
print("=" * 60)

converted = convert_multi_line_format(test_data)

if converted:
    print(f"轉換後訂單數：{len(converted.split(chr(10)))}")

    # 載入到 OrderFormatter 展開
    formatter = OrderFormatter()
    formatter.load_data(converted)

    print(f"展開後明細數：{len(formatter.expanded_orders)}")

    # 輸出前5筆轉換結果
    print("\n前5筆轉換結果：")
    for i, line in enumerate(converted.split('\n')[:5], 1):
        print(f"{i}. {line[:100]}...")
else:
    print("轉換失敗")
