from typing import List, Dict, Tuple
from models.batch import Batch
from models.vehicle import VehicleMaster
from models.station import Station, Workstation
from data_loader import get_vehicle_master


class GreedyScheduler:
    """貪婪啟發式排程器"""
    
    def __init__(self, vehicles_master: Dict[Tuple[str, str], VehicleMaster]):
        self.vehicles_master = vehicles_master
        self.stations = self._initialize_stations()
    
    def _initialize_stations(self) -> Dict[str, Station]:
        """初始化五個檢修廠"""
        station_names = [
            "南高檢修廠",
            "北高檢修廠", 
            "鳳山檢修廠",
            "楠梓檢修廠",
            "岡山檢修廠"
        ]
        
        stations = {}
        for name in station_names:
            station = Station(station_name=name)
            stations[name] = station
        
        return stations
    
    def assign_batches_to_stations(self, batches: List[Batch]) -> List[Batch]:
        """
        將批次分配到檢修廠
        使用貪婪策略
        """
        sorted_batches = self._sort_batches(batches)
        
        for batch in sorted_batches:
            # 獲取車輛主數據
            vehicle = get_vehicle_master(
                self.vehicles_master, 
                batch.manufacturer, 
                batch.model
            )
            
            # 計算工位配置和換線時間
            workstation_config = vehicle.calculate_workstations()
            setup_time = vehicle.calculate_setup_time()
            
            # 選擇最佳檢修廠
            selected_station = self._select_best_station(
                batch, 
                vehicle, 
                workstation_config,
                setup_time
            )
            
            # 分配批次
            batch.assigned_station = selected_station.station_name
            batch.setup_time = setup_time
            batch.start_time = 0  # 修正：所有批次都可以立即開始（流水線並行）
            
            # 估算完成時間（粗略估計，精確時間由模擬器計算）
            estimated_process_time = self._estimate_process_time(
                vehicle, 
                batch.quantity,
                workstation_config
            )
            batch.finish_time = batch.start_time + setup_time + estimated_process_time
            
            # 更新檢修廠狀態（記錄負載，但不阻塞後續批次）
            # next_available_time 不再影響開始時間
            selected_station.next_available_time = max(
                selected_station.next_available_time, 
                batch.finish_time
            )
            selected_station.total_batches += 1
            selected_station.total_vehicles += batch.quantity
            selected_station.current_batch = batch.batch_id
            
            # 動態調整檢修廠工位配置
            # 如果是第一個批次，直接初始化
            if not selected_station.stages:
                selected_station.initialize_stages(workstation_config)
            else:
                # 如果已有配置，需要擴展到所需工位數的最大值
                self._expand_station_workstations(selected_station, workstation_config)
        
        return sorted_batches
    
    def _sort_batches(self, batches: List[Batch]) -> List[Batch]:
        """
        排序批次
        優先級: high > normal > low
        相同優先級: due_date 早的優先
        """
        priority_order = {"high": 0, "normal": 1, "low": 2}
        
        return sorted(
            batches,
            key=lambda b: (
                priority_order.get(b.priority, 1),
                b.due_date if b.due_date else "9999-12-31"
            )
        )
    
    def _select_best_station(self, 
                            batch: Batch, 
                            vehicle: VehicleMaster,
                            workstation_config: List[int],
                            setup_time: int) -> Station:
        """
        選擇最佳檢修廠
        策略修正：允許多批次同時進行
        
        考慮因素:
        1. preferred_stations (偏好檢修廠)
        2. 當前可用的最早開始時間（非阻塞）
        3. 換線成本
        """
        candidate_stations = []
        
        # 優先考慮偏好檢修廠
        for station_name in vehicle.preferred_stations:
            if station_name in self.stations:
                candidate_stations.append(self.stations[station_name])
        
        # 如果偏好檢修廠為空，考慮所有檢修廠
        if not candidate_stations:
            candidate_stations = list(self.stations.values())
        
        # 計算每個候選檢修廠的得分
        scores = {}
        for station in candidate_stations:
            # 基礎得分：最早可開始時間（允許立即開始，不需等待前批結束）
            # 修正：next_available_time 應該是「下一批可進入的時間」，而非「當前批結束時間」
            # 對於流水線系統，只要第一工站有空，新批次就可以開始
            earliest_start = 0  # 允許立即開始（流水線特性）
            
            estimated_time = self._estimate_process_time(
                vehicle, 
                batch.quantity,
                workstation_config
            )
            finish_time = earliest_start + setup_time + estimated_time
            
            # 偏好加成
            preference_bonus = 1.0 if station.station_name in vehicle.preferred_stations else 1.2
            
            # 負載平衡：考慮檢修廠當前已分配的批次數量
            # 傾向選擇負載較低的檢修廠
            load_penalty = 1.0 + (station.total_batches * 0.1)
            
            score = finish_time * preference_bonus * load_penalty
            scores[station.station_name] = score
        
        # 選擇得分最低的（最優）
        best_station_name = min(scores, key=scores.get)
        return self.stations[best_station_name]
    
    def _estimate_process_time(self, 
                               vehicle: VehicleMaster, 
                               quantity: int,
                               workstation_config: List[int]) -> int:
        """
        粗略估算處理時間
        實際時間由流水線模擬器精確計算
        
        簡化公式: 
        處理時間 ≈ 瓶頸時間 × 數量
        （因為工位已平衡，瓶頸站限制產能）
        """
        bottleneck_time = vehicle.bottleneck_time
        return bottleneck_time * quantity
    
    def _expand_station_workstations(self, station: Station, new_config: List[int]):
        """
        動態擴展檢修廠工位數量
        每個關卡的工位數取現有配置和新配置的最大值
        
        Args:
            station: 檢修廠
            new_config: 新批次需要的工位配置 [5個關卡的工位數]
        """
        if len(station.stages) != 5 or len(new_config) != 5:
            return
        
        stage_names = [
            "車輛外觀檢查",
            "跑輸送帶電腦掃描",
            "起重機檢查底盤",
            "測試(動力測試,排氣測試,儀錶板功能測試,煞車功能測試)",
            "集貨裝運"
        ]
        
        for i in range(5):
            stage = station.stages[i]
            current_count = stage.workstation_count
            required_count = new_config[i]
            
            # 如果新配置需要更多工位，擴展工位數
            if required_count > current_count:
                # 添加新工位
                for ws_num in range(current_count, required_count):
                    new_workstation = Workstation(
                        workstation_id=f"{station.station_name}_{i+1}_{ws_num}",
                        station_name=station.station_name,
                        stage_number=i+1,
                        ws_number=ws_num
                    )
                    stage.workstations.append(new_workstation)
                
                # 更新工位數量
                stage.workstation_count = required_count
                
                # 更新檢修廠的工位配置記錄
                station.workstation_config[i] = required_count
    
    def get_station(self, station_name: str) -> Station:
        """獲取檢修廠"""
        return self.stations.get(station_name)
    
    def get_all_stations(self) -> List[Station]:
        """獲取所有檢修廠"""
        return list(self.stations.values())
