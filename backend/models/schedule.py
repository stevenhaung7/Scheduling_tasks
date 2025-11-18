from pydantic import BaseModel
from typing import Optional
from enum import Enum


class VehicleStatus(str, Enum):
    """車輛狀態"""
    WAITING = "waiting"          # 等待
    IN_PROGRESS = "in_progress"  # 進行中
    COMPLETED = "completed"      # 完成


class VehicleInstance(BaseModel):
    """車輛實例模型"""
    vehicle_id: str  # 格式: {batch_id}_{model}_{seq}
    batch_id: str
    manufacturer: str
    model: str
    sequence: int  # 在批次中的序號
    system: str
    
    current_stage: int = 0  # 當前關卡 0-5 (0表示未開始)
    current_station: Optional[str] = None
    status: VehicleStatus = VehicleStatus.WAITING
    
    # 時間記錄
    start_time: Optional[int] = None
    finish_time: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "vehicle_id": "1115_001_RAV4_3",
                "batch_id": "1115_001",
                "manufacturer": "TOYOTA",
                "model": "RAV4",
                "sequence": 3,
                "system": "日系",
                "current_stage": 2,
                "status": "in_progress"
            }
        }


class ScheduleStatus(str, Enum):
    """排程狀態"""
    SCHEDULED = "scheduled"          # 已排程
    IN_PROGRESS = "in_progress"      # 進行中
    COMPLETED = "completed"          # 已完成


class StageSchedule(BaseModel):
    """關卡排程模型"""
    schedule_id: str
    vehicle_id: str
    batch_id: str
    station_name: str
    stage_number: int  # 1-5
    workstation_id: str
    
    start_time: int  # 分鐘
    finish_time: int  # 分鐘
    duration: int  # 分鐘
    
    status: ScheduleStatus = ScheduleStatus.SCHEDULED
    
    class Config:
        json_schema_extra = {
            "example": {
                "schedule_id": "SCH_001",
                "vehicle_id": "1115_001_RAV4_3",
                "batch_id": "1115_001",
                "station_name": "南高檢修廠",
                "stage_number": 2,
                "workstation_id": "南高_2_0",
                "start_time": 40,
                "finish_time": 50,
                "duration": 10,
                "status": "scheduled"
            }
        }
