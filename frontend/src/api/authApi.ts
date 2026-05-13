import httpClient, { authWithCredentials } from './httpClient';
import type {
  AccessTokenResponse,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  TokenResponse,
} from '../types/auth.types';

const storeTokens = (
  tokens: Pick<TokenResponse, 'access_token' | 'refresh_token'>
) => {
  localStorage.setItem('accessToken', tokens.access_token);
  if (authWithCredentials) {
    localStorage.removeItem('refreshToken');
    return;
  }

  if (tokens.refresh_token) {
    localStorage.setItem('refreshToken', tokens.refresh_token);
  }
};

export const login = async (data: LoginRequest) => {
  const response = await httpClient.post<LoginResponse>(
    '/api/v1/auth/login',
    data
  );
  storeTokens(response.data.tokens);
  return response;
};

export const register = async (data: RegisterRequest) => {
  const response = await httpClient.post<RegisterResponse>(
    '/api/v1/auth/register',
    data
  );
  storeTokens(response.data.tokens);
  return response;
};

export const refreshToken = async (refresh_token?: string) => {
  const payload = refresh_token ? { refresh_token } : {};
  const response = await httpClient.post<AccessTokenResponse>(
    '/api/v1/auth/refresh',
    payload
  );
  localStorage.setItem('accessToken', response.data.access_token);
  return response;
};

export const logout = async () => {
  try {
    await httpClient.post('/api/v1/auth/logout');
  } finally {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  }
};
