# 📋 訂單資料整理工具

一個強大的訂單資料處理工具，支援自動品項展開、統計分析、差異比對等功能。

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

## ✨ 功能特色

- ✅ **自動品項展開**：將 `鬼王x3` 自動展開為 3 筆獨立明細
- ✅ **智慧統計**：自動統計各品項數量和金額
- ✅ **格式轉換**：支援多種輸入格式，自動識別
- ✅ **異常檢測**：自動檢測重複品項等異常情況
- ✅ **參考比對**：可與參考數據比對，確認統計正確性
- ✅ **多種輸出**：提供完整報表、純明細、統計表等多種格式

## 🚀 快速開始

### 線上使用（網頁版）

**👉 [立即使用](https://your-app.streamlit.app)** （部署後更新此連結）

無需安裝，直接在瀏覽器使用！

### 本地運行

#### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

#### 2. 啟動應用程式

**網頁版（推薦）：**
```bash
streamlit run app.py
```

**桌面版：**
```bash
python order_formatter_gui.py
```

macOS 使用者也可以雙擊 `啟動GUI.command`

## 📋 使用說明

### 輸入資料格式

#### 格式一：Tab 分隔（推薦）

從 Excel 直接複製會保留此格式：

```
鬼王x2+三鬼頭x4    王小明 1990/5/20    李美麗 1992/8/15    願望：事業順利
愛神x1    陳大華 1985/12/10    —    求好姻緣
```

#### 格式二：多行格式

```
鬼王x2+三鬼頭x4
王小明 1990/5/20
李美麗 1992/8/15
願望：事業順利

愛神x1
陳大華 1985/12/10
—
求好姻緣
```

### 品項格式

支援以下寫法：
- `鬼王x3` 或 `鬼王 x 3`
- `鬼王*3` 或 `鬼王 * 3`
- 多品項：`鬼王x2+三鬼頭x4` 或 `鬼王x2、三鬼頭x4`

### 使用流程

1. **輸入訂單資料**：貼上或輸入訂單資料
2. **（可選）輸入參考數據**：用於比對驗證
3. **生成報表**：點擊按鈕生成
4. **下載或複製**：選擇需要的格式

## 📦 輸出格式

### 1. 完整報表
包含摘要、明細表、統計表、異常報告等完整資訊

### 2. 純明細（Tab 分隔）
橫向格式，適合貼到 Excel：
```
1    鬼王    王小明 1990/5/20    李美麗 1992/8/15    事業順利
2    鬼王    王小明 1990/5/20    李美麗 1992/8/15    事業順利
```

### 3. 品項統計表
```
鬼王    87    $250    $21,750
三鬼頭    101    $300    $30,300
總計    188    -    $52,050
```

## 🛠️ 技術架構

### 核心模組
- `order_formatter.py` - 核心處理邏輯
- `app.py` - Streamlit 網頁版介面
- `order_formatter_gui.py` - tkinter 桌面版介面

### 相依套件
- Python 3.7+
- streamlit - 網頁框架
- openpyxl - Excel 讀取（可選）

## 📂 專案結構

```
訂單整理工具/
├── app.py                      # Streamlit 網頁版主程式
├── order_formatter.py          # 核心處理邏輯
├── order_formatter_gui.py      # tkinter 桌面版
├── requirements.txt            # 相依套件清單
├── README.md                   # 本文件
├── .gitignore                  # Git 忽略檔案
├── 範例資料.txt                # 範例訂單資料
└── 範例參考數據.txt            # 範例參考數據
```

## 🌐 部署到 Streamlit Cloud

### 步驟

1. **推送到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/你的用戶名/訂單整理工具.git
   git push -u origin main
   ```

2. **部署到 Streamlit Cloud**
   - 訪問 [streamlit.io/cloud](https://streamlit.io/cloud)
   - 登入並連接 GitHub
   - 選擇您的 repository
   - 主文件選擇：`app.py`
   - 點擊 **Deploy**

3. **完成！**
   - 您會獲得一個網址，例如：`https://your-app.streamlit.app`
   - 分享給任何人，直接在瀏覽器使用

### 部署注意事項

- 確保 `requirements.txt` 包含所有相依套件
- 主程式文件名為 `app.py`
- 建議使用 `main` 分支

## 💡 使用技巧

1. **從 Excel 複製資料**
   - 直接從 Excel 選取 → Ctrl+C → 貼到工具
   - 會自動保留 Tab 分隔

2. **參考數據比對**
   - 用於驗證統計結果
   - 支援格式：`87支鬼王` 或 `鬼王 87 支`

3. **異常訂單檢測**
   - 自動檢測重複品項
   - 在報表中標註警告

## 🐛 故障排除

### 無法解析訂單資料

**解決方案：**
1. 確認使用 Tab 分隔（不是空格）
2. 從 Excel 複製時使用 Ctrl+C
3. 參考範例資料格式

### 品項統計不正確

**解決方案：**
1. 檢查品項格式（例如：`鬼王x3`）
2. 查看異常訂單報告
3. 使用參考數據比對

### 網頁版無法啟動

**解決方案：**
```bash
# 確認 Streamlit 已安裝
pip install --upgrade streamlit

# 清除緩存
streamlit cache clear

# 重新啟動
streamlit run app.py
```

## 📝 版本歷史

### v2.0 (2025-12-01)
- ✨ 新增 Streamlit 網頁版
- ✨ 支援線上部署到 Streamlit Cloud
- 🎨 全新使用者介面
- 📱 支援行動裝置訪問
- 🚀 一鍵部署功能

### v1.4 (2024-11-03)
- ✨ 新增 tkinter 桌面 GUI 版本
- ✨ 新增多行格式轉換
- ✨ 新增異常訂單檢測
- 🐛 修復品項解析問題

## 📄 授權

MIT License

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！

## 📧 聯絡

如有問題或建議，請透過 GitHub Issues 回報

---

**⭐ 如果這個工具對您有幫助，請給個星星支持！**

Made with ❤️ using [Streamlit](https://streamlit.io)
