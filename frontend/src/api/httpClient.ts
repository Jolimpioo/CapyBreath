// Instância base do axios para requisições à API
import axios from 'axios';

const authWithCredentials =
  import.meta.env.VITE_AUTH_WITH_CREDENTIALS === 'true';

const httpClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  withCredentials: authWithCredentials,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Adiciona o token JWT em todas as requisições, se existir
httpClient.interceptors.request.use(
  config => {
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
      config.headers = config.headers || {};
      config.headers['Authorization'] = `Bearer ${accessToken}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Interceptor de resposta para lidar com refresh automático do token
httpClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    const isAuthRefreshCall = originalRequest?.url?.includes(
      '/api/v1/auth/refresh'
    );

    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry &&
      !isAuthRefreshCall
    ) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) throw error;

        const res = await httpClient.post('/api/v1/auth/refresh', {
          refresh_token: refreshToken,
        });

        const { access_token } = res.data;
        localStorage.setItem('accessToken', access_token);

        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers['Authorization'] = `Bearer ${access_token}`;

        return httpClient(originalRequest);
      } catch (refreshError) {
        // Logout automático se o refresh falhar
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default httpClient;
