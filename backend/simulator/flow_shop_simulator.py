from typing import List, Dict, Tuple
from models.batch import Batch
from models.vehicle import VehicleMaster
from models.station import Station
from models.schedule import VehicleInstance, StageSchedule, VehicleStatus, ScheduleStatus
from data_loader import get_vehicle_master


class FlowShopSimulator:
    """流水線模擬器"""
    
    def __init__(self, 
                 vehicles_master: Dict[Tuple[str, str], VehicleMaster],
                 stations: Dict[str, Station]):
        self.vehicles_master = vehicles_master
        self.stations = stations
        self.vehicle_instances: List[VehicleInstance] = []
        self.schedules: List[StageSchedule] = []
    
    def simulate_batch(self, batch: Batch) -> Tuple[List[VehicleInstance], List[StageSchedule]]:
        """
        模擬單個批次的流水線排程
        返回: (車輛實例列表, 排程記錄列表)
        """
        if not batch.assigned_station:
            raise ValueError(f"批次 {batch.batch_id} 尚未分配檢修廠")
        
        # 獲取檢修廠和車輛主數據
        station = self.stations[batch.assigned_station]
        vehicle = get_vehicle_master(
            self.vehicles_master,
            batch.manufacturer,
            batch.model
        )
        
        # 確保檢修廠已初始化工位
        if not station.stages:
            workstation_config = vehicle.calculate_workstations()
            station.initialize_stages(workstation_config)
        
        # 創建車輛實例
        vehicles = self._create_vehicle_instances(batch)
        
        # 模擬流水線
        schedules = self._simulate_flow_shop(
            vehicles,
            batch,
            station,
            vehicle
        )
        
        # 更新批次完成時間（實際計算的精確時間）
        if schedules:
            batch.finish_time = max(s.finish_time for s in schedules)
        
        return vehicles, schedules
    
    def _create_vehicle_instances(self, batch: Batch) -> List[VehicleInstance]:
        """創建批次中的所有車輛實例"""
        vehicles = []
        for seq in range(1, batch.quantity + 1):
            vehicle = VehicleInstance(
                vehicle_id=f"{batch.batch_id}_{batch.model}_{seq}",
                batch_id=batch.batch_id,
                manufacturer=batch.manufacturer,
                model=batch.model,
                sequence=seq,
                system=batch.system,
                current_station=batch.assigned_station
            )
            vehicles.append(vehicle)
        
        return vehicles
    
    def _simulate_flow_shop(self,
                           vehicles: List[VehicleInstance],
                           batch: Batch,
                           station: Station,
                           vehicle_master: VehicleMaster) -> List[StageSchedule]:
        """
        模擬流水線生產
        每台車依序通過5個關卡
        """
        schedules = []
        stage_times = vehicle_master.inspection_times
        
        # 換線時間
        setup_time = batch.setup_time or vehicle_master.calculate_setup_time()
        current_time = batch.start_time or 0
        
        # 記錄每台車在每個關卡的完成時間
        vehicle_finish_times = {v.vehicle_id: 0 for v in vehicles}
        
        # 逐台車輛進行排程
        for vehicle in vehicles:
            prev_stage_finish = current_time + setup_time  # 第一台車要等換線完成
            vehicle_start_time = None
            
            # 依序通過5個關卡
            for stage_num in range(1, 6):
                stage = station.get_stage(stage_num)
                if not stage:
                    continue
                
                # 找最早可用的工位
                workstation = stage.find_earliest_available_workstation(prev_stage_finish)
                if not workstation:
                    continue
                
                # 計算開始時間
                # 考慮: 1) 工位可用時間 2) 前一關卡完成時間
                ws_available = workstation.get_available_time()
                start_time = max(ws_available, prev_stage_finish)
                
                # 計算完成時間
                duration = stage_times[stage_num - 1]
                finish_time = start_time + duration
                
                # 記錄車輛開始時間與狀態
                if vehicle_start_time is None:
                    vehicle_start_time = start_time
                    vehicle.start_time = start_time
                    vehicle.status = VehicleStatus.IN_PROGRESS
                
                # 創建排程記錄
                schedule = StageSchedule(
                    schedule_id=f"SCH_{batch.batch_id}_{vehicle.sequence}_{stage_num}",
                    vehicle_id=vehicle.vehicle_id,
                    batch_id=batch.batch_id,
                    station_name=station.station_name,
                    stage_number=stage_num,
                    workstation_id=workstation.workstation_id,
                    start_time=start_time,
                    finish_time=finish_time,
                    duration=duration
                )
                schedules.append(schedule)
                
                # 更新工位狀態
                workstation.current_vehicle = vehicle.vehicle_id
                workstation.start_time = start_time
                workstation.finish_time = finish_time
                workstation.status = "busy"
                
                # 更新下一關卡的前置時間
                prev_stage_finish = finish_time
            
            # 記錄車輛完成時間
            vehicle_finish_times[vehicle.vehicle_id] = prev_stage_finish
            vehicle.finish_time = prev_stage_finish
            vehicle.status = VehicleStatus.COMPLETED
        
        return schedules
    
    def simulate_all_batches(self, batches: List[Batch]) -> Dict:
        """
        模擬所有批次
        返回完整排程結果
        """
        all_vehicles = []
        all_schedules = []
        
        for batch in batches:
            if batch.assigned_station:
                vehicles, schedules = self.simulate_batch(batch)
                all_vehicles.extend(vehicles)
                all_schedules.extend(schedules)
        
        self.vehicle_instances = all_vehicles
        self.schedules = all_schedules
        
        return {
            "vehicles": all_vehicles,
            "schedules": all_schedules,
            "batches": batches,
            "stations": list(self.stations.values())
        }
    
    def get_state_at_time(self, time: int) -> Dict:
        """
        獲取指定時間點的系統狀態
        用於視覺化
        """
        state = {
            "time": time,
            "stations": {}
        }

        # 建立每個工位的狀態初始值
        workstation_lookup: Dict[str, Dict] = {}
        for station_name, station in self.stations.items():
            station_state = {
                "name": station_name,
                "status": station.status.value if hasattr(station.status, "value") else station.status,
                "current_batch": station.current_batch,
                "stages": []
            }
            ws_map = {}
            for stage in station.stages:
                stage_state = {
                    "stage_number": stage.stage_number,
                    "stage_name": stage.stage_name,
                    "workstations": []
                }
                for ws in stage.workstations:
                    ws_state = {
                        "workstation_id": ws.workstation_id,
                        "ws_number": ws.ws_number,
                        "status": "idle",
                        "current_vehicle": None
                    }
                    stage_state["workstations"].append(ws_state)
                    ws_map[ws.workstation_id] = ws_state
                station_state["stages"].append(stage_state)
            state["stations"][station_name] = station_state
            workstation_lookup[station_name] = ws_map

        # 套用排程資料決定特定時間點的工位狀態
        for schedule in self.schedules:
            station_state = state["stations"].get(schedule.station_name)
            if not station_state:
                continue
            ws_state = workstation_lookup[schedule.station_name].get(schedule.workstation_id)
            if not ws_state:
                continue

            if schedule.start_time <= time < schedule.finish_time:
                ws_state["status"] = "busy"
                ws_state["current_vehicle"] = schedule.vehicle_id
                station_state["status"] = "running"
                station_state["current_batch"] = schedule.batch_id
            elif time >= schedule.finish_time and ws_state["status"] != "busy":
                ws_state["status"] = "idle"

        return state
