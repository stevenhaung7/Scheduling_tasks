import axios from 'axios';

// 根據環境自動切換 API URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const scheduleAPI = {
  // 創建排程
  createSchedule: async (orderFile) => {
    const response = await apiClient.post('/api/schedule', {
      order_file: orderFile,
    });
    return response.data;
  },

  // 獲取排程結果
  getScheduleResult: async () => {
    const response = await apiClient.get('/api/result');
    return response.data;
  },

  // 獲取指定時間的狀態
  getStateAtTime: async (time) => {
    const response = await apiClient.get(`/api/state/${time}`);
    return response.data;
  },

  // 獲取所有檢修廠狀態
  getStations: async () => {
    const response = await apiClient.get('/api/stations');
    return response.data;
  },
};

export const createWebSocket = (onMessage) => {
  // 根據 API URL 自動決定 WebSocket URL
  const wsProtocol = API_BASE_URL.startsWith('https') ? 'wss' : 'ws';
  const wsBaseUrl = API_BASE_URL.replace(/^https?/, wsProtocol);
  const ws = new WebSocket(`${wsBaseUrl}/ws/simulation`);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };
  
  ws.onerror = (error) => {
    console.warn('WebSocket error (這不影響基本功能，播放功能可能受限):', error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };
  
  return ws;
};

export const sendWebSocketCommand = (ws, command, params = {}) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ command, ...params }));
  }
};

export default apiClient;
