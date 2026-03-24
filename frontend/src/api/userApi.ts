import httpClient from './httpClient';
import type { PublicUserStats, User, UserProfile, UserStats, UserUpdateRequest } from '../types/user.types';

export const getProfile = async (): Promise<User> => {
  const res = await httpClient.get('/api/v1/users/me');
  return res.data;
};

export const updateProfile = async (data: UserUpdateRequest): Promise<User> => {
  const res = await httpClient.patch('/api/v1/users/me', data);
  return res.data;
};

export const getMyStats = async (): Promise<UserStats> => {
  const res = await httpClient.get<UserStats>('/api/v1/users/me/stats');
  return res.data;
};

export const getMyFullProfile = async (): Promise<UserProfile> => {
  const res = await httpClient.get<UserProfile>('/api/v1/users/me/profile');
  return res.data;
};

export const getLeaderboardByRetention = async (limit = 10): Promise<PublicUserStats[]> => {
  const res = await httpClient.get<PublicUserStats[]>('/api/v1/users/leaderboard/retention', {
    params: { limit },
  });
  return res.data;
};

export const getLeaderboardByStreak = async (limit = 10): Promise<PublicUserStats[]> => {
  const res = await httpClient.get<PublicUserStats[]>('/api/v1/users/leaderboard/streak', {
    params: { limit },
  });
  return res.data;
};

export const getLeaderboardByActive = async (limit = 10): Promise<PublicUserStats[]> => {
  const res = await httpClient.get<PublicUserStats[]>('/api/v1/users/leaderboard/active', {
    params: { limit },
  });
  return res.data;
};

export const searchUsers = async (query: string, limit = 10): Promise<User[]> => {
  const res = await httpClient.get<User[]>('/api/v1/users/search', {
    params: { q: query, limit },
  });
  return res.data;
};
