export type WorkoutType = 'Endurance' | 'Tempo' | 'Seuil' | 'VO2 Max' | 'Sprint' | 'Libre' | 'Trail' | 'Fractionné' | 'Sortie Longue';

export interface WorkoutInterval {
  type: string;
  pace: string;
  duration?: number;
  distance?: number;
  repetitions: number;
}

export interface Workout {
  id: number;
  workout_type: string;
  category: string;
  name: string;
  duration_minutes: number;
  distance_km: number | null;
  difficulty_level: number;
  estimated_load: number | null;
  description_short: string;
  description_long: string;
  scheme: WorkoutInterval[] | null;
  date: string;
  is_validated: boolean;
  perceived_difficulty: number | null;
  athlete_comment: string | null;
  plan_id: number | null;
  athlete_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface CatalogInterval {
  type: string;
  pace_vma: number; // en %
  duration?: number;
  distance?: number;
  repetitions: number;
}

export interface CatalogWorkout {
  id: number;
  name: string;
  workout_type: string;
  category: string;
  perceived_difficulty: number;
  scheme: CatalogInterval[];
}
