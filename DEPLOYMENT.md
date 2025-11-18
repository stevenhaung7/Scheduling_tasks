# 車輛檢修排程系統 - 部署指南

## 📦 部署架構

- **前端**: Vercel (React + Vite)
- **後端**: Railway (FastAPI + Python)
- **程式碼**: GitHub Repository

---

## 🚀 部署步驟

### 1️⃣ 準備 GitHub Repository

```bash
# 1. 在 GitHub 建立新的 repository
# 2. 上傳程式碼
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的帳號/scheduling-system.git
git push -u origin main
```

---

### 2️⃣ 部署後端到 Railway

1. **註冊 Railway**
   - 前往 https://railway.app
   - 使用 GitHub 帳號登入

2. **建立新專案**
   - 點擊 "New Project"
   - 選擇 "Deploy from GitHub repo"
   - 選擇您的 repository

3. **設定環境變數**
   ```
   PYTHON_VERSION=3.11
   PYTHONPATH=/app/backend
   PORT=8000
   ```

4. **設定啟動命令**
   - Railway 會自動偵測 `railway.json`
   - 或手動設定: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

5. **取得後端 URL**
   - 部署完成後會得到類似: `https://your-app.railway.app`
   - 記下這個 URL

---

### 3️⃣ 部署前端到 Vercel

1. **註冊 Vercel**
   - 前往 https://vercel.com
   - 使用 GitHub 帳號登入

2. **建立新專案**
   - 點擊 "Add New" → "Project"
   - 選擇您的 GitHub repository
   - 設定 Root Directory: `frontend`

3. **設定環境變數**
   ```
   VITE_API_URL=https://your-app.railway.app
   ```
   ⚠️ 將 `your-app.railway.app` 替換成您的 Railway 後端 URL

4. **設定建置命令**
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`

5. **部署**
   - 點擊 "Deploy"
   - 等待建置完成

6. **取得前端 URL**
   - 部署完成後會得到類似: `https://your-app.vercel.app`

---

## 🔧 後端 CORS 設定

確認 `backend/main.py` 的 CORS 設定包含 Vercel 網址:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-app.vercel.app"  # 加入您的 Vercel 網址
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ✅ 驗證部署

1. **測試後端**
   ```bash
   curl https://your-app.railway.app/
   ```
   應該回傳: `{"message":"車輛檢修排程系統 API","version":"1.0.0"}`

2. **測試前端**
   - 開啟瀏覽器訪問: `https://your-app.vercel.app`
   - 點擊「開始排程」測試功能

---

## 🆓 免費額度說明

### Vercel (前端)
- ✅ 完全免費
- ✅ 100 GB 頻寬/月
- ✅ 無限部署次數

### Railway (後端)
- ✅ 免費 $5 美金額度/月
- ✅ 約可運行 500 小時/月
- ⚠️ 超過額度需付費

### 節省 Railway 額度技巧
1. 設定閒置自動睡眠 (15 分鐘)
2. 只在測試時啟動
3. 監控使用量

---

## 🔄 自動部署 (CI/CD)

配置完成後:
- ✅ 推送到 GitHub → 自動部署
- ✅ Pull Request → 自動預覽
- ✅ 回滾到先前版本

---

## 📱 訪問方式

部署完成後,任何人都可以透過以下網址訪問:

- **前端**: `https://your-app.vercel.app`
- **後端 API**: `https://your-app.railway.app`
- **API 文檔**: `https://your-app.railway.app/docs`

---

## ❓ 常見問題

### Q: Railway 免費額度用完了怎麼辦?
A: 可以:
1. 切換到 Render (完全免費但會睡眠)
2. 升級 Railway 付費方案 ($5/月起)
3. 自架伺服器

### Q: 前端無法連接後端?
A: 檢查:
1. Vercel 環境變數 `VITE_API_URL` 是否正確
2. Railway 後端是否正常運行
3. CORS 設定是否包含 Vercel 網址

### Q: 部署後效能如何?
A: 
- 前端: Vercel CDN 全球加速,很快
- 後端: Railway 免費版在美國/歐洲,台灣訪問延遲約 200-300ms

---

## 📞 技術支援

如有問題,請查看:
- Railway 文檔: https://docs.railway.app
- Vercel 文檔: https://vercel.com/docs
- FastAPI 文檔: https://fastapi.tiangolo.com
