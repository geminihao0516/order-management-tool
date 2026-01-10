#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動測試網頁版轉換功能
"""
import re
from order_formatter import OrderFormatter

# 從 app.py 複製最新的轉換函數
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
print("=" * 80)
print("🧪 自動測試：網頁版轉換功能")
print("=" * 80)

# 讀取範例資料
with open('/Users/hao/Desktop/訂單整理工具/範例資料.txt', 'r', encoding='utf-8') as f:
    test_data = f.read()

print(f"\n📄 輸入資料：範例資料.txt")
print(f"   總行數：{len(test_data.split(chr(10)))}")

# 執行轉換
print(f"\n🔄 執行轉換...")
converted = convert_multi_line_format(test_data)

if converted:
    converted_lines = converted.split('\n')
    print(f"✅ 轉換成功！")
    print(f"   轉換後訂單數：{len(converted_lines)} 筆")

    # 載入到 OrderFormatter 展開
    formatter = OrderFormatter()
    formatter.load_data(converted)

    expanded_count = len(formatter.expanded_orders)
    print(f"   展開後明細數：{expanded_count} 筆")

    # 判斷結果
    print(f"\n" + "=" * 80)
    if expanded_count == 194:
        print("🎉 測試通過！展開後明細數正確：194 筆")
    else:
        print(f"❌ 測試失敗！預期 194 筆，實際 {expanded_count} 筆")
        print(f"   差異：{194 - expanded_count} 筆")
    print("=" * 80)

    # 顯示前 3 筆轉換結果
    print(f"\n📋 前 3 筆轉換結果：")
    for i, line in enumerate(converted_lines[:3], 1):
        parts = line.split('\t')
        print(f"\n{i}. 品項：{parts[0]}")
        print(f"   主要人物：{parts[1] if len(parts) > 1 else '(無)'}")
        print(f"   對象：{parts[2] if len(parts) > 2 else '(無)'}")
        print(f"   願望：{parts[3][:50] if len(parts) > 3 else '(無)'}...")
else:
    print("❌ 轉換失敗")
