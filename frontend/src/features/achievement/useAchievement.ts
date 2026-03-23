import { useCallback, useState } from 'react';
import {
  checkAchievements,
  getAchievements,
  getAchievementsByCategory,
  getAchievementsByRarity,
  getMyAchievementDetail,
  getMyAchievements,
} from '../../api/achievementApi';
import { getApiErrorMessage } from '../../api/apiError';
import type {
  Achievement,
  AchievementCatalogFilters,
  AchievementDetail,
  CheckAchievementsResponse,
  UserAchievementsResponse,
} from '../../types/achievement.types';

export const useAchievement = () => {
  const [catalog, setCatalog] = useState<Achievement[]>([]);
  const [userAchievements, setUserAchievements] =
    useState<UserAchievementsResponse | null>(null);
  const [selectedAchievement, setSelectedAchievement] = useState<AchievementDetail | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCatalog = useCallback(
    async (filters: AchievementCatalogFilters = {}) => {
      setLoading(true);
      setError(null);
      try {
        let data: Achievement[];

        if (filters.category && filters.category !== 'all') {
          data = await getAchievementsByCategory(filters.category);
        } else if (filters.rarity && filters.rarity !== 'all') {
          data = await getAchievementsByRarity(filters.rarity);
        } else {
          data = await getAchievements();
        }

        if (filters.category && filters.category !== 'all') {
          data = data.filter(item =>
            filters.rarity && filters.rarity !== 'all'
              ? item.rarity === filters.rarity
              : true
          );
        }

        if (filters.rarity && filters.rarity !== 'all') {
          data = data.filter(item =>
            filters.category && filters.category !== 'all'
              ? item.category === filters.category
              : true
          );
        }

        setCatalog(data);
        return data;
      } catch (error) {
        const message = getApiErrorMessage(
          error,
          'Erro ao buscar catálogo de conquistas'
        );
        setError(message);
        throw new Error(message);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const fetchMyAchievements = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getMyAchievements();
      setUserAchievements(data);
      return data;
    } catch (error) {
      const message = getApiErrorMessage(
        error,
        'Erro ao buscar suas conquistas'
      );
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchAchievementDetail = useCallback(async (achievementId: string) => {
    setDetailLoading(true);
    setError(null);
    try {
      const data = await getMyAchievementDetail(achievementId);
      setSelectedAchievement(data);
      return data;
    } catch (error) {
      const message = getApiErrorMessage(
        error,
        'Erro ao buscar detalhe da conquista'
      );
      setError(message);
      throw new Error(message);
    } finally {
      setDetailLoading(false);
    }
  }, []);

  const clearSelectedAchievement = useCallback(() => {
    setSelectedAchievement(null);
  }, []);

  const checkAndUnlock = useCallback(async (): Promise<CheckAchievementsResponse> => {
    setLoading(true);
    setError(null);
    try {
      const result = await checkAchievements();
      const mine = await getMyAchievements();
      setUserAchievements(mine);
      return result;
    } catch (error) {
      const message = getApiErrorMessage(error, 'Erro ao verificar conquistas');
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    catalog,
    userAchievements,
    selectedAchievement,
    loading,
    detailLoading,
    error,
    fetchCatalog,
    fetchMyAchievements,
    fetchAchievementDetail,
    clearSelectedAchievement,
    checkAndUnlock,
  };
};
