import { Card, List, Progress, Tag } from 'antd';
import useScheduleStore from '../store/scheduleStore';
import { SYSTEM_COLORS } from '../constants/colors';

const BatchProgress = () => {
  const { batches, vehicles, currentTime } = useScheduleStore();

  const getBatchProgress = (batchId) => {
    const batchVehicles = vehicles.filter(v => v.batch_id === batchId);
    if (batchVehicles.length === 0) return { completed: 0, inProgress: 0, waiting: 0, percent: 0 };
    
    const completed = batchVehicles.filter(v => typeof v.finish_time === 'number' && v.finish_time <= currentTime).length;
    const inProgress = batchVehicles.filter(v => {
      const start = typeof v.start_time === 'number' ? v.start_time : null;
      const finish = typeof v.finish_time === 'number' ? v.finish_time : null;
      if (start === null || start > currentTime) return false;
      if (finish === null) return true;
      return finish > currentTime;
    }).length;
    const waiting = Math.max(0, batchVehicles.length - completed - inProgress);
    const percent = Math.round((completed / batchVehicles.length) * 100);
    
    return { completed, inProgress, waiting, percent };
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'red';
      case 'normal': return 'blue';
      case 'low': return 'default';
      default: return 'default';
    }
  };

  return (
    <Card 
      title="批次進度" 
      style={{ 
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        maxHeight: '500px',
        overflow: 'auto'
      }}
    >
      <List
        dataSource={batches}
        renderItem={(batch) => {
          const progress = getBatchProgress(batch.batch_id);
          const systemColor = SYSTEM_COLORS[batch.system] || {};
          
          return (
            <List.Item>
              <div style={{ width: '100%' }}>
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  marginBottom: '8px'
                }}>
                  <div>
                    <Tag 
                      color={getPriorityColor(batch.priority)}
                      style={{ marginRight: '8px' }}
                    >
                      {batch.priority}
                    </Tag>
                    <span style={{ 
                      fontWeight: 500,
                      backgroundColor: systemColor.bg,
                      color: systemColor.text,
                      padding: '2px 8px',
                      borderRadius: '4px',
                      marginRight: '8px'
                    }}>
                      {batch.manufacturer} {batch.model}
                    </span>
                    <span style={{ color: '#666' }}>
                      ({batch.quantity}台)
                    </span>
                  </div>
                  
                  <span style={{ fontSize: '12px', color: '#999' }}>
                    完成: {progress.completed} | 進行: {progress.inProgress} | 等待: {progress.waiting}
                  </span>
                </div>
                
                <Progress 
                  percent={progress.percent} 
                  size="small"
                  status={progress.percent === 100 ? 'success' : 'active'}
                />
              </div>
            </List.Item>
          );
        }}
      />
    </Card>
  );
};

export default BatchProgress;
