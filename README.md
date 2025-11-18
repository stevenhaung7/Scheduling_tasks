# 車輛檢修排程系統 (Vehicle Inspection Scheduling System)

## 專案概述

本系統為車輛檢修廠的動態排程管理系統，支援多檢修廠、多批次的流水線排程優化與即時視覺化監控。

### 核心功能
- 🚗 支援 20+ 車廠、220+ 車型的檢修排程
- 🏭 5個檢修廠並行作業管理
- 📊 即時視覺化工位狀態與進度追蹤
- ⚡ 智能工位平衡計算（無 WIP 堆積）
- 🔄 換線時間自動計算與優化
- 📈 產能利用率監控與分析

---

## 系統架構

### 技術棧
- **後端**: Python 3.10+ / FastAPI
- **前端**: React 18+ / ECharts / Ant Design
- **通訊**: WebSocket (即時推送)
- **資料庫**: SQLite (開發) / PostgreSQL (生產)
- **建構工具**: Vite

### 架構圖
```
┌─────────────┐
│   React     │ ←─ WebSocket ─→ ┌──────────────┐
│  + ECharts  │                 │   FastAPI    │
└─────────────┘                 │              │
                                │ - 排程引擎    │
                                │ - 模擬器      │
                                │ - API        │
                                └──────────────┘
                                       ↓
                                ┌──────────────┐
                                │  PostgreSQL  │
                                └──────────────┘
```

---

## 業務邏輯

### 檢修流程
每輛車必須依序通過 5 個檢修關卡：
1. **車輛外觀檢查**
2. **跑輸送帶電腦掃描**
3. **起重機檢查底盤**
4. **測試** (動力、排氣、儀表板、煞車)
5. **集貨裝運**

### 檢修廠配置
- **南高檢修廠**
- **北高檢修廠**
- **鳳山檢修廠**
- **楠梓檢修廠**
- **岡山檢修廠**

### 工位平衡計算

**核心公式**：
```python
# 1. 找出瓶頸時間
bottleneck_time = max(stage_times)

# 2. 計算各關卡理想工位比例
ratios = [stage_time / bottleneck_time for stage_time in stage_times]

# 3. 轉換為最簡分數，通分後取分子
# 例如：[1/3, 1/6, 1/2, 5/6, 1] → 通分母6 → [2, 1, 3, 5, 6]
workstations = calculate_workstations(ratios)
```

**範例 (TOYOTA RAV4)**：
```
關卡時間: [20, 10, 30, 50, 60] 分鐘
瓶頸: 60 分鐘
工位數: [2, 1, 3, 5, 6]
```

### 換線作業

**公式**：
```python
換線時間 = 工位總數 × 2 分鐘
```

**範例**：
```
RAV4 工位總數: 2+1+3+5+6 = 17
換線時間: 17 × 2 = 34 分鐘
```

---

## 排程演算法

### 方案：貪婪啟發式 + 流水線模擬

#### 階段一：批次分配
```python
優先順序：
1. 優先選擇 preferred_stations (偏好檢修廠)
2. 選擇當前負載最低的檢修廠
3. 考慮換線成本 (相同車型優先同廠)
4. 平衡各廠利用率
```

#### 階段二：流水線模擬
```python
for vehicle in batch:
    for stage in [1, 2, 3, 4, 5]:
        # 找最早可用工位
        available_workstation = find_earliest_available(stage)
        # 考慮前一階段完成時間
        start_time = max(prev_finish_time, workstation_available_time)
        # 分配並更新時間表
        schedule(vehicle, stage, available_workstation, start_time)
```

---

## 資料結構

### 車輛主數據 (vehicles_data.json)
```json
{
  "manufacturer": "TOYOTA",
  "model": "RAV4",
  "inspection_times": [20, 10, 30, 50, 60],
  "preferred_stations": ["北高檢修廠", "楠梓檢修廠"],
  "system": "日系"
}
```

### 測試工單 (test_orders_xxx.json)
```json
{
  "batch_id": "1115_001",
  "manufacturer": "TOYOTA",
  "model": "RAV4",
  "quantity": 15,
  "system": "日系",
  "priority": "normal",
  "due_date": "2025-11-15 18:00"
}
```

---

## 視覺化設計

### 配色方案

#### 車系顏色
| 車系 | 背景色 | 字體色 |
|------|--------|--------|
| 日系 | `#E8F4F8` | `#1E5A6E` |
| 韓系 | `#FFF4E6` | `#8B5A00` |
| 陸系 | `#FEF0F0` | `#7D2828` |
| 歐系 | `#F0F9E8` | `#3D5A2E` |
| 美系 | `#FFF9E6` | `#8B7500` |

