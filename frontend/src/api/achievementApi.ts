import httpClient from './httpClient';
import type {
  Achievement,
  AchievementCategory,
  AchievementDetail,
  AchievementRarity,
  CheckAchievementsResponse,
  UserAchievementsResponse,
} from '../types/achievement.types';

export const getAchievements = async (): Promise<Achievement[]> => {
  const res = await httpClient.get<Achievement[]>('/api/v1/achievements');
  return res.data;
};

export const getAchievementsByCategory = async (
  category: AchievementCategory
): Promise<Achievement[]> => {
  const res = await httpClient.get<Achievement[]>(
    `/api/v1/achievements/category/${category}`
  );
  return res.data;
};

export const getAchievementsByRarity = async (
  rarity: AchievementRarity
): Promise<Achievement[]> => {
  const res = await httpClient.get<Achievement[]>(
    `/api/v1/achievements/rarity/${rarity}`
  );
  return res.data;
};

export const getMyAchievements = async (): Promise<UserAchievementsResponse> => {
  const res = await httpClient.get<UserAchievementsResponse>(
    '/api/v1/achievements/me'
  );
  return res.data;
};

export const getMyAchievementDetail = async (
  achievementId: string
): Promise<AchievementDetail> => {
  const res = await httpClient.get<AchievementDetail>(
    `/api/v1/achievements/me/${achievementId}`
  );
  return res.data;
};

export const checkAchievements = async (): Promise<CheckAchievementsResponse> => {
  const res = await httpClient.post<CheckAchievementsResponse>(
    '/api/v1/achievements/check'
  );
  return res.data;
};
