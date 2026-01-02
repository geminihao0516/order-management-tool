#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
訂單資料整理與版面設計工具
功能：自動展開品項、統計、比對、生成A4雙欄列印表格
"""

import re
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Tuple


class OrderFormatter:
    # 價目表
    PRICE_LIST = {
        '大鬼鎖心': 220,
        '雙色直立燕通': 300,
        '徐柱老人': 300,
        '孔雀王祈願蠟燭': 120,
        '藥師佛': 350,
        '象神': 260,
        '拆散': 250,
        '拉胡': 260,
        '三色蠟燭': 450,
        '財神爺': 300,
        '大鬼頭': 260,
        '三鬼頭': 300,
        '超大鬼頭': 380,
        '燕通': 300,
        '招財女神': 300,
        '人緣鳥': 260,
        '水龍': 350,
        '二哥豐': 300,
        '愛神': 300,
        '懲罰': 300,
        '巴拉迪燕通': 300,
        '行走佛': 300,
        '依霸': 300,
        '直立大鬼': 290,
        '鬼王': 250,
        '帕猜佛蠟燭': 450,
        '紅眼帕嬰': 280
    }

    def __init__(self):
        self.orders = []
        self.expanded_orders = []
        self.item_stats = defaultdict(int)
        self.item_amounts = defaultdict(int)  # 新增：各品項總金額
        self.anomalies = []

    def parse_order(self, parts: List[str], index: int) -> Dict:
        """解析單筆訂單資料"""
        # 預期格式：品項、姓名/生日、對象/生日、願望
        if len(parts) < 2:
            return None

        order = {
            'index': index,
            'raw_items': parts[0] if len(parts) > 0 else '',
            'main_person': parts[1] if len(parts) > 1 else '',
            'target_person': parts[2] if len(parts) > 2 else '—',
            'wish': parts[3] if len(parts) > 3 else ''
        }

        return order

    def extract_items(self, items_str: str) -> List[Tuple[str, int]]:
        """
        從品項字串中提取品項名稱和數量
        支援多種格式：
        - 品項x3 或 品項 x 3
        - 品項*3 或 品項 * 3
        - 品項 3（純空格分隔）
        例如："鬼王x2+三鬼頭x4" -> [('鬼王', 2), ('三鬼頭', 4)]
        """
        items = []

        # 分割多個品項（用+或、或，分隔）
        item_parts = re.split(r'[+、,，]', items_str)

        for part in item_parts:
            part = part.strip()
            if not part:
                continue

            # 方法1：優先匹配帶符號的格式 "品項名稱[xX×*]N"
            match = re.search(r'(.+?)\s*[xX×*]\s*(\d+)', part)
            if match:
                item_name = match.group(1).strip()
                quantity = int(match.group(2))
                items.append((item_name, quantity))
                continue

            # 方法2：匹配純空格分隔格式 "品項名稱 N"
            # 限制：數字必須是1-3位（避免把日期等當成數量）
            match = re.search(r'(.+?)\s+(\d{1,3})$', part)
            if match:
                item_name = match.group(1).strip()
                quantity = int(match.group(2))
                # 額外檢查：品項名稱不能為空，數量要合理（1-999）
                if item_name and 1 <= quantity <= 999:
                    items.append((item_name, quantity))
                    continue

            # 如果以上都沒匹配到，預設為數量1
            items.append((part, 1))

        return items

    def check_duplicate_items(self, items: List[Tuple[str, int]]) -> List[str]:
        """檢查同一訂單中是否有重複品項"""
        item_counts = defaultdict(int)
        for item_name, _ in items:
            item_counts[item_name] += 1

        duplicates = [name for name, count in item_counts.items() if count > 1]
        return duplicates

    def expand_orders(self):
        """將訂單按品項數量展開成明細"""
        expanded_index = 1

        for order in self.orders:
            items = self.extract_items(order['raw_items'])

            # 檢查異常（重複品項）
            duplicates = self.check_duplicate_items(items)
            if duplicates:
                item_total = {}
                for item_name, qty in items:
                    if item_name in item_total:
                        item_total[item_name] += qty
                    else:
                        item_total[item_name] = qty

                self.anomalies.append({
                    'original_index': order['index'],
                    'items': order['raw_items'],
                    'main_person': order['main_person'],
                    'target_person': order['target_person'],
                    'duplicates': duplicates,
                    'item_totals': item_total
                })

            # 展開每個品項
            for item_name, quantity in items:
                # 統計品項總數
                self.item_stats[item_name] += quantity

                # 計算金額（從價目表中查詢）
                price = self.PRICE_LIST.get(item_name, 0)
                self.item_amounts[item_name] += price * quantity

                # 為每個數量創建一筆明細
                for _ in range(quantity):
                    expanded = {
                        'index': expanded_index,
                        'item': item_name,
                        'price': price,
                        'main_person': order['main_person'],
                        'target_person': order['target_person'],
                        'wish': order['wish']
                    }
                    self.expanded_orders.append(expanded)
                    expanded_index += 1

    def load_data(self, data_text: str):
        """載入訂單資料（支援多行格式和容錯處理）"""
        lines = data_text.strip().split('\n')

        i = 0
        order_index = 1

        while i < len(lines):
            line = lines[i].strip()

            # 跳過空行
            if not line:
                i += 1
                continue

            # 首先嘗試用 Tab 分隔
            parts = [p.strip() for p in line.split('\t') if p.strip()]

            # 情況1：如果 Tab 分隔後只有 1 個欄位，可能是空格分隔或多行訂單的開始
            if len(parts) == 1:
                first_part = parts[0]

                # 跳過單獨的願望行（可能是上個訂單的遺漏部分）
                if first_part.startswith('願望') or first_part.startswith('愿望'):
                    i += 1
                    continue

                # 嘗試用空格分隔品項和姓名/生日
                # 期望格式：品項 姓名 生日
                space_parts = first_part.split()
                if len(space_parts) >= 2:
                    # 重組：第一部分是品項，第二、三部分組成姓名/生日
                    if len(space_parts) >= 3:
                        parts = [space_parts[0], ' '.join(space_parts[1:])]
                    else:
                        parts = space_parts[:2]

                # 嘗試從後續行補充資料
                j = i + 1
                while len(parts) < 4 and j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line:
                        j += 1
                        continue

                    # 如果下一行以願望開頭，添加後結束
                    if next_line.startswith('願望') or next_line.startswith('愿望'):
                        parts.append(next_line)
                        i = j  # 更新主索引
                        break

                    # 如果下一行包含日期格式（/），很可能是對象/生日
                    if '/' in next_line and len(parts) < 3:
                        parts.append(next_line)
                        i = j
                        j += 1
                    else:
                        # 其他情況也嘗試添加
                        parts.append(next_line)
                        i = j
                        j += 1

            # 情況2：Tab 分隔正常，但可能欄位不足
            elif len(parts) < 4:
                # 嘗試從後續行補充資料
                j = i + 1
                while len(parts) < 4 and j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line:
                        break

                    # 檢查是否是新訂單的開始（包含品項格式）
                    if re.search(r'[xX×*]\d+', next_line) or '\t' in next_line:
                        # 這是新訂單，不要合併
                        break

                    parts.append(next_line)
                    i = j
                    j += 1

            # 解析訂單
            order = self.parse_order(parts, order_index)
            if order:
                self.orders.append(order)
                order_index += 1

            i += 1

        # 自動展開訂單
        self.expand_orders()

    def generate_dual_column_table(self) -> str:
        """生成訂單明細表（單欄格式，方便複製）"""
        result = []
        result.append("# 📋 訂單明細表\n")
        result.append("**使用說明**：直接複製以下內容即可\n")
        result.append("---\n")

        # 單欄格式輸出
        for order in self.expanded_orders:
            result.append(f"{order['index']}")
            result.append(f"{order['item']}")
            result.append(f"{order['main_person']}")
            result.append(f"{order['target_person']}")
            result.append(f"{order['wish']}")
            result.append("")  # 空行分隔每筆訂單

        return '\n'.join(result)

    def generate_plain_details(self) -> str:
        """生成純明細內容（不含標題，方便直接複製）"""
        result = []

        # 橫向格式輸出，用 Tab 分隔，編號和品項分開
        for order in self.expanded_orders:
            line = f"{order['index']}\t{order['item']}\t{order['main_person']}\t{order['target_person']}\t{order['wish']}"
            result.append(line)

        return '\n'.join(result)

    def generate_statistics(self) -> str:
        """生成品項統計表"""
        result = []
        result.append("\n# 📊 品項統計總表\n")
        result.append("| 品項名稱 | 數量 | 單價 | 小計金額 |")
        result.append("|----------|------|------|----------|")

        # 按品項名稱排序
        sorted_items = sorted(self.item_stats.items(), key=lambda x: x[0])

        total_quantity = 0
        total_amount = 0
        for item_name, quantity in sorted_items:
            price = self.PRICE_LIST.get(item_name, 0)
            amount = self.item_amounts.get(item_name, 0)
            result.append(f"| {item_name} | {quantity} | ${price} | ${amount} |")
            total_quantity += quantity
            total_amount += amount

        result.append(f"| **總計** | **{total_quantity}** | - | **${total_amount}** |")

        return '\n'.join(result)

    def generate_plain_statistics(self) -> str:
        """生成純品項統計內容（Tab分隔格式，方便複製到Excel）"""
        result = []

        # 按品項名稱排序
        sorted_items = sorted(self.item_stats.items(), key=lambda x: x[0])

        total_quantity = 0
        total_amount = 0
        for item_name, quantity in sorted_items:
            price = self.PRICE_LIST.get(item_name, 0)
            amount = self.item_amounts.get(item_name, 0)
            result.append(f"{item_name}\t{quantity}\t${price}\t${amount}")
            total_quantity += quantity
            total_amount += amount

        result.append(f"總計\t{total_quantity}\t-\t${total_amount}")

        return '\n'.join(result)

    def compare_with_reference(self, reference_data: str) -> str:
        """與參考數據比對"""
        result = []
        result.append("\n# 🔍 數量差異比對表\n")

        # 解析參考數據
        reference = {}

        # 支援換行或逗號分隔
        parts = re.split(r'[\n、,，]', reference_data)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # 嘗試匹配「品項+x+數量」格式（例如：三鬼頭x121 或 三鬼頭 x 121）
            match = re.search(r'^(.+?)\s*[xX×*]\s*(\d+)$', part)
            if match:
                item_name = match.group(1).strip()
                quantity = int(match.group(2))
                reference[item_name] = quantity
                continue

            # 嘗試匹配「數量+支+品項」格式（例如：87支鬼王）
            match = re.search(r'^(\d+)\s*支\s*(.+)$', part)
            if match:
                quantity = int(match.group(1))
                item_name = match.group(2).strip()
                reference[item_name] = quantity
                continue

            # 嘗試匹配「品項+數量+支」格式（例如：鬼王 87 支）
            match = re.search(r'^(.+?)\s*(\d+)\s*支?$', part)
            if match:
                item_name = match.group(1).strip()
                quantity = int(match.group(2))
                reference[item_name] = quantity
                continue

        result.append("| 品項名稱 | 系統統計 | 參考數據 | 差異 | 狀態 |")
        result.append("|----------|----------|----------|------|------|")

        # 比對所有品項
        all_items = set(self.item_stats.keys()) | set(reference.keys())

        has_difference = False
        for item_name in sorted(all_items):
            system_qty = self.item_stats.get(item_name, 0)
            ref_qty = reference.get(item_name, 0)
            diff = system_qty - ref_qty
            status = "✅ 相符" if diff == 0 else "⚠️ 不符"

            if diff != 0:
                has_difference = True

            diff_str = f"+{diff}" if diff > 0 else str(diff)
            result.append(f"| {item_name} | {system_qty} | {ref_qty} | {diff_str} | {status} |")

        if not has_difference:
            result.append("\n**✅ 所有品項數量完全相符！**")
        else:
            result.append("\n**⚠️ 發現數量差異，請檢查！**")

        return '\n'.join(result)

    def generate_anomaly_report(self) -> str:
        """生成異常訂單報告"""
        if not self.anomalies:
            return "\n# ✅ 異常訂單檢測\n\n**未發現異常訂單！**\n"

        result = []
        result.append("\n# ⚠️ 異常訂單明細\n")
        result.append(f"**共發現 {len(self.anomalies)} 筆異常訂單**\n")
        result.append("| 編號 | 品項 | 主要人物 | 對象 | 問題說明 | 各品項數量 |")
        result.append("|------|------|----------|------|----------|------------|")

        for anomaly in self.anomalies:
            duplicates_str = '、'.join(anomaly['duplicates'])
            totals_str = '、'.join([f"{name}×{qty}" for name, qty in anomaly['item_totals'].items()])
            problem = f"重複品項：{duplicates_str}"

            result.append(f"| {anomaly['original_index']} | {anomaly['items']} | {anomaly['main_person']} | {anomaly['target_person']} | {problem} | {totals_str} |")

        return '\n'.join(result)

    def generate_summary(self) -> str:
        """生成報表摘要"""
        result = []
        result.append("\n# 📈 報表摘要\n")
        result.append(f"- **生成時間**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        result.append(f"- **總訂單數**：{len(self.orders)} 筆")
        result.append(f"- **總品項數**（展開後）：{len(self.expanded_orders)} 支")
        result.append(f"- **品項種類數**：{len(self.item_stats)} 種")

        # 計算總金額
        total_amount = sum(self.item_amounts.values())
        result.append(f"- **總金額**：${total_amount}")

        result.append(f"- **異常訂單數**：{len(self.anomalies)} 筆")

        return '\n'.join(result)

    def generate_full_report(self, reference_data: str = None) -> str:
        """生成完整報表"""
        report_parts = []

        # 1. 摘要
        report_parts.append(self.generate_summary())

        # 2. 雙欄明細表
        report_parts.append("\n---\n")
        report_parts.append(self.generate_dual_column_table())

        # 3. 統計表
        report_parts.append("\n---\n")
        report_parts.append(self.generate_statistics())

        # 4. 差異比對（如果有參考數據）
        if reference_data:
            report_parts.append("\n---\n")
            report_parts.append(self.compare_with_reference(reference_data))

        # 5. 異常訂單
        report_parts.append("\n---\n")
        report_parts.append(self.generate_anomaly_report())

        return '\n'.join(report_parts)


def main():
    """主程式"""
    print("=" * 60)
    print("📋 訂單資料整理與版面設計工具")
    print("=" * 60)
    print()

    formatter = OrderFormatter()

    # 輸入訂單資料
    print("請貼上訂單資料（每行格式：品項<TAB>姓名/生日<TAB>對象/生日<TAB>願望）")
    print("貼完後輸入空行並按 Ctrl+D (Mac/Linux) 或 Ctrl+Z (Windows) 結束輸入：")
    print("-" * 60)

    lines = []
    try:
        while True:
            line = input()
            if line:
                lines.append(line)
            else:
                # 空行時詢問是否結束
                confirm = input("輸入空行，是否結束輸入？(y/n): ")
                if confirm.lower() == 'y':
                    break
    except EOFError:
        pass

    order_data = '\n'.join(lines)

    if not order_data.strip():
        print("\n❌ 未輸入任何資料！")
        return

    # 載入資料
    formatter.load_data(order_data)
    print(f"\n✅ 已載入 {len(formatter.orders)} 筆訂單，展開為 {len(formatter.expanded_orders)} 筆明細")

    # 是否需要比對參考數據
    print("\n" + "-" * 60)
    print("是否需要與參考數據比對？(y/n): ", end='')
    need_compare = input().strip().lower() == 'y'

    reference_data = None
    if need_compare:
        print("\n請輸入參考數據（格式：鬼王 87 支、三鬼頭 101 支...）：")
        reference_data = input().strip()

    # 生成報表
    print("\n" + "=" * 60)
    print("生成報表中...")
    print("=" * 60)

    report = formatter.generate_full_report(reference_data)
    print(report)

    # 儲存報表
    print("\n" + "-" * 60)
    print("是否要將報表儲存為檔案？(y/n): ", end='')
    need_save = input().strip().lower() == 'y'

    if need_save:
        filename = f"訂單報表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✅ 報表已儲存為：{filename}")

    print("\n" + "=" * 60)
    print("✅ 處理完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
