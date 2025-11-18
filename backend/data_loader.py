import json
from typing import List, Dict
from pathlib import Path
from models.vehicle import VehicleMaster
from models.batch import Order, Batch


class DataLoader:
    """數據載入器"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
    
    def load_vehicles_master(self) -> Dict[str, VehicleMaster]:
        """
        載入車輛主數據
        返回: {(manufacturer, model): VehicleMaster}
        """
        file_path = self.base_path / "vehicles_data.json"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        vehicles = {}
        for vehicle_data in data.get('vehicles', []):
            key = (vehicle_data['manufacturer'], vehicle_data['model'])
            vehicles[key] = VehicleMaster(**vehicle_data)
        
        return vehicles
    
    def load_order(self, order_file: str) -> Order:
        """
        載入工單
        order_file: 'test_orders_001.json' 或完整路徑
        """
        file_path = self.base_path / order_file
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return Order(**data)
    
    def load_all_orders(self) -> List[Order]:
        """載入所有測試工單"""
        orders = []
        for i in range(1, 4):
            order_file = f"test_orders_{i:03d}.json"
            try:
                order = self.load_order(order_file)
                orders.append(order)
            except FileNotFoundError:
                pass
        
        return orders


def get_vehicle_master(vehicles_dict: Dict[str, VehicleMaster], 
                       manufacturer: str, 
                       model: str) -> VehicleMaster:
    """
    從字典中獲取車輛主數據
    """
    key = (manufacturer, model)
    if key not in vehicles_dict:
        raise ValueError(f"找不到車型: {manufacturer} {model}")
    return vehicles_dict[key]
