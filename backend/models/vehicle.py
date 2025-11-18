from pydantic import BaseModel, Field
from typing import List, Optional


class VehicleMaster(BaseModel):
    """車輛主數據模型"""
    manufacturer: str
    model: str
    inspection_times: List[int]  # 5個關卡時間 [站1, 站2, 站3, 站4, 站5]
    preferred_stations: List[str]  # 偏好的2個檢修廠
    system: Optional[str] = None  # 車系: 日系/韓系/陸系/歐系/美系（可選）
    
    def model_post_init(self, __context):
        """初始化後自動推斷車系"""
        if not self.system:
            # 根據製造商推斷車系
            self.system = self._infer_system()
    
    def _infer_system(self) -> str:
        """根據製造商推斷車系"""
        japanese = ['TOYOTA', 'HONDA', 'NISSAN', 'MAZDA', 'SUBARU', 'MITSUBISHI', 'SUZUKI', 'LEXUS', 'INFINITI', 'ACURA']
        korean = ['HYUNDAI', 'KIA', 'GENESIS', 'SSANGYONG']
        chinese = ['BYD', 'GEELY', 'CHERY', 'GREAT WALL', 'HAVAL', 'NIO', 'XPENG', 'LI AUTO']
        european = ['BMW', 'MERCEDES-BENZ', 'AUDI', 'VOLKSWAGEN', 'PORSCHE', 'VOLVO', 'LAND ROVER', 'JAGUAR', 'MINI', 'PEUGEOT', 'RENAULT', 'FIAT', 'ALFA ROMEO', 'SKODA']
        american = ['FORD', 'CHEVROLET', 'JEEP', 'RAM', 'CADILLAC', 'GMC', 'TESLA', 'CHRYSLER', 'DODGE', 'BUICK']
        
        manufacturer_upper = self.manufacturer.upper()
        
        if manufacturer_upper in japanese:
            return '日系'
        elif manufacturer_upper in korean:
            return '韓系'
        elif manufacturer_upper in chinese:
            return '陸系'
        elif manufacturer_upper in european:
            return '歐系'
        elif manufacturer_upper in american:
            return '美系'
        else:
            return '其他'
    
    @property
    def total_time(self) -> int:
        """總檢修時間（不考慮平行作業）"""
        return sum(self.inspection_times)
    
    @property
    def bottleneck_time(self) -> int:
        """瓶頸時間（最長的關卡）"""
        return max(self.inspection_times)
    
    def calculate_workstations(self) -> List[int]:
        """
        計算各關卡所需工位數
        使用最簡分數通分法，確保流水線平衡
        
        策略：
        1. 計算每個關卡相對於瓶頸的時間比例（分數）
        2. 找出所有分數的最小公倍數（LCM）作為通分母
        3. 將所有分數通分，取分子作為工位數
        4. 如果工位數過大（>20），進行縮放
        
        範例：
        - RAV4 [20,10,30,50,60] → 分數 [1/3, 1/6, 1/2, 5/6, 1] → LCM=6 → [2,1,3,5,6]
        - CAMRY [21,16,31,52,61] → 分數 [21/61, 16/61, ...] → LCM=61 → 縮放後合理數值
        """
        from fractions import Fraction
        from math import lcm, gcd
        from functools import reduce
        
        bottleneck = self.bottleneck_time
        
        # 計算比例並轉換為最簡分數
        fractions = [Fraction(t, bottleneck) for t in self.inspection_times]
        
        # 找出所有分母的最小公倍數
        denominators = [f.denominator for f in fractions]
        common_denominator = reduce(lcm, denominators)
        
        # 通分後取分子作為工位數
        workstations = [int(f.numerator * (common_denominator // f.denominator)) 
                       for f in fractions]
        
        # 如果工位數過大，進行簡化（保持比例）
        max_workstation = max(workstations)
        if max_workstation > 20:
            # 方法1: 先嘗試用 GCD 簡化
            workstation_gcd = reduce(gcd, workstations)
            if workstation_gcd > 1:
                workstations = [w // workstation_gcd for w in workstations]
                max_workstation = max(workstations)
            
            # 方法2: 如果還是太大，強制等比例縮小
            if max_workstation > 20:
                scale_factor = 20 / max_workstation
                workstations = [max(1, round(w * scale_factor)) for w in workstations]
        
        return workstations
    
    def calculate_setup_time(self) -> int:
        """
        計算換線時間
        換線時間 = 工位總數 × 2 分鐘
        """
        workstations = self.calculate_workstations()
        return sum(workstations) * 2
    
    class Config:
        json_schema_extra = {
            "example": {
                "manufacturer": "TOYOTA",
                "model": "RAV4",
                "inspection_times": [20, 10, 30, 50, 60],
                "preferred_stations": ["北高檢修廠", "楠梓檢修廠"],
                "system": "日系"
            }
        }
