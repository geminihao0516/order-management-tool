#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
訂單資料整理工具 - 圖形介面版本
使用 tkinter 建立友善的 GUI 介面
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from datetime import datetime
import os
import re
from order_formatter import OrderFormatter
from version import APP_VERSION


class OrderFormatterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"📋 訂單資料整理工具 {APP_VERSION}")
        self.root.geometry("1200x800")

        # 設定視窗圖示和樣式
        self.setup_style()

        # 建立主要容器
        self.create_widgets()

        # 初始化資料
        self.formatter = None
        self.current_report = ""

    def setup_style(self):
        """設定視覺樣式"""
        style = ttk.Style()
        style.theme_use('default')

        # 自訂按鈕樣式
        style.configure('Primary.TButton', font=('微軟正黑體', 10), padding=10)
        style.configure('Success.TButton', font=('微軟正黑體', 10), padding=10)
        style.configure('Title.TLabel', font=('微軟正黑體', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('微軟正黑體', 10))

    def create_widgets(self):
        """建立所有介面元件"""

        # ===== 標題區 =====
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            title_frame,
            text="📋 訂單資料整理與版面設計工具",
            style='Title.TLabel'
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text=f"{APP_VERSION} • 自動展開品項 • 雙欄排版 • 統計分析 • 差異比對",
            style='Subtitle.TLabel',
            foreground='gray'
        )
        subtitle_label.pack()

        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, pady=5)

        # ===== 主要內容區（使用 PanedWindow 分割） =====
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ----- 左側：輸入區 -----
        left_frame = ttk.Frame(main_paned, padding="5")
        main_paned.add(left_frame, weight=1)

        # 訂單資料輸入區
        order_label_frame = ttk.LabelFrame(left_frame, text="📝 訂單資料輸入", padding="10")
        order_label_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 說明文字框架
        help_frame = ttk.Frame(order_label_frame)
        help_frame.pack(fill=tk.X, pady=(0, 5))

        help_text = ttk.Label(
            help_frame,
            text="⚠️ 格式：品項<Tab>姓名/生日<Tab>對象/生日<Tab>願望\n"
                 "💡 請從 Excel 直接複製，或點擊「貼上範例資料」查看格式",
            foreground='red',
            font=('微軟正黑體', 9, 'bold')
        )
        help_text.pack(side=tk.LEFT, anchor=tk.W)

        # 格式說明按鈕
        format_help_btn = ttk.Button(
            help_frame,
            text="❓ 格式說明",
            command=self.show_format_help
        )
        format_help_btn.pack(side=tk.RIGHT, padx=5)

        # 訂單資料輸入框
        self.order_text = scrolledtext.ScrolledText(
            order_label_frame,
            height=15,
            font=('Consolas', 10),
            wrap=tk.NONE
        )
        self.order_text.pack(fill=tk.BOTH, expand=True)

        # 輸入區按鈕
        order_btn_frame = ttk.Frame(order_label_frame)
        order_btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(
            order_btn_frame,
            text="📋 貼上範例資料",
            command=self.load_example_data,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            order_btn_frame,
            text="🔄 轉換多行格式",
            command=self.convert_multi_line_format,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            order_btn_frame,
            text="🗑️ 清除",
            command=self.clear_order_data
        ).pack(side=tk.LEFT, padx=2)

        # 參考資料輸入區
        ref_label_frame = ttk.LabelFrame(left_frame, text="🔍 參考數據（選填）", padding="10")
        ref_label_frame.pack(fill=tk.X, pady=5)

        ref_help = ttk.Label(
            ref_label_frame,
            text="格式A：87支鬼王、101支三鬼頭（每行一個或用、分隔）\n"
                 "格式B：鬼王 87 支、三鬼頭 101 支（兩種格式都支援）",
            foreground='blue',
            font=('微軟正黑體', 9)
        )
        ref_help.pack(anchor=tk.W, pady=(0, 5))

        self.ref_text = tk.Text(
            ref_label_frame,
            height=3,
            font=('Consolas', 10)
        )
        self.ref_text.pack(fill=tk.X)

        ref_btn_frame = ttk.Frame(ref_label_frame)
        ref_btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(
            ref_btn_frame,
            text="📋 貼上範例參考數據",
            command=self.load_example_reference,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            ref_btn_frame,
            text="🗑️ 清除",
            command=self.clear_reference_data
        ).pack(side=tk.LEFT, padx=2)

        # 主要操作按鈕
        action_frame = ttk.Frame(left_frame, padding="10")
        action_frame.pack(fill=tk.X, pady=10)

        self.generate_btn = ttk.Button(
            action_frame,
            text="🚀 生成報表",
            command=self.generate_report,
            style='Success.TButton'
        )
        self.generate_btn.pack(fill=tk.X)

        # ----- 右側：結果顯示區 -----
        right_frame = ttk.Frame(main_paned, padding="5")
        main_paned.add(right_frame, weight=2)

        # 報表顯示區
        result_label_frame = ttk.LabelFrame(right_frame, text="📊 報表結果", padding="10")
        result_label_frame.pack(fill=tk.BOTH, expand=True)

        # 結果文字框
        self.result_text = scrolledtext.ScrolledText(
            result_label_frame,
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 結果區按鈕
        result_btn_frame = ttk.Frame(result_label_frame)
        result_btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(
            result_btn_frame,
            text="💾 儲存報表",
            command=self.save_report,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            result_btn_frame,
            text="📋 複製完整報表",
            command=self.copy_to_clipboard
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            result_btn_frame,
            text="📄 複製純明細",
            command=self.copy_plain_details,
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            result_btn_frame,
            text="📊 複製純品項統計表",
            command=self.copy_plain_statistics,
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            result_btn_frame,
            text="🗑️ 清除結果",
            command=self.clear_result
        ).pack(side=tk.LEFT, padx=2)

        # ===== 狀態列 =====
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X)

        self.status_label = ttk.Label(
            self.status_frame,
            text="就緒",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_label.pack(fill=tk.X)

    def update_status(self, message):
        """更新狀態列訊息"""
        self.status_label.config(text=f"{datetime.now().strftime('%H:%M:%S')} - {message}")
        self.root.update_idletasks()

    def show_format_help(self):
        """顯示資料格式說明"""
        help_window = tk.Toplevel(self.root)
        help_window.title("📝 資料格式說明")
        help_window.geometry("700x600")

        # 創建捲動文字區
        text_frame = ttk.Frame(help_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)

        help_text = scrolledtext.ScrolledText(
            text_frame,
            font=('微軟正黑體', 10),
            wrap=tk.WORD
        )
        help_text.pack(fill=tk.BOTH, expand=True)

        # 插入說明內容
        help_content = """
📝 訂單資料格式說明

❗ 重要提醒
資料必須使用 Tab 分隔，不是空白鍵！

─────────────────────────────────

✅ 正確格式

格式：品項<Tab>姓名/生日<Tab>對象/生日<Tab>願望

說明：
• <Tab> = 按鍵盤上的 Tab 鍵
• 至少需要前 2 欄（品項、姓名/生日）
• 後面 2 欄是選填

─────────────────────────────────

📊 從 Excel 準備資料（最推薦）

步驟：
1. 在 Excel 建立 4 欄表格
2. 填入資料
3. 選取資料列（不含標題）
4. 按 Ctrl+C (Win) 或 Cmd+C (Mac)
5. 貼到 GUI 輸入框

✅ Excel 會自動使用 Tab 分隔！

─────────────────────────────────

📋 範例資料

單一品項：
愛神x3<Tab>陳大華/1985.12.10<Tab>—<Tab>求好姻緣

多個品項：
鬼王x2+三鬼頭x4<Tab>王小明/1990.05.20<Tab>李美麗/1992.08.15<Tab>事業順利

─────────────────────────────────

🎯 品項格式

✅ 正確：
• 鬼王x3
• 鬼王 x 3（可有空格）
• 鬼王x2+三鬼頭x4（用+連接）
• 鬼王x2、三鬼頭x3（用、連接）

❌ 錯誤：
• 鬼王*3（不能用 *）
• 鬼王 3支（缺少 x）
• 鬼王2+三鬼頭4（缺少 x）

─────────────────────────────────

🐛 遇到問題？

如果顯示「0 筆訂單」：
1. 檢查是否使用 Tab 分隔
2. 點擊「📋 貼上範例資料」查看正確格式
3. 從 Excel 重新複製資料
4. 查看「資料格式說明.md」檔案

─────────────────────────────────

🔍 參考數據格式

支援兩種格式：

格式A（數量在前）：
87支鬼王
101支三鬼頭
24支直立大鬼

格式B（數量在後）：
鬼王 87 支
三鬼頭 101 支

可用換行或逗號（、）分隔

─────────────────────────────────

💡 快速測試

1. 點擊「📋 貼上範例資料」
2. 點擊「🚀 生成報表」
3. 如果成功，你的資料應該用相同格式
        """

        help_text.insert(1.0, help_content)
        help_text.config(state='disabled')  # 設為唯讀

        # 關閉按鈕
        btn_frame = ttk.Frame(help_window, padding="10")
        btn_frame.pack(fill=tk.X)

        ttk.Button(
            btn_frame,
            text="✅ 我知道了",
            command=help_window.destroy,
            style='Primary.TButton'
        ).pack(side=tk.RIGHT)

        # 視窗置中
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (help_window.winfo_width() // 2)
        y = (help_window.winfo_screenheight() // 2) - (help_window.winfo_height() // 2)
        help_window.geometry(f'+{x}+{y}')

    def load_example_data(self):
        """載入範例資料"""
        example_file = os.path.join(os.path.dirname(__file__), '範例資料.txt')

        if os.path.exists(example_file):
            with open(example_file, 'r', encoding='utf-8') as f:
                data = f.read()
            self.order_text.delete(1.0, tk.END)
            self.order_text.insert(1.0, data)
            self.update_status("✅ 已載入範例資料")
        else:
            messagebox.showwarning("提示", "找不到範例資料檔案")

    def load_example_reference(self):
        """載入範例參考數據"""
        example_file = os.path.join(os.path.dirname(__file__), '範例參考數據.txt')

        if os.path.exists(example_file):
            with open(example_file, 'r', encoding='utf-8') as f:
                data = f.read()
            self.ref_text.delete(1.0, tk.END)
            self.ref_text.insert(1.0, data)
            self.update_status("✅ 已載入範例參考數據")
        else:
            messagebox.showwarning("提示", "找不到範例參考數據檔案")

    def clear_order_data(self):
        """清除訂單資料"""
        self.order_text.delete(1.0, tk.END)
        self.update_status("🗑️ 已清除訂單資料")

    def clear_reference_data(self):
        """清除參考數據"""
        self.ref_text.delete(1.0, tk.END)
        self.update_status("🗑️ 已清除參考數據")

    def clear_result(self):
        """清除結果"""
        self.result_text.delete(1.0, tk.END)
        self.current_report = ""
        self.update_status("🗑️ 已清除結果")

    def convert_multi_line_format(self):
        """轉換多行格式為 Tab 分隔格式"""
        # 獲取輸入框內容
        order_data = self.order_text.get(1.0, tk.END).strip()

        if not order_data:
            messagebox.showwarning("提示", "請先輸入資料！")
            return

        # 檢查是否為多行格式
        lines = order_data.split('\n')

        # 簡單判斷：如果幾乎每行都沒有 Tab，可能是多行格式
        tab_count = sum(1 for line in lines if '\t' in line)
        if tab_count > len(lines) * 0.3:  # 如果超過30%的行有Tab，可能已經是正確格式
            response = messagebox.askyesno(
                "確認",
                "資料看起來可能已經是正確的格式。\n\n是否仍要轉換？"
            )
            if not response:
                return

        try:
            self.update_status("🔄 轉換中...")

            # 解析多行格式
            orders = []
            current_order = []
            consecutive_empty_lines = 0

            for i, line in enumerate(lines):
                line = line.strip()

                if not line:
                    # 遇到空行表示一筆訂單結束
                    if current_order:
                        # 過濾掉空項
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
                messagebox.showwarning(
                    "轉換失敗",
                    "無法解析資料格式！\n\n"
                    "請確認資料是多行格式：\n"
                    "• 第1行：品項\n"
                    "• 第2行：姓名 生日\n"
                    "• 第3行：對象 生日（選填）\n"
                    "• 第N行：願望：內容"
                )
                self.update_status("❌ 轉換失敗")
                return

            # 更新輸入框
            self.order_text.delete(1.0, tk.END)
            for order in converted_orders:
                self.order_text.insert(tk.END, order + '\n')

            self.update_status(f"✅ 已轉換 {len(converted_orders)} 筆訂單")
            messagebox.showinfo(
                "轉換成功",
                f"✅ 成功轉換 {len(converted_orders)} 筆訂單！\n\n"
                f"資料已更新為 Tab 分隔格式。\n"
                f"現在可以點擊「生成報表」了。"
            )

        except Exception as e:
            messagebox.showerror("錯誤", f"轉換失敗：{str(e)}")
            self.update_status(f"❌ 轉換失敗：{str(e)}")

    def generate_report(self):
        """生成報表"""
        # 獲取訂單資料
        order_data = self.order_text.get(1.0, tk.END).strip()

        if not order_data:
            messagebox.showwarning("提示", "請先輸入訂單資料！")
            return

        # 驗證資料格式（支援 Tab 分隔或多行格式）
        lines = order_data.split('\n')
        tab_lines = 0
        item_lines = 0

        for line in lines:
            if line.strip():
                # 檢查是否有 Tab 分隔
                if '\t' in line:
                    tab_lines += 1
                # 檢查是否有品項格式 (例如：鬼王x2)
                if re.search(r'[xX×*]\d+', line):
                    item_lines += 1

        # 如果既沒有 Tab 分隔的行，也沒有品項格式的行，才報錯
        if tab_lines == 0 and item_lines == 0:
            messagebox.showerror(
                "資料格式錯誤",
                "❌ 未偵測到正確的訂單資料格式！\n\n"
                "支援兩種格式：\n\n"
                "1️⃣ Tab 分隔格式（推薦）：\n"
                "   品項<Tab>姓名/生日<Tab>對象/生日<Tab>願望\n"
                "   範例：鬼王x2+三鬼頭x4<Tab>王小明 1990/5/20<Tab>...\n\n"
                "2️⃣ 多行格式：\n"
                "   鬼王x2+三鬼頭x4\n"
                "   王小明 1990/5/20\n"
                "   李美麗 1992/8/15\n"
                "   願望：事業順利\n\n"
                "提示：點擊「📋 貼上範例資料」查看範例"
            )
            return

        # 獲取參考數據（選填）
        reference_data = self.ref_text.get(1.0, tk.END).strip()
        if not reference_data:
            reference_data = None

        try:
            self.update_status("🔄 處理中...")
            self.generate_btn.config(state='disabled')
            self.root.update()

            # 建立格式化工具並處理資料
            self.formatter = OrderFormatter()
            self.formatter.load_data(order_data)

            # 檢查是否成功載入資料
            if len(self.formatter.orders) == 0:
                messagebox.showwarning(
                    "資料解析失敗",
                    f"⚠️ 已讀取 {len(lines)} 行資料，但無法解析出有效訂單！\n\n"
                    "可能原因：\n"
                    "1. 資料分隔符號不是 Tab\n"
                    "2. 每行資料欄位不足（至少需要2欄）\n"
                    "3. 資料格式不符合預期\n\n"
                    "建議：\n"
                    "- 點擊「📋 貼上範例資料」查看正確格式\n"
                    "- 從 Excel 複製時，確保使用 Ctrl+C (Win) 或 Cmd+C (Mac)\n"
                    "- 檢查資料是否包含必要欄位"
                )
                self.update_status("❌ 資料解析失敗")
                self.generate_btn.config(state='normal')
                return

            self.update_status(f"📊 已載入 {len(self.formatter.orders)} 筆訂單，展開為 {len(self.formatter.expanded_orders)} 筆明細")

            # 生成報表
            self.current_report = self.formatter.generate_full_report(reference_data)

            # 顯示報表
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, self.current_report)

            # 顯示統計摘要
            summary = f"✅ 報表生成完成！總訂單：{len(self.formatter.orders)} 筆，總品項：{len(self.formatter.expanded_orders)} 支"
            if self.formatter.anomalies:
                summary += f"，異常訂單：{len(self.formatter.anomalies)} 筆 ⚠️"

            self.update_status(summary)

            messagebox.showinfo(
                "成功",
                f"報表生成完成！\n\n"
                f"📊 總訂單數：{len(self.formatter.orders)} 筆\n"
                f"📦 總品項數：{len(self.formatter.expanded_orders)} 支\n"
                f"🏷️ 品項種類：{len(self.formatter.item_stats)} 種\n"
                f"⚠️ 異常訂單：{len(self.formatter.anomalies)} 筆"
            )

        except Exception as e:
            messagebox.showerror("錯誤", f"處理失敗：{str(e)}")
            self.update_status(f"❌ 處理失敗：{str(e)}")
        finally:
            self.generate_btn.config(state='normal')

    def save_report(self):
        """儲存報表"""
        if not self.current_report:
            messagebox.showwarning("提示", "請先生成報表！")
            return

        # 預設檔名
        default_filename = f"訂單報表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        filename = filedialog.asksaveasfilename(
            title="儲存報表",
            defaultextension=".md",
            initialfile=default_filename,
            filetypes=[
                ("Markdown 檔案", "*.md"),
                ("文字檔案", "*.txt"),
                ("所有檔案", "*.*")
            ]
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.current_report)
                self.update_status(f"💾 報表已儲存：{os.path.basename(filename)}")
                messagebox.showinfo("成功", f"報表已儲存至：\n{filename}")
            except Exception as e:
                messagebox.showerror("錯誤", f"儲存失敗：{str(e)}")

    def copy_to_clipboard(self):
        """複製完整報表到剪貼簿"""
        if not self.current_report:
            messagebox.showwarning("提示", "請先生成報表！")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_report)
        self.update_status("📋 完整報表已複製到剪貼簿")
        messagebox.showinfo("成功", "完整報表已複製到剪貼簿！")

    def copy_plain_details(self):
        """複製純明細內容到剪貼簿（不含標題和統計）"""
        if not self.formatter:
            messagebox.showwarning("提示", "請先生成報表！")
            return

        # 生成純明細內容
        plain_details = self.formatter.generate_plain_details()

        self.root.clipboard_clear()
        self.root.clipboard_append(plain_details)
        self.update_status(f"📄 已複製 {len(self.formatter.expanded_orders)} 筆純明細到剪貼簿")
        messagebox.showinfo(
            "成功",
            f"已複製純明細內容！\n\n"
            f"共 {len(self.formatter.expanded_orders)} 筆訂單明細\n"
            f"格式：編號、品項、姓名/生日、對象/生日、願望"
        )

    def copy_plain_statistics(self):
        """複製純品項統計表到剪貼簿（Tab分隔格式，方便貼到Excel）"""
        if not self.formatter:
            messagebox.showwarning("提示", "請先生成報表！")
            return

        # 生成純品項統計內容
        plain_stats = self.formatter.generate_plain_statistics()

        self.root.clipboard_clear()
        self.root.clipboard_append(plain_stats)
        self.update_status(f"📊 已複製 {len(self.formatter.item_stats)} 種品項統計到剪貼簿")
        messagebox.showinfo(
            "成功",
            f"已複製純品項統計表！\n\n"
            f"共 {len(self.formatter.item_stats)} 種品項\n"
            f"格式：品項名稱、數量、單價、小計金額\n"
            f"可直接貼到 Excel 或記事本"
        )


def main():
    """主程式入口"""
    root = tk.Tk()
    app = OrderFormatterGUI(root)

    # 視窗置中
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()
