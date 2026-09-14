export type WorkoutType = 'Endurance' | 'Tempo' | 'Seuil' | 'VO2 Max' | 'Sprint';

export interface WorkoutInterval {
  type: string;
  pace: string;
  duration?: number;
  distance?: number;
  repetitions: number;
}

export interface Workout {
  id: number;
  workout_type: WorkoutType;
  name: string;
  duration_minutes: number;
  difficulty_level: number;
  description_short: string;
  description_long: string;
  scheme: WorkoutInterval[] | null;
  date: string;
  is_validated: boolean;
  perceived_difficulty: number | null;
  athlete_comment: string | null;
  created_at: string;
  updated_at: string;
}
