import { useState, useEffect } from 'react';
import { Layout, Row, Col, Button, Select, message, Space } from 'antd';
import TimelineControl from './components/TimelineControl';
import Dashboard from './components/Dashboard';
import BatchProgress from './components/BatchProgress';
import StationView from './components/StationView';
import useScheduleStore from './store/scheduleStore';
import { scheduleAPI, createWebSocket } from './services/api';
import './App.css';

const { Header, Content } = Layout;
const { Option } = Select;

function App() {
  const [loading, setLoading] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState('test_orders_001.json');
  
  const {
    setScheduleResult,
    setBatches,
    setVehicles,
    setSchedules,
    setStations,
    setWebSocket,
    setMaxTime,
    fetchStateAtTime,
  } = useScheduleStore();

  // 初始化 WebSocket
  useEffect(() => {
    const ws = createWebSocket((data) => {
      if (data.type === 'state_update') {
        fetchStateAtTime(data.time);
      }
    });

    setWebSocket(ws);

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const handleLoadSchedule = async () => {
    setLoading(true);
    try {
      // 創建排程
      const result = await scheduleAPI.createSchedule(selectedOrder);
      message.success(`排程完成！共 ${result.total_batches} 批次，${result.total_vehicles} 台車輛`);
      
      // 獲取詳細結果
      const detailResult = await scheduleAPI.getScheduleResult();
      
      setScheduleResult(detailResult);
      setBatches(detailResult.batches);
      setVehicles(detailResult.vehicles);
      setSchedules(detailResult.schedules);
      setStations(detailResult.stations);
      
      // 設置最大時間
      if (detailResult.schedules.length > 0) {
        const maxTime = Math.max(...detailResult.schedules.map(s => s.finish_time));
        setMaxTime(maxTime);
      }
      
      // 獲取初始狀態
      await fetchStateAtTime(0);
      
    } catch (error) {
      message.error(`載入排程失敗: ${error.message}`);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
      <Header style={{ 
        background: '#001529', 
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <h1 style={{ 
          color: 'white', 
          margin: 0,
          fontSize: '20px'
        }}>
          車輛檢修排程系統
        </h1>
        
        <Space>
          <Select
            value={selectedOrder}
            onChange={setSelectedOrder}
            style={{ width: 200 }}
          >
            <Option value="test_orders_001.json">測試工單 001</Option>
            <Option value="test_orders_002.json">測試工單 002</Option>
            <Option value="test_orders_003.json">測試工單 003</Option>
          </Select>
          
          <Button 
            type="primary" 
            onClick={handleLoadSchedule}
            loading={loading}
          >
            載入排程
          </Button>
        </Space>
      </Header>

      <Content style={{ padding: '24px' }}>
        <Row gutter={[16, 16]}>
          {/* 時間軸控制 */}
          <Col span={24}>
            <TimelineControl />
          </Col>

          {/* 儀表板和批次進度 */}
          <Col span={12}>
            <Dashboard />
          </Col>
          
          <Col span={12}>
            <BatchProgress />
          </Col>

          {/* 檢修廠視圖 */}
          <Col span={24}>
            <StationView />
          </Col>
        </Row>
      </Content>
    </Layout>
  );
}

export default App;
