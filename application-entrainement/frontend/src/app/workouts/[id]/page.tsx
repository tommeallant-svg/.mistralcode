'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { 
  ChevronLeft, 
  Clock, 
  AlignLeft, 
  Activity, 
  CheckCircle2, 
  Send,
  Calendar,
  RotateCcw
} from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { fr } from 'date-fns/locale';
import Link from 'next/link';
import { Workout, WorkoutInterval, WorkoutBlock } from '@/types/workout';
import { fetchWithAuth } from '@/lib/api';

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
      const response = await fetchWithAuth(`/api/workouts/${id}`);
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
      const response = await fetchWithAuth(`/api/workouts/${id}/validate`, {
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
    <main className="min-h-screen bg-[#F8F9FA] pb-20 font-sans">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 h-20 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-black hover:opacity-70 transition-all group">
            <div className="p-2 bg-gray-100 rounded-xl group-hover:bg-black group-hover:text-white transition-all">
              <ChevronLeft className="w-5 h-5" />
            </div>
            <span className="font-black uppercase text-[10px] tracking-[0.2em]">Retour au calendrier</span>
          </Link>
          <div className="flex items-center gap-4">
            {workout.is_validated && (
              <span className="flex items-center gap-2 text-white bg-green-500 px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest shadow-lg shadow-green-100">
                <CheckCircle2 className="w-4 h-4" /> Validée
              </span>
            )}
            <span className="text-gray-400 font-bold uppercase text-[10px] tracking-widest">{format(parseISO(workout.date), 'd MMMM yyyy', { locale: fr })}</span>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 mt-12 space-y-12">
        {/* Main Info */}
        <section className="bg-white rounded-[3rem] p-10 md:p-16 shadow-[0_40px_80px_-20px_rgba(0,0,0,0.06)] border border-gray-50 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-3 h-full bg-black" />
          
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-10 mb-16">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-8">
                <span className="px-4 py-1.5 rounded-full text-[10px] font-black bg-yellow-400 text-black uppercase tracking-widest">
                  {workout.workout_type}
                </span>
                <span className="w-8 h-[2px] bg-gray-100" />
              </div>
              <h1 className="text-6xl md:text-8xl font-black text-black leading-[0.9] uppercase tracking-tighter mb-6">{workout.name}</h1>
              <div className="flex items-center gap-6 text-gray-400 font-black uppercase text-[10px] tracking-[0.2em]">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  {format(parseISO(workout.date), 'EEEE', { locale: fr })}
                </div>
              </div>
            </div>
            
            <div className="flex gap-4">
              <div className="bg-black text-white px-10 py-8 rounded-[2.5rem] flex flex-col items-center justify-center min-w-[140px] shadow-2xl shadow-black/20">
                <Clock className="w-8 h-8 mb-4 text-yellow-400" />
                <span className="text-4xl font-black leading-none">{workout.duration_minutes}</span>
                <span className="text-[10px] uppercase font-black tracking-widest mt-2 opacity-50">Minutes</span>
              </div>
              <div className="bg-gray-100 text-black px-10 py-8 rounded-[2.5rem] flex flex-col items-center justify-center min-w-[140px] border border-gray-200">
                <Activity className="w-8 h-8 mb-4 text-black" />
                <span className="text-4xl font-black leading-none">{workout.difficulty_level}</span>
                <span className="text-[10px] uppercase font-black tracking-widest mt-2 opacity-50">Intensité</span>
              </div>
            </div>
          </div>

          <div className="space-y-10 border-t border-gray-100 pt-16">
            <div className="max-w-3xl">
              <h4 className="font-black text-[10px] text-gray-400 uppercase tracking-[0.3em] mb-8 flex items-center gap-3">
                <div className="w-2 h-2 bg-black rounded-full" />
                Objectifs & Description
              </h4>
              <p className="text-gray-800 text-2xl md:text-3xl leading-snug font-medium italic tracking-tight">
                "{workout.description_long || workout.description_short}"
              </p>
            </div>

            {workout.scheme && workout.scheme.length > 0 && (
              <div className="pt-8">
                <h4 className="font-black text-[10px] text-gray-400 uppercase tracking-[0.3em] mb-8 flex items-center gap-3">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full" />
                  Structure de l'exercice
                </h4>
                <div className="space-y-6">
                  {workout.scheme.map((block: WorkoutBlock, bIdx: number) => (
                    <div key={bIdx} className="bg-gray-50 p-8 rounded-[2.5rem] border border-gray-100 relative group overflow-hidden">
                      <div className="absolute top-0 left-0 w-2 h-full bg-yellow-400 opacity-20 group-hover:opacity-100 transition-all" />
                      
                      {block.repetitions > 1 && (
                        <div className="flex items-center gap-2 mb-6 ml-2">
                          <div className="bg-black text-white p-2 rounded-xl">
                            <RotateCcw className="w-4 h-4" />
                          </div>
                          <span className="font-black text-[10px] uppercase tracking-[0.2em] text-black">Répéter {block.repetitions} fois</span>
                        </div>
                      )}

                      <div className="space-y-4">
                        {block.intervals.map((interval, iIdx) => (
                          <div key={iIdx} className="bg-white p-8 rounded-[2rem] border border-gray-100 flex flex-col md:flex-row md:items-center justify-between group/item hover:border-black transition-all shadow-sm">
                            <div className="flex items-center gap-8 mb-4 md:mb-0">
                              <div className="w-12 h-12 bg-gray-50 rounded-2xl flex items-center justify-center font-black text-black border border-gray-100 group-hover/item:bg-black group-hover/item:text-white transition-all">
                                {iIdx + 1}
                              </div>
                              <div>
                                <div className="font-black uppercase tracking-tighter text-xl mb-1">{interval.type}</div>
                                <div className="text-gray-400 font-bold text-[10px] uppercase tracking-widest flex items-center gap-2">
                                  <span className="w-2 h-[2px] bg-yellow-400" />
                                  Allure: {interval.pace_min} {interval.pace_max !== interval.pace_min ? `- ${interval.pace_max}` : ''}
                                </div>
                              </div>
                            </div>
                            <div className="flex md:block items-end justify-between border-t md:border-t-0 border-gray-200 pt-4 md:pt-0">
                              <span className="text-[10px] font-black uppercase tracking-widest text-gray-400 md:hidden">Volume</span>
                              <div className="text-4xl font-black tracking-tighter text-black">
                                {interval.duration || interval.distance}
                                <span className="text-sm ml-2 opacity-30 font-bold uppercase">{interval.duration !== undefined ? 'min' : 'm'}</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Validation Section */}
        <section className="bg-black text-white rounded-[3rem] p-10 md:p-16 shadow-[0_40px_80px_-20px_rgba(0,0,0,0.3)] relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-yellow-400 rounded-bl-[10rem] opacity-5 -mr-16 -mt-16" />
          
          {!workout.is_validated ? (
            <>
              <div className="flex items-center gap-4 mb-12">
                <div className="w-12 h-12 bg-yellow-400 rounded-2xl flex items-center justify-center">
                  <Activity className="w-6 h-6 text-black" />
                </div>
                <h2 className="text-4xl font-black uppercase tracking-tighter">Valider la séance</h2>
              </div>
              
              <form onSubmit={handleValidate} className="space-y-12 max-w-4xl">
                <div className="space-y-6">
                  <div className="flex justify-between items-end">
                    <label className="text-[10px] font-black uppercase tracking-[0.2em] opacity-40">Difficulté ressentie</label>
                    <div className="text-6xl font-black text-yellow-400 leading-none">{perceivedDifficulty}<span className="text-xl ml-2 opacity-30">/10</span></div>
                  </div>
                  <input 
                    type="range" 
                    min="1" 
                    max="10" 
                    step="1"
                    value={perceivedDifficulty}
                    onChange={(e) => setPerceivedDifficulty(parseInt(e.target.value))}
                    className="w-full h-4 bg-white/10 rounded-full appearance-none cursor-pointer accent-yellow-400"
                  />
                  <div className="flex justify-between text-[9px] font-black uppercase tracking-[0.3em] opacity-30">
                    <span>Facile</span>
                    <span>Modéré</span>
                    <span>Épuisant</span>
                  </div>
                </div>

                <div className="space-y-6">
                  <label className="text-[10px] font-black uppercase tracking-[0.2em] opacity-40 flex items-center gap-3">
                    <AlignLeft className="w-4 h-4 text-yellow-400" />
                    Compte-rendu de l'athlète
                  </label>
                  <textarea 
                    rows={6}
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="Quelles sont vos sensations ? Des points d'attention particuliers ?"
                    className="w-full bg-white/5 border border-white/10 rounded-[2rem] p-8 text-white text-lg placeholder:text-white/10 focus:outline-none focus:border-yellow-400 focus:bg-white/10 transition-all min-h-[180px] font-medium"
                  />
                </div>

                <button 
                  type="submit"
                  disabled={isValidating}
                  className="w-full bg-yellow-400 hover:bg-yellow-300 text-black font-black uppercase tracking-[0.2em] text-sm py-8 rounded-[2rem] transition-all shadow-[0_20px_40px_-10px_rgba(250,204,21,0.3)] active:scale-[0.98] flex items-center justify-center gap-4 disabled:opacity-50 group"
                >
                  {isValidating ? 'TRANSMISSION...' : (
                    <>
                      <Send className="w-5 h-5 transition-transform group-hover:translate-x-1 group-hover:-translate-y-1" />
                      ENREGISTRER LA SÉANCE
                    </>
                  )}
                </button>
              </form>
            </>
          ) : (
            <div className="space-y-12">
              <div className="flex items-center gap-4 mb-8">
                <div className="w-12 h-12 bg-green-500 rounded-2xl flex items-center justify-center">
                  <CheckCircle2 className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-4xl font-black uppercase tracking-tighter">Séance Enregistrée</h2>
              </div>
              
              <div className="grid md:grid-cols-3 gap-12 relative z-10">
                <div className="space-y-4">
                  <div className="text-[10px] font-black uppercase tracking-[0.2em] opacity-40 text-yellow-400">Ressenti</div>
                  <div className="text-7xl font-black">{workout.perceived_difficulty}<span className="text-2xl ml-2 opacity-20">/10</span></div>
                </div>
                <div className="md:col-span-2 space-y-4">
                  <div className="text-[10px] font-black uppercase tracking-[0.2em] opacity-40 text-yellow-400">Commentaires</div>
                  <div className="text-2xl font-medium italic leading-relaxed border-l-4 border-yellow-400 pl-8 py-2">
                    "{workout.athlete_comment || "Aucun commentaire laissé."}"
                  </div>
                </div>
              </div>
              
              <div className="pt-12 border-t border-white/10 mt-12 flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-green-500/20 rounded-full flex items-center justify-center">
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                  </div>
                  <div className="text-sm font-bold opacity-60">Transmission effectuée au coach</div>
                </div>
                <Link href="/" className="text-[10px] font-black uppercase tracking-[0.2em] hover:text-yellow-400 transition-colors">
                  Retour à la vue d'ensemble →
                </Link>
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
