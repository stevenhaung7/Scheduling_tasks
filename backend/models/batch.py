from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    """優先級"""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class BatchStatus(str, Enum):
    """批次狀態"""
    PENDING = "pending"      # 等待排程
    SETUP = "setup"          # 換線中
    RUNNING = "running"      # 檢修中
    COMPLETED = "completed"  # 已完成


class Batch(BaseModel):
    """批次任務模型"""
    batch_id: str
    order_id: Optional[str] = None
    manufacturer: str
    model: str
    quantity: int
    system: str
    priority: Priority = Priority.NORMAL
    due_date: Optional[datetime] = None
    
    # 排程結果
    assigned_station: Optional[str] = None
    start_time: Optional[int] = None  # 分鐘（從0開始）
    finish_time: Optional[int] = None
    setup_time: Optional[int] = None
    status: BatchStatus = BatchStatus.PENDING
    
    class Config:
        json_schema_extra = {
            "example": {
                "batch_id": "1115_001",
                "order_id": "ORDER_001",
                "manufacturer": "TOYOTA",
                "model": "RAV4",
                "quantity": 15,
                "system": "日系",
                "priority": "normal",
                "due_date": "2025-11-15T18:00:00"
            }
        }


class Order(BaseModel):
    """工單模型"""
    order_id: str
    order_date: str
    description: str
    batches: List[Batch]
    total_batches: int
    total_vehicles: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ORDER_001",
                "order_date": "2025-11-15",
                "description": "第一批測試工單",
                "batches": [],
                "total_batches": 12,
                "total_vehicles": 153
            }
        }
