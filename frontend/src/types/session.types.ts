export interface Session {
  id: string;
  user_id: string;
  session_group_id: string;
  round_number: number;
  total_rounds: number;
  breaths_count: number;
  retention_time: number;
  recovery_time: number;
  session_date: string;
  duration_seconds: number;
  notes: string | null;
  mood_before: number | null;
  mood_after: number | null;
  technique_variant: string;
  created_at: string;
  updated_at: string;
}

export interface SessionDetail extends Session {
  is_personal_best: boolean;
}

export interface SessionUnlockedAchievement {
  achievement_id: string;
  name: string;
  description: string;
  icon: string;
  points: number;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  unlocked_at: string;
}

export interface SessionCreateResponse extends SessionDetail {
  newly_unlocked: SessionUnlockedAchievement[];
}

export interface SessionListItem {
  id: string;
  session_group_id: string;
  round_number: number;
  total_rounds: number;
  breaths_count: number;
  retention_time: number;
  session_date: string;
  technique_variant: string;
  mood_improvement: number | null;
  is_personal_best: boolean;
}

export interface PaginatedSessionsResponse {
  items: SessionListItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface SessionCreateRequest {
  session_group_id?: string;
  round_number?: number;
  total_rounds?: number;
  breaths_count?: number;
  retention_time: number;
  recovery_time?: number;
  duration_seconds: number;
  notes?: string;
  mood_before?: number;
  mood_after?: number;
  technique_variant?: 'standard' | 'advanced' | 'beginner' | 'power';
}

export interface SessionUpdateRequest {
  notes?: string | null;
  mood_before?: number | null;
  mood_after?: number | null;
}

export interface SessionPeriodStats {
  sessions_count: number;
  total_retention_time: number;
  average_retention_time: number;
  best_retention_time: number;
}

export interface SessionsSummary {
  total_sessions: number;
  total_retention_time: number;
  average_retention_time: number;
  best_retention_time: number;
  current_streak: number;
  longest_streak: number;
  total_breaths: number;
  last_7_days: SessionPeriodStats;
  last_30_days: SessionPeriodStats;
}

export interface ProgressDataPoint {
  date: string;
  sessions_count: number;
  total_retention_time: number;
  average_retention_time: number;
  best_retention_time: number;
}

export interface ProgressResponse {
  data_points: ProgressDataPoint[];
  period_days: number;
  trend: 'improving' | 'stable' | 'declining';
}

export interface MoodCorrelationResponse {
  average_mood_before: number;
  average_mood_after: number;
  average_improvement: number;
  correlation_retention_improvement: number;
  sessions_with_mood: number;
}

export interface SessionQueryParams {
  page?: number;
  size?: number;
  order_by?: string;
  order_dir?: 'asc' | 'desc';
}
