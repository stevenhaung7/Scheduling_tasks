import { useMemo } from 'react';
import { Card, Tag } from 'antd';
import useScheduleStore from '../store/scheduleStore';
import { SYSTEM_COLORS, STAGE_COLORS } from '../constants/colors';

const StationView = () => {
  const { currentState, stations, batches, vehicles } = useScheduleStore();

  const stationStatusMap = {
    setup: { label: '換線中', color: '#fa8c16' },
    running: { label: '生產中', color: '#3B82F6' },
    idle: { label: '待命', color: '#999999' },
  };

  const vehicleMap = useMemo(() => {
    const map = {};
    vehicles.forEach((vehicle) => {
      map[vehicle.vehicle_id] = vehicle;
    });
    return map;
  }, [vehicles]);

  const batchMap = useMemo(() => {
    const map = {};
    batches.forEach((batch) => {
      map[batch.batch_id] = batch;
    });
    return map;
  }, [batches]);

  const renderWorkstation = (ws) => {
    const vehicleInfo = ws.current_vehicle ? vehicleMap[ws.current_vehicle] : null;
    const systemColor = vehicleInfo ? (SYSTEM_COLORS[vehicleInfo.system] || {}) : {};
    const isBusy = ws.status === 'busy' && !!vehicleInfo;
    const isEmpty = !vehicleInfo;
    
    return (
      <div
        key={ws.workstation_id}
        style={{
          width: '100px',
          height: '60px',
          border: isBusy ? '2px solid #1890ff' : '2px dashed #d9d9d9',
          borderRadius: '4px',
          margin: '4px',
          display: 'inline-flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: isEmpty ? '#fafafa' : systemColor.bg || '#fff',
          fontSize: '12px',
          padding: '4px',
        }}
      >
        {isEmpty ? (
          <span style={{ color: '#999' }}>空</span>
        ) : (
          <>
            <div style={{ 
              fontWeight: 500, 
              color: systemColor.text,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              width: '90px',
              textAlign: 'center'
            }}>
              {vehicleInfo?.batch_id || ws.current_vehicle?.split('_')[0]}
            </div>
            <div style={{ 
              fontSize: '11px',
              color: systemColor.text || '#333',
              opacity: 0.8
            }}>
              {vehicleInfo?.model || ws.current_vehicle?.split('_').slice(1).join('_')}
            </div>
          </>
        )}
      </div>
    );
  };

  const renderStage = (stage, stageIndex) => {
    return (
      <div 
        key={stage.stage_number}
        style={{
          padding: '12px',
          backgroundColor: STAGE_COLORS[stageIndex],
          borderRadius: '4px',
          marginBottom: '8px'
        }}
      >
        <div style={{ 
          fontWeight: 500, 
          marginBottom: '8px',
          fontSize: '13px'
        }}>
          站{stage.stage_number} - {stage.stage_name}
        </div>
        <div style={{ 
          display: 'flex', 
          flexWrap: 'wrap',
          gap: '4px'
        }}>
          {stage.workstations.map(ws => renderWorkstation(ws))}
        </div>
      </div>
    );
  };

  const renderStation = (stationName) => {
    if (!currentState?.stations?.[stationName]) {
      return (
        <Card 
          title={stationName}
          style={{ marginBottom: '16px' }}
        >
          <div style={{ textAlign: 'center', color: '#999', padding: '20px' }}>
            暫無數據
          </div>
        </Card>
      );
    }

    const stationData = currentState.stations[stationName];
    const stationInfo = stations.find(s => s.station_name === stationName);
    const currentBatch = stationData.current_batch || stationInfo?.current_batch;
    const batchInfo = currentBatch ? batchMap[currentBatch] : null;
    const systemColor = batchInfo ? SYSTEM_COLORS[batchInfo.system] : null;

    return (
      <Card 
        title={stationName}
        extra={
          stationData.current_batch && (
            <span style={{ fontSize: '12px', color: '#666' }}>
              當前批次: {stationData.current_batch}
            </span>
          )
        }
        style={{ 
          marginBottom: '16px',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}
      >
        <div style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>
            狀態：
            <span style={{ color: (stationStatusMap[stationData.status]?.color) || '#555', fontWeight: 500 }}>
              {stationStatusMap[stationData.status]?.label || stationStatusMap.idle.label}
            </span>
          </span>
          {batchInfo && (
            <Tag color={systemColor?.text || '#333'} style={{ backgroundColor: systemColor?.bg || '#fff' }}>
              {batchInfo.system}
            </Tag>
          )}
        </div>
        {stationData.status === 'setup' ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '20px',
            backgroundColor: '#fff7e6',
            borderRadius: '4px'
          }}>
            <div style={{ fontSize: '16px', fontWeight: 500, color: '#fa8c16' }}>
              換線中
            </div>
          </div>
        ) : (
          stationData.stages.map((stage, index) => 
            renderStage(stage, index)
          )
        )}
      </Card>
    );
  };

  const stationNames = [
    '南高檢修廠',
    '北高檢修廠',
    '鳳山檢修廠',
    '楠梓檢修廠',
    '岡山檢修廠',
  ];

  return (
    <div style={{ padding: '16px' }}>
      <h2 style={{ marginBottom: '16px' }}>檢修廠工位狀態</h2>
      {stationNames.map(name => (
        <div key={name}>
          {renderStation(name)}
        </div>
      ))}
    </div>
  );
};

export default StationView;
