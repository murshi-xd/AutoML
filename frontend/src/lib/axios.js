import axios from 'axios';

// Create an Axios instance for the backend API
const api = axios.create({
    baseURL: 'http://localhost:5004/',
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000,
});

// Add a response interceptor for error handling
api.interceptors.response.use(
    response => response,
    error => {
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);

export default api;


