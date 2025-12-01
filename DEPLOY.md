# 🚀 部署指南

## 部署到 Streamlit Cloud（免費）

### 準備工作

確保您的專案包含以下文件：
- ✅ `app.py` - 主程式
- ✅ `order_formatter.py` - 核心邏輯
- ✅ `requirements.txt` - 相依套件
- ✅ `README.md` - 說明文件

### 步驟 1：上傳到 GitHub

#### 1.1 初始化 Git（如果還沒有）

```bash
cd /Users/hao/Desktop/訂單整理工具
git init
git add .
git commit -m "Initial commit: 訂單整理工具網頁版"
```

#### 1.2 建立 GitHub Repository

1. 登入 [GitHub](https://github.com)
2. 點擊右上角 `+` → `New repository`
3. Repository 名稱：`order-management-tool` （或其他名稱）
4. 選擇 `Public`（必須是公開才能免費部署）
5. **不要**勾選任何初始化選項
6. 點擊 `Create repository`

#### 1.3 推送程式碼到 GitHub

複製 GitHub 提供的命令（類似下方），並執行：

```bash
git remote add origin https://github.com/你的用戶名/order-management-tool.git
git branch -M main
git push -u origin main
```

### 步驟 2：部署到 Streamlit Cloud

#### 2.1 註冊 Streamlit Cloud

1. 訪問 [streamlit.io/cloud](https://streamlit.io/cloud)
2. 點擊 `Sign up` 或 `Sign in with GitHub`
3. 授權 Streamlit 存取您的 GitHub 帳號

#### 2.2 建立新的部署

1. 登入後，點擊 `New app`
2. 選擇您的 Repository：`你的用戶名/order-management-tool`
3. Branch: `main`
4. Main file path: `app.py`
5. 點擊 `Deploy!`

#### 2.3 等待部署完成

- 初次部署需要 2-5 分鐘
- 您會看到部署進度和日誌
- 完成後會自動開啟應用程式

### 步驟 3：獲取網址

部署成功後，您會獲得一個網址：

```
https://你的用戶名-order-management-tool-app-xxxxxx.streamlit.app
```

這個網址可以：
- ✅ 分享給任何人使用
- ✅ 在任何裝置（電腦、手機、平板）開啟
- ✅ 無需安裝任何軟體

## 本地測試

在部署前，建議先在本地測試：

```bash
# 安裝相依套件
pip install -r requirements.txt

# 啟動網頁版
streamlit run app.py

# 或雙擊（macOS）
./啟動網頁版.command
```

瀏覽器會自動開啟 `http://localhost:8501`

## 更新部署

當您修改程式碼後：

```bash
# 提交修改
git add .
git commit -m "描述您的修改"
git push

# Streamlit Cloud 會自動偵測並重新部署
```

## 常見問題

### Q: 部署失敗怎麼辦？

**A:** 檢查以下項目：
1. `requirements.txt` 是否包含所有套件
2. `app.py` 是否有語法錯誤
3. 查看 Streamlit Cloud 的部署日誌

### Q: 可以部署私有 Repository 嗎？

**A:** 可以，但需要付費方案。免費方案只支援公開 Repository。

### Q: 如何自訂網址？

**A:**
1. 在 Streamlit Cloud 設定中可修改 App URL
2. 或使用自己的網域（需要付費方案）

### Q: 有使用限制嗎？

**A:** 免費方案限制：
- 1 個私有 App 或 無限公開 Apps
- 1 GB RAM
- 共享 CPU
- 適合個人使用和小型專案

## 進階設定

### 設定 Secrets（如果需要）

1. 在 Streamlit Cloud 的 App 設定中
2. 點擊 `Secrets`
3. 添加敏感資訊（如 API Keys）

### 自訂配置

建立 `.streamlit/config.toml`：

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
```

## 其他部署選項

### Heroku（免費額度已取消）

適合需要更多控制的情況

### Render

另一個免費部署平台

### Railway

提供免費額度

## 疑難排解

### 錯誤：ModuleNotFoundError

**解決：** 確保 `requirements.txt` 包含所有套件

### 錯誤：Port already in use

**解決：** 關閉其他 Streamlit 實例，或使用不同 port：
```bash
streamlit run app.py --server.port 8502
```

### 應用程式很慢

**解決：**
1. 優化程式碼，減少不必要的計算
2. 使用 `@st.cache_data` 快取資料
3. 考慮升級到付費方案

## 資源

- [Streamlit 官方文檔](https://docs.streamlit.io)
- [Streamlit Cloud 文檔](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit 社群論壇](https://discuss.streamlit.io)

---

🎉 **恭喜！您的應用程式已成功部署！**

記得在 README.md 中更新您的應用程式網址！
