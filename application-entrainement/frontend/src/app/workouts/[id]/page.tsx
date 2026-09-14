'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { 
  ChevronLeft, 
  Clock, 
  Trophy, 
  AlignLeft, 
  Activity, 
  CheckCircle2, 
  AlertTriangle,
  Send,
  Calendar
} from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { fr } from 'date-fns/locale';
import Link from 'next/link';
import { Workout, WorkoutInterval } from '@/types/workout';

export default function WorkoutDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [workout, setWorkout] = useState<Workout | null>(null);
  const [loading, setLoading] = useState(true);
  const [perceivedDifficulty, setPerceivedDifficulty] = useState(5);
  const [comment, setComment] = useState('');
  const [isValidating, setIsValidating] = useState(false);

  useEffect(() => {
    fetchWorkout();
  }, [id]);

  const fetchWorkout = async () => {
    try {
      const response = await fetch(`/api/workouts/${id}`);
      if (!response.ok) throw new Error('Workout not found');
      const data = await response.json();
      setWorkout(data);
      if (data.is_validated) {
        setPerceivedDifficulty(data.perceived_difficulty || 5);
        setComment(data.athlete_comment || '');
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsValidating(true);
    try {
      const response = await fetch(`/api/workouts/${id}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          perceived_difficulty: perceivedDifficulty,
          athlete_comment: comment
        }),
      });
      if (response.ok) {
        const updated = await response.json();
        setWorkout(updated);
      }
    } catch (error) {
      console.error('Validation failed:', error);
    } finally {
      setIsValidating(false);
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center">Chargement...</div>;
  if (!workout) return <div className="min-h-screen flex items-center justify-center">Séance non trouvée</div>;

  return (
    <main className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors">
            <ChevronLeft className="w-5 h-5" />
            <span className="font-medium">Retour au calendrier</span>
          </Link>
          <div className="flex items-center gap-2">
            {workout.is_validated && (
              <span className="flex items-center gap-1 text-green-600 bg-green-50 px-3 py-1 rounded-full text-xs font-bold border border-green-200">
                <CheckCircle2 className="w-4 h-4" /> Validée
              </span>
            )}
            <span className="text-gray-400 text-sm">{format(parseISO(workout.date), 'd MMMM yyyy', { locale: fr })}</span>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 mt-8 space-y-8">
        {/* Main Info */}
        <section className="bg-white rounded-3xl p-8 shadow-sm border border-gray-100">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
            <div>
              <span className="inline-block px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800 uppercase mb-3">
                {workout.workout_type}
              </span>
              <h1 className="text-3xl md:text-4xl font-black text-gray-900 leading-tight">{workout.name}</h1>
            </div>
            <div className="flex gap-3">
              <div className="bg-blue-50 px-4 py-2 rounded-2xl flex flex-col items-center justify-center min-w-[80px]">
                <Clock className="w-5 h-5 text-blue-600 mb-1" />
                <span className="text-lg font-bold text-blue-900">{workout.duration_minutes}</span>
                <span className="text-[10px] text-blue-700 uppercase font-bold">Minutes</span>
              </div>
              <div className="bg-orange-50 px-4 py-2 rounded-2xl flex flex-col items-center justify-center min-w-[80px]">
                <Activity className="w-5 h-5 text-orange-600 mb-1" />
                <span className="text-lg font-bold text-orange-900">{workout.difficulty_level}</span>
                <span className="text-[10px] text-orange-700 uppercase font-bold">Cible</span>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-8 mt-8 border-t pt-8">
            <div className="space-y-4">
              <h3 className="flex items-center gap-2 font-bold text-gray-800 uppercase text-sm tracking-wider">
                <AlignLeft className="w-4 h-4 text-blue-500" /> Description
              </h3>
              <p className="text-gray-600 leading-relaxed font-medium">{workout.description_short}</p>
              <p className="text-gray-500 text-sm leading-relaxed">{workout.description_long}</p>
            </div>

            <div className="space-y-4">
              <h3 className="flex items-center gap-2 font-bold text-gray-800 uppercase text-sm tracking-wider">
                <Trophy className="w-4 h-4 text-yellow-500" /> Schéma d'entraînement
              </h3>
              <div className="space-y-3">
                {workout.scheme ? (
                  workout.scheme.map((interval: WorkoutInterval, idx: number) => (
                    <div key={idx} className="bg-gray-50 rounded-xl p-4 border border-gray-200 hover:border-blue-200 transition-colors">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-gray-900 text-sm">{interval.type}</span>
                        {interval.repetitions > 1 && (
                          <span className="bg-blue-600 text-white text-[10px] px-2 py-0.5 rounded-full font-bold">
                            x{interval.repetitions}
                          </span>
                        )}
                      </div>
                      <div className="flex items-baseline gap-4 text-sm">
                        <span className="text-blue-600 font-mono font-bold">{interval.pace} min/km</span>
                        {interval.duration && <span className="text-gray-500">{interval.duration} min</span>}
                        {interval.distance && <span className="text-gray-500">{interval.distance} km</span>}
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-400 italic text-sm">Aucun schéma défini pour cette séance.</p>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Validation Section */}
        <section className="bg-white rounded-3xl p-8 shadow-sm border border-gray-100 overflow-hidden relative">
          {!workout.is_validated && (
            <div className="absolute top-0 left-0 w-1.5 h-full bg-blue-500" />
          )}
          {workout.is_validated && (
            <div className="absolute top-0 left-0 w-1.5 h-full bg-green-500" />
          )}
          
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            {workout.is_validated ? 'Résumé de la séance' : 'Valider ma séance'}
          </h2>

          <form onSubmit={handleValidate} className="space-y-6">
            <div className="space-y-3">
              <label className="block font-bold text-gray-700 text-sm uppercase tracking-wider">
                Difficulté ressentie : <span className="text-blue-600 text-lg">{perceivedDifficulty}</span> / 10
              </label>
              <input 
                type="range" 
                min="1" 
                max="10" 
                step="1"
                value={perceivedDifficulty}
                onChange={(e) => setPerceivedDifficulty(parseInt(e.target.value))}
                disabled={workout.is_validated}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <div className="flex justify-between text-[10px] text-gray-400 font-bold uppercase px-1">
                <span>Facile</span>
                <span>Modéré</span>
                <span>Épuisant</span>
              </div>
            </div>

            <div className="space-y-3">
              <label className="block font-bold text-gray-700 text-sm uppercase tracking-wider">
                Commentaire de l'athlète
              </label>
              <textarea 
                rows={4}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                disabled={workout.is_validated}
                placeholder="Comment se sont passées les sensations ? Météo ? Douleurs éventuelles ?"
                className="w-full rounded-2xl border-gray-200 border p-4 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all disabled:bg-gray-50 disabled:text-gray-500"
              />
            </div>

            {!workout.is_validated && (
              <button 
                type="submit"
                disabled={isValidating}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-4 rounded-2xl transition-all shadow-xl hover:shadow-blue-200 flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isValidating ? 'Validation en cours...' : (
                  <>
                    <Send className="w-5 h-5" />
                    Valider la séance
                  </>
                )}
              </button>
            )}
            
            {workout.is_validated && (
              <div className="bg-green-50 rounded-2xl p-6 border border-green-100 flex items-start gap-4">
                <div className="bg-green-100 p-3 rounded-full">
                  <CheckCircle2 className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h4 className="text-green-900 font-bold">Séance enregistrée avec succès</h4>
                  <p className="text-green-700 text-sm mt-1">Bravo pour votre séance ! Vos retours ont été partagés avec votre coach.</p>
                </div>
              </div>
            )}
          </form>
        </section>
      </div>
    </main>
  );
}
