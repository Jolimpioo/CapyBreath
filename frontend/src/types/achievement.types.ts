export type AchievementRarity = 'common' | 'rare' | 'epic' | 'legendary';

export type AchievementCategory =
  | 'sessions'
  | 'retention'
  | 'streak'
  | 'improvement'
  | 'milestone';

export interface Achievement {
  id: string;
  name: string;
  description: string;
  category: AchievementCategory;
  rarity: AchievementRarity;
  icon: string;
  points: number;
  criteria_type: string;
  criteria_value: number;
  is_active: boolean;
  is_hidden: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface AchievementProgress {
  current: number;
  target: number;
  percentage: number;
}

export interface UnlockedAchievement extends Achievement {
  unlocked_at: string;
  is_recent: boolean;
}

export interface LockedAchievement extends Achievement {
  progress: AchievementProgress;
}

export interface AchievementDetail extends Achievement {
  unlocked: boolean;
  unlocked_at: string | null;
  progress: AchievementProgress | null;
}

export interface UserAchievementsResponse {
  unlocked: UnlockedAchievement[];
  locked: LockedAchievement[];
  total_points: number;
  unlocked_count: number;
  total_count: number;
}

export interface CheckAchievementsResponse {
  newly_unlocked: UnlockedAchievement[];
  count: number;
  message: string;
}

export interface AchievementCatalogFilters {
  category?: AchievementCategory | 'all';
  rarity?: AchievementRarity | 'all';
}
