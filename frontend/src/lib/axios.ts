import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL as string || "http://127.0.0.1:14201/api/v1";

export const apiClient = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' },
    timeout: 20000, 
});

apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error("API Error:", error.response?.data || error.message);
        return Promise.reject(error);
    }
);