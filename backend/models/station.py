from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum


class StationStatus(str, Enum):
    """檢修廠狀態"""
    IDLE = "idle"        # 閒置
    SETUP = "setup"      # 換線中
    RUNNING = "running"  # 運行中


class WorkstationStatus(str, Enum):
    """工位狀態"""
    IDLE = "idle"    # 空閒
    BUSY = "busy"    # 忙碌


class Workstation(BaseModel):
    """工位模型"""
    workstation_id: str  # 格式: {station}_{stage}_{ws}
    station_name: str
    stage_number: int  # 1-5
    ws_number: int  # 工位編號
    current_vehicle: Optional[str] = None
    start_time: Optional[int] = None
    finish_time: Optional[int] = None
    status: WorkstationStatus = WorkstationStatus.IDLE
    
    def is_available(self, time: int) -> bool:
        """檢查工位在指定時間是否可用"""
        if self.status == WorkstationStatus.IDLE:
            return True
        if self.finish_time and time >= self.finish_time:
            return True
        return False
    
    def get_available_time(self) -> int:
        """獲取工位最早可用時間"""
        if self.status == WorkstationStatus.IDLE:
            return 0
        return self.finish_time if self.finish_time else 0


class Stage(BaseModel):
    """關卡模型"""
    station_name: str
    stage_number: int  # 1-5
    stage_name: str
    workstation_count: int
    workstations: List[Workstation] = []
    utilization: float = 0.0
    
    def initialize_workstations(self):
        """初始化工位"""
        self.workstations = [
            Workstation(
                workstation_id=f"{self.station_name}_{self.stage_number}_{i}",
                station_name=self.station_name,
                stage_number=self.stage_number,
                ws_number=i
            )
            for i in range(self.workstation_count)
        ]
    
    def find_earliest_available_workstation(self, time: int = 0) -> Optional[Workstation]:
        """找到最早可用的工位"""
        available = []
        for ws in self.workstations:
            if ws.is_available(time):
                available.append(ws)
        
        if not available:
            # 所有工位都忙碌，找最早完成的
            return min(self.workstations, key=lambda x: x.get_available_time())
        
        # 找到最早可用的（已經空閒的優先）
        return min(available, key=lambda x: x.get_available_time())


class Station(BaseModel):
    """檢修廠模型"""
    station_name: str
    current_batch: Optional[str] = None
    workstation_config: List[int] = []  # 5個關卡的工位配置
    stages: List[Stage] = []
    utilization: float = 0.0
    next_available_time: int = 0
    status: StationStatus = StationStatus.IDLE
    
    # 統計資料
    total_batches: int = 0
    total_vehicles: int = 0
    
    def initialize_stages(self, workstation_config: List[int]):
        """
        初始化檢修廠的5個關卡
        workstation_config: [站1工位數, 站2工位數, ..., 站5工位數]
        """
        self.workstation_config = workstation_config
        
        stage_names = [
            "車輛外觀檢查",
            "跑輸送帶電腦掃描",
            "起重機檢查底盤",
            "測試(動力測試,排氣測試,儀錶板功能測試,煞車功能測試)",
            "集貨裝運"
        ]
        
        self.stages = []
        for i, count in enumerate(workstation_config, 1):
            stage = Stage(
                station_name=self.station_name,
                stage_number=i,
                stage_name=stage_names[i-1],
                workstation_count=count
            )
            stage.initialize_workstations()
            self.stages.append(stage)
    
    def get_stage(self, stage_number: int) -> Optional[Stage]:
        """獲取指定關卡"""
        for stage in self.stages:
            if stage.stage_number == stage_number:
                return stage
        return None
    
    def calculate_utilization(self, total_time: int) -> float:
        """計算利用率"""
        if total_time == 0:
            return 0.0
        
        total_busy_time = 0
        total_capacity = 0
        
        for stage in self.stages:
            for ws in stage.workstations:
                total_capacity += total_time
                if ws.finish_time:
                    total_busy_time += (ws.finish_time - (ws.start_time or 0))
        
        if total_capacity == 0:
            return 0.0
        
        return total_busy_time / total_capacity
