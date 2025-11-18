import { create } from 'zustand';
import { scheduleAPI } from '../services/api';

const useScheduleStore = create((set, get) => ({
  // 排程數據
  scheduleResult: null,
  stations: [],
  batches: [],
  vehicles: [],
  schedules: [],
  
  // 模擬狀態
  currentTime: 0,
  maxTime: 2000,
  isPlaying: false,
  speed: 1,
  currentState: null,
  
  // WebSocket
  ws: null,
  
  // Actions
  setScheduleResult: (result) => set({ scheduleResult: result }),
  
  setStations: (stations) => set({ stations }),
  
  setBatches: (batches) => set({ batches }),
  
  setVehicles: (vehicles) => set({ vehicles }),
  
  setSchedules: (schedules) => set({ schedules }),
  
  setCurrentTime: (time) => set({ currentTime: time }),
  
  setMaxTime: (time) => set({ maxTime: time }),
  
  setIsPlaying: (playing) => set({ isPlaying: playing }),
  
  setSpeed: (speed) => set({ speed }),
  
  setCurrentState: (state) => set({ currentState: state }),
  
  setWebSocket: (ws) => set({ ws }),
  
  fetchStateAtTime: async (time) => {
    const targetTime = typeof time === 'number' ? time : get().currentTime;
    try {
      const state = await scheduleAPI.getStateAtTime(targetTime);
      set({ currentState: state, currentTime: targetTime });
    } catch (error) {
      console.error('無法取得指定時間的狀態', error);
    }
  },
  
  // 控制命令
  play: () => {
    const { ws } = get();
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ command: 'play' }));
      set({ isPlaying: true });
    }
  },
  
  pause: () => {
    const { ws } = get();
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ command: 'pause' }));
      set({ isPlaying: false });
    }
  },
  
  reset: () => {
    const { ws, fetchStateAtTime } = get();
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ command: 'reset' }));
      set({ currentTime: 0, isPlaying: false });
      fetchStateAtTime(0);
    }
  },
  
  seek: (time) => {
    const { ws, fetchStateAtTime } = get();
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ command: 'seek', time }));
      set({ currentTime: time });
    }
    fetchStateAtTime(time);
  },
  
  changeSpeed: (speed) => {
    const { ws } = get();
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ command: 'speed', value: speed }));
      set({ speed });
    }
  },
}));

export default useScheduleStore;
