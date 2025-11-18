import { useState } from 'react';
import { Button, Slider, Space, Typography } from 'antd';
import { 
  PlayCircleOutlined, 
  PauseCircleOutlined, 
  ReloadOutlined,
  FastForwardOutlined,
} from '@ant-design/icons';
import useScheduleStore from '../store/scheduleStore';

const { Text } = Typography;

const TimelineControl = () => {
  const {
    currentTime,
    maxTime,
    isPlaying,
    speed,
    play,
    pause,
    reset,
    seek,
    changeSpeed,
    setCurrentTime,
  } = useScheduleStore();

  const formatTime = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}:${mins.toString().padStart(2, '0')}`;
  };

  const handleSpeedChange = () => {
    const speeds = [1, 2, 4];
    const currentIndex = speeds.indexOf(speed);
    const nextSpeed = speeds[(currentIndex + 1) % speeds.length];
    changeSpeed(nextSpeed);
  };

  return (
    <div style={{ 
      padding: '20px', 
      background: '#fff', 
      borderRadius: '8px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
    }}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* 控制按鈕 */}
        <Space size="middle">
          <Button
            type="primary"
            icon={isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
            onClick={isPlaying ? pause : play}
            size="large"
          >
            {isPlaying ? '暫停' : '播放'}
          </Button>
          
          <Button
            icon={<ReloadOutlined />}
            onClick={reset}
            size="large"
          >
            重置
          </Button>
          
          <Button
            icon={<FastForwardOutlined />}
            onClick={handleSpeedChange}
            size="large"
          >
            {speed}x
          </Button>
          
          <Text strong style={{ fontSize: '16px', marginLeft: '20px' }}>
            當前時間: {formatTime(currentTime)} / {formatTime(maxTime)}
          </Text>
        </Space>

        {/* 時間軸滑桿 */}
        <Slider
          min={0}
          max={maxTime}
          value={currentTime}
          onChange={(value) => setCurrentTime(value)}
          onAfterChange={(value) => seek(value)}
          tooltip={{
            formatter: (value) => formatTime(value),
          }}
          style={{ width: '100%' }}
        />
      </Space>
    </div>
  );
};

export default TimelineControl;
