from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

from data_loader import DataLoader
from scheduler.greedy_scheduler import GreedyScheduler
from simulator.flow_shop_simulator import FlowShopSimulator

router = APIRouter(prefix="/api", tags=["scheduling"])

# 全局變量存儲排程結果
_scheduler = None
_simulator = None
_current_result = None


class ScheduleRequest(BaseModel):
    """排程請求"""
    order_file: str  # 例如: "test_orders_001.json"


class ScheduleResponse(BaseModel):
    """排程響應"""
    success: bool
    message: str
    total_batches: int
    total_vehicles: int
    total_time: int


@router.post("/schedule", response_model=ScheduleResponse)
async def create_schedule(request: ScheduleRequest):
    """
    創建排程
    讀取工單並執行排程計算
    """
    global _scheduler, _simulator, _current_result
    
    try:
        # 載入數據 - 數據文件在項目根目錄（backend的上一層）
        import os
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(backend_dir)
        loader = DataLoader(base_path=project_root)
        vehicles_master = loader.load_vehicles_master()
        order = loader.load_order(request.order_file)
        
        # 初始化排程器
        _scheduler = GreedyScheduler(vehicles_master)
        
        # 批次分配
        assigned_batches = _scheduler.assign_batches_to_stations(order.batches)
        
        # 初始化模擬器
        _simulator = FlowShopSimulator(vehicles_master, _scheduler.stations)
        
        # 模擬流水線
        _current_result = _simulator.simulate_all_batches(assigned_batches)
        
        # 計算總時間
        max_time = 0
        if _current_result["schedules"]:
            max_time = max(s.finish_time for s in _current_result["schedules"])
        
        return ScheduleResponse(
            success=True,
            message=f"排程完成: {order.order_id}",
            total_batches=len(assigned_batches),
            total_vehicles=sum(b.quantity for b in assigned_batches),
            total_time=max_time
        )
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"找不到工單文件: {request.order_file}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"排程失敗: {str(e)}")


@router.get("/result")
async def get_schedule_result():
    """
    獲取排程結果
    """
    global _current_result
    
    if not _current_result:
        raise HTTPException(status_code=404, detail="尚未執行排程")
    
    # 轉換為可序列化的格式
    return {
        "batches": [b.model_dump() for b in _current_result["batches"]],
        "vehicles": [v.model_dump() for v in _current_result["vehicles"]],
        "schedules": [s.model_dump() for s in _current_result["schedules"]],
        "stations": [st.model_dump() for st in _current_result["stations"]]
    }


@router.get("/state/{time}")
async def get_state_at_time(time: int):
    """
    獲取指定時間點的狀態
    用於視覺化
    """
    global _simulator
    
    if not _simulator:
        raise HTTPException(status_code=404, detail="尚未執行排程")
    
    state = _simulator.get_state_at_time(time)
    return state


@router.get("/stations")
async def get_stations():
    """獲取所有檢修廠狀態"""
    global _scheduler
    
    if not _scheduler:
        raise HTTPException(status_code=404, detail="尚未執行排程")
    
    stations = _scheduler.get_all_stations()
    return [s.model_dump() for s in stations]