#### 關卡漸層（灰階）
```
站1: #F5F5F5 (最淺灰)
站2: #E0E0E0
站3: #BDBDBD
站4: #9E9E9E
站5: #757575 (最深灰)
```

#### 狀態顏色
```
等待:   #EF4444 (紅色)
進行中: #3B82F6 (藍色)
完成:   #10B981 (綠色)
```

### 主要視圖

#### 1. 全局時間軸控制
- 播放 / 暫停 / 快轉 / 倒退
- 速度控制 (1x, 2x, 4x)
- 時間軸拖拉條

#### 2. 整體產能儀表板
- 完成 / 進行中 / 等待車輛數
- 整體進度百分比

#### 3. 批次進度條
- 每批次完成狀況
- 預計完成時間

#### 4. 五個檢修廠工位狀態
```
┌─ 南高檢修廠 ────────────────────────────┐
│ 站1 [1115_001 RAV4_3][空][虛線][虛線]...│
│ 站2 [1115_001 RAV4_2][虛線]...         │
│ 站3 [空][空][空][虛線]...               │
│ 站4 [1115_001 RAV4_1][空][空][空][空]...│
│ 站5 [空][空][空][空][空][空]...         │
└────────────────────────────────────────┘
```

---

## 開發階段

### 階段一：核心視覺化 (MVP) - 2週
- [x] 測試工單創建
- [ ] 核心排程邏輯
- [ ] 流水線模擬
- [ ] API 開發
- [ ] 視覺化主視圖
- [ ] 時間軸控制

### 階段二：監控與預警 - 1週
- [ ] 檢修廠利用率
- [ ] 等候區車輛清單
- [ ] 瓶頸分析
- [ ] 異常警示

### 階段三：分析與優化 - 1週
- [ ] 換線歷史記錄
- [ ] 統計圖表
- [ ] 智能建議

---

## 專案結構

```
Scheduling_tasks/
├── README.md
├── vehicles_data.json          # 車輛主數據
├── test_orders_001.json        # 測試工單1
├── test_orders_002.json        # 測試工單2
├── test_orders_003.json        # 測試工單3
├── backend/                    # Python 後端
│   ├── main.py                # FastAPI 入口
│   ├── models/                # 數據模型
│   ├── scheduler/             # 排程引擎
│   ├── simulator/             # 流水線模擬器
│   └── api/                   # API 端點
├── frontend/                   # React 前端
│   ├── src/
│   │   ├── components/        # UI 組件
│   │   ├── services/          # API 服務
│   │   └── App.jsx
│   └── package.json
└── docs/                       # 文檔
```

---

## 快速開始

### 本地開發環境

#### 環境需求
- Python 3.11+
- Node.js 18+
- npm

#### 後端啟動
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端啟動
```powershell
cd frontend
npm install
npm run dev
```

#### 訪問系統
- 前端: http://localhost:5173
- API 文檔: http://localhost:8000/docs

---

## 雲端部署

本系統支援部署到雲端平台，供內部測試使用。

### 快速部署
1. 推送程式碼到 GitHub
2. 後端部署到 Railway (免費 $5/月額度)
3. 前端部署到 Vercel (完全免費)

**完整部署指南**: 請參考 [DEPLOYMENT.md](./DEPLOYMENT.md)

### 部署後訪問
- **前端**: `https://your-app.vercel.app`
- **後端 API**: `https://your-app.railway.app`
- **API 文檔**: `https://your-app.railway.app/docs`

---

## 系統特性

### 核心優勢
- ✅ **零 WIP 堆積**: 精確工位平衡計算
- ✅ **智能分配**: 考慮偏好檢修廠與負載平衡
- ✅ **即時視覺化**: WebSocket 推送，10分鐘刻度更新
- ✅ **高效模擬**: 貪婪演算法快速計算

### 運作假設
- OEE = 100% (理想狀態)
- 24 小時連續運作
- 無設備故障或延遲
- 單機使用，無權限管理

### 保留設計（未實作）
- 22HR 運作模式切換
- 手動調整排程
- 設備異常處理
- 用戶權限管理

---

## 測試數據

### 測試工單統計
- **ORDER_001**: 12批次，153台 (日系/歐系/美系)
- **ORDER_002**: 13批次，162台 (日系/韓系/陸系)
- **ORDER_003**: 14批次，155台 (歐系/日系高端)
- **總計**: 39批次，470台車輛

---

## 授權
MIT License

## 作者
車輛檢修排程系統開發團隊

## 版本
v1.0.0 - MVP (2025-11-15)
