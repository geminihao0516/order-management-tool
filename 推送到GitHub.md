# 推送到 GitHub 指南

## 🎯 您的 Repository

```
https://github.com/geminihao0516/order-management-tool
```

---

## 方法一：使用 GitHub Desktop（最簡單）

### 步驟：

1. **下載 GitHub Desktop**
   - 訪問：https://desktop.github.com
   - 下載並安裝

2. **登入 GitHub Desktop**
   - 開啟 GitHub Desktop
   - File → Options → Accounts → Sign in

3. **添加本地倉庫**
   - File → Add Local Repository
   - 選擇：`/Users/hao/Desktop/訂單整理工具`
   - 點擊 Add Repository

4. **推送到 GitHub**
   - 點擊上方的 `Publish repository`
   - 或點擊 `Push origin`
   - 完成！

---

## 方法二：使用命令列（需要 Personal Access Token）

### 步驟 1：建立 Personal Access Token

1. **登入 GitHub**
   - 訪問：https://github.com

2. **進入設定**
   - 點擊右上角頭像 → Settings

3. **建立 Token**
   - 左側選單：Developer settings
   - Personal access tokens → Tokens (classic)
   - 點擊：Generate new token (classic)

4. **設定 Token**
   ```
   Note: order-management-tool-push
   Expiration: 90 days（或選擇其他）

   勾選權限：
   ✅ repo（勾選全部 repo 相關）
   ```

5. **生成並複製**
   - 點擊：Generate token
   - **立即複製 Token**（只會顯示一次！）
   - 格式類似：`ghp_xxxxxxxxxxxxxxxxxxxx`

### 步驟 2：推送程式碼

打開終端機，執行：

```bash
cd "/Users/hao/Desktop/訂單整理工具"

# 推送（會要求輸入）
git push -u origin main
```

當要求輸入時：
- **Username**: `geminihao0516`
- **Password**: 貼上您的 **Personal Access Token**（不是密碼）

---

## 方法三：設定 SSH Key（一勞永逸）

### 步驟 1：生成 SSH Key

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
```

按 Enter 使用預設位置，設定密碼（可選）

### 步驟 2：複製 SSH Key

```bash
cat ~/.ssh/id_ed25519.pub
```

複製輸出的內容

### 步驟 3：添加到 GitHub

1. GitHub → Settings → SSH and GPG keys
2. 點擊：New SSH key
3. Title: `Mac Desktop`
4. Key: 貼上剛才複製的內容
5. 點擊：Add SSH key

### 步驟 4：更改 Remote URL

```bash
cd "/Users/hao/Desktop/訂單整理工具"
git remote set-url origin git@github.com:geminihao0516/order-management-tool.git
git push -u origin main
```

---

## ✅ 驗證推送成功

推送成功後，訪問：

```
https://github.com/geminihao0516/order-management-tool
```

您應該會看到：
- ✅ app.py
- ✅ order_formatter.py
- ✅ requirements.txt
- ✅ README.md
- ✅ 其他文件

---

## 🚨 常見問題

### Q: Permission denied (publickey)

**A:** 使用方法一（GitHub Desktop）或方法二（Personal Access Token）

### Q: Authentication failed

**A:** 確認：
1. Username 正確：`geminihao0516`
2. Password 使用 **Token**（不是 GitHub 密碼）

### Q: Token 遺失了

**A:** 重新建立一個新的 Token（步驟同上）

---

## 📋 推送成功後的下一步

### 1. 確認文件已上傳

訪問：https://github.com/geminihao0516/order-management-tool

### 2. 部署到 Streamlit Cloud

1. 訪問：https://streamlit.io/cloud
2. Sign in with GitHub
3. New app
4. Repository: `geminihao0516/order-management-tool`
5. Branch: `main`
6. Main file: `app.py`
7. Deploy!

### 3. 獲得應用網址

約 2-5 分鐘後，您會獲得網址：
```
https://geminihao0516-order-management-tool-app-xxxxx.streamlit.app
```

### 4. 更新 README

將網址填入 README.md 的徽章中

---

## 💡 建議

**最簡單的方式：使用 GitHub Desktop**
- 視覺化介面
- 無需記指令
- 自動處理認證

下載：https://desktop.github.com

---

需要協助？請告訴我您選擇哪個方法！
