export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserStats extends User {
  total_sessions: number;
  total_retention_time: number;
  best_retention_time: number;
  current_streak: number;
  longest_streak: number;
  last_session_date: string | null;
}

export type UserProfile = UserStats;

export interface UserUpdateRequest {
  full_name?: string | null;
  avatar_url?: string | null;
}
