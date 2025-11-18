from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from typing import List

from api.routes import router as api_router
from simulator.flow_shop_simulator import FlowShopSimulator

app = FastAPI(title="車輛檢修排程系統 API")

# CORS設置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://scheduling-tasks.vercel.app",
        "https://*.vercel.app",  # 允許所有 Vercel 部署網址
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(api_router)

# WebSocket連接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()


@app.get("/")
async def root():
    return {
        "message": "車輛檢修排程系統 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.websocket("/ws/simulation")
async def websocket_simulation(websocket: WebSocket):
    """
    WebSocket模擬推送
    客戶端可控制播放/暫停/速度
    """
    await manager.connect(websocket)
    
    try:
        # 模擬參數
        current_time = 0
        is_playing = False
        speed = 1  # 1x, 2x, 4x
        max_time = 2000  # 預設最大時間（分鐘）
        
        while True:
            # 接收客戶端指令
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(), 
                    timeout=0.1
                )
                
                if data.get("command") == "play":
                    is_playing = True
                elif data.get("command") == "pause":
                    is_playing = False
                elif data.get("command") == "reset":
                    current_time = 0
                elif data.get("command") == "seek":
                    current_time = data.get("time", 0)
                elif data.get("command") == "speed":
                    speed = data.get("value", 1)
                elif data.get("command") == "set_max_time":
                    max_time = data.get("value", 2000)
            
            except asyncio.TimeoutError:
                pass
            
            # 推送當前狀態
            if is_playing:
                # 這裡需要從simulator獲取狀態
                # 簡化處理：先推送時間
                await websocket.send_json({
                    "type": "state_update",
                    "time": current_time,
                    "is_playing": is_playing,
                    "speed": speed
                })
                
                # 時間前進
                current_time += 10 * speed  # 每次前進10分鐘 * 速度
                
                if current_time >= max_time:
                    is_playing = False
                    current_time = max_time
                
                # 控制推送頻率
                await asyncio.sleep(0.5 / speed)
            else:
                await asyncio.sleep(0.1)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
