import axios from "axios";

const API_BASE = "http://192.168.5.118:8000/api";
const WS_BASE = "ws://192.168.5.118:8000";
const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Token ${token}`;
  return config;
});

export const getWsUrl = (channelId) => {
  const token = localStorage.getItem("token");
  return `${WS_BASE}/ws/chat/${channelId}/?token=${token}`;
};

export default api;
