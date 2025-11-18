import { Card, Statistic, Row, Col, Progress } from 'antd';
import { 
  CheckCircleOutlined, 
  SyncOutlined, 
  ClockCircleOutlined,
  CarOutlined 
} from '@ant-design/icons';
import useScheduleStore from '../store/scheduleStore';

const Dashboard = () => {
  const { vehicles, currentTime } = useScheduleStore();

  // 計算統計數據
  const completedVehicles = vehicles.filter(v => typeof v.finish_time === 'number' && v.finish_time <= currentTime).length;
  const inProgressVehicles = vehicles.filter(v => {
    const start = typeof v.start_time === 'number' ? v.start_time : null;
    const finish = typeof v.finish_time === 'number' ? v.finish_time : null;
    if (start === null || start > currentTime) return false;
    if (finish === null) return true;
    return finish > currentTime;
  }).length;
  const waitingVehicles = Math.max(0, vehicles.length - completedVehicles - inProgressVehicles);
  const totalVehicles = vehicles.length;
  
  const progress = totalVehicles > 0 ? Math.round((completedVehicles / totalVehicles) * 100) : 0;

  return (
    <Card 
      title="今日概況" 
      style={{ 
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}
    >
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Statistic
            title="完成"
            value={completedVehicles}
            suffix={`/ ${totalVehicles} 台`}
            prefix={<CheckCircleOutlined style={{ color: '#10B981' }} />}
            valueStyle={{ color: '#10B981' }}
          />
        </Col>
        
        <Col span={6}>
          <Statistic
            title="進行中"
            value={inProgressVehicles}
            suffix="台"
            prefix={<SyncOutlined spin style={{ color: '#3B82F6' }} />}
            valueStyle={{ color: '#3B82F6' }}
          />
        </Col>
        
        <Col span={6}>
          <Statistic
            title="等待"
            value={waitingVehicles}
            suffix="台"
            prefix={<ClockCircleOutlined style={{ color: '#EF4444' }} />}
            valueStyle={{ color: '#EF4444' }}
          />
        </Col>
        
        <Col span={6}>
          <Statistic
            title="總計"
            value={totalVehicles}
            suffix="台"
            prefix={<CarOutlined />}
          />
        </Col>
      </Row>

      <div style={{ marginTop: '24px' }}>
        <div style={{ marginBottom: '8px', fontWeight: 500 }}>整體進度</div>
        <Progress 
          percent={progress} 
          status={progress === 100 ? 'success' : 'active'}
          strokeColor={{
            '0%': '#3B82F6',
            '100%': '#10B981',
          }}
        />
      </div>
    </Card>
  );
};

export default Dashboard;
