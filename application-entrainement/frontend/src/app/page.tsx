'use client';

import React, { useState, useEffect } from 'react';
import { 
  format, 
  startOfMonth, 
  endOfMonth, 
  startOfWeek, 
  endOfWeek, 
  eachDayOfInterval, 
  isSameMonth, 
  isSameDay, 
  addMonths, 
  subMonths, 
  addWeeks, 
  subWeeks,
  parseISO,
  setDay
} from 'date-fns';
import { fr } from 'date-fns/locale';
import { 
  ChevronLeft, 
  ChevronRight, 
  Calendar as CalendarIcon, 
  LayoutList,
  ExternalLink,
  X,
  CheckCircle2,
  Clock,
  ArrowRightLeft,
  Activity,
  AlignLeft
} from 'lucide-react';
import Link from 'next/link';
import { Workout } from '@/types/workout';

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<'month' | 'week'>('month');
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [selectedWorkout, setSelectedWorkout] = useState<Workout | null>(null);
  const [isSideMenuOpen, setIsSideMenuOpen] = useState(false);

  useEffect(() => {
    fetchWorkouts();
  }, []);

  const fetchWorkouts = async () => {
    try {
      const response = await fetch('/api/workouts');
      const data = await response.json();
      if (Array.isArray(data)) {
        setWorkouts(data);
      } else {
        console.error('Data is not an array:', data);
        setWorkouts([]);
      }
    } catch (error) {
      console.error('Failed to fetch workouts:', error);
      setWorkouts([]);
    }
  };

  const next = () => {
    if (view === 'month') setCurrentDate(addMonths(currentDate, 1));
    else setCurrentDate(addWeeks(currentDate, 1));
  };

  const prev = () => {
    if (view === 'month') setCurrentDate(subMonths(currentDate, 1));
    else setCurrentDate(subWeeks(currentDate, 1));
  };

  const handleWorkoutClick = (workout: Workout) => {
    setSelectedWorkout(workout);
    setIsSideMenuOpen(true);
  };

  const shiftWorkout = async (workout: Workout, newDate: Date) => {
    try {
      const response = await fetch(`/api/workouts/${workout.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: newDate.toISOString() }),
      });
      if (response.ok) {
        fetchWorkouts();
        if (selectedWorkout?.id === workout.id) {
          const updated = await response.json();
          setSelectedWorkout(updated);
        }
      }
    } catch (error) {
      console.error('Failed to shift workout:', error);
    }
  };

  const renderHeader = () => (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
      <div className="flex flex-col gap-2">
        <h1 className="text-5xl font-black text-black tracking-tighter uppercase leading-none">
          {format(currentDate, 'MMMM yyyy', { locale: fr })}
        </h1>
        <div className="flex items-center gap-2 text-gray-400 font-bold uppercase text-xs tracking-widest">
          <CalendarIcon className="w-4 h-4" />
          <span>Tableau de Bord Entraînement</span>
        </div>
      </div>
      
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center bg-gray-100 rounded-2xl p-1.5 border border-gray-200">
          <button 
            onClick={() => setView('month')}
            className={`px-6 py-2 rounded-xl text-sm font-black transition-all ${view === 'month' ? 'bg-black text-white shadow-lg' : 'text-gray-500 hover:text-black'}`}
          >
            MOIS
          </button>
          <button 
            onClick={() => setView('week')}
            className={`px-6 py-2 rounded-xl text-sm font-black transition-all ${view === 'week' ? 'bg-black text-white shadow-lg' : 'text-gray-500 hover:text-black'}`}
          >
            SEMAINE
          </button>
        </div>

        <div className="flex items-center gap-2 bg-white rounded-2xl p-1.5 border border-gray-200">
          <button onClick={prev} className="p-2 hover:bg-gray-100 rounded-xl transition-colors">
            <ChevronLeft className="w-6 h-6" />
          </button>
          <button 
            onClick={() => setCurrentDate(new Date())}
            className="px-4 py-2 hover:bg-gray-100 rounded-xl text-xs font-black uppercase tracking-wider"
          >
            Aujourd'hui
          </button>
          <button onClick={next} className="p-2 hover:bg-gray-100 rounded-xl transition-colors">
            <ChevronRight className="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>
  );

  const renderDays = () => {
    const days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
    return (
      <div className="grid grid-cols-7 mb-0 bg-black text-white rounded-t-2xl">
        {days.map(day => (
          <div key={day} className="py-4 text-center text-xs font-black uppercase tracking-widest border-r border-white/10 last:border-r-0">
            {day}
          </div>
        ))}
      </div>
    );
  };

  const renderCells = () => {
    const monthStart = startOfMonth(currentDate);
    const monthEnd = endOfMonth(monthStart);
    const startDate = startOfWeek(view === 'month' ? monthStart : currentDate, { weekStartsOn: 1 });
    const endDate = endOfWeek(view === 'month' ? monthEnd : currentDate, { weekStartsOn: 1 });

    const days = eachDayOfInterval({ start: startDate, end: endDate });

    return (
      <div className="grid grid-cols-7 auto-rows-fr border-l border-b border-gray-200">
        {days.map((day, idx) => {
          const dayWorkouts = (Array.isArray(workouts) ? workouts : []).filter(w => isSameDay(parseISO(w.date), day));
          const isToday = isSameDay(day, new Date());
          const isNotCurrentMonth = !isSameMonth(day, monthStart) && view === 'month';

          return (
            <div 
              key={idx}
              className={`min-h-[160px] p-3 border-r border-t border-gray-200 transition-all ${
                isNotCurrentMonth ? 'bg-gray-50/50 text-gray-300' : 'bg-white'
              } ${isToday ? 'bg-yellow-50/50' : ''}`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className={`text-sm font-black tracking-tighter ${
                  isToday 
                    ? 'bg-black text-white w-8 h-8 flex items-center justify-center rounded-lg shadow-lg' 
                    : isNotCurrentMonth ? 'text-gray-300' : 'text-gray-400'
                }`}>
                  {format(day, 'd')}
                </span>
              </div>
              <div className="space-y-2">
                {dayWorkouts.map(workout => (
                  <div 
                    key={workout.id}
                    onClick={() => handleWorkoutClick(workout)}
                    className={`p-3 rounded-xl cursor-pointer text-xs border-2 transition-all hover:scale-[1.02] hover:shadow-xl active:scale-[0.98] ${
                      workout.is_validated 
                        ? 'bg-white border-green-500 text-black' 
                        : 'bg-black border-black text-white'
                    }`}
                  >
                    <div className="font-black uppercase tracking-tighter flex items-center justify-between mb-1">
                      <span className="truncate">{workout.workout_type}</span>
                      {workout.is_validated && <CheckCircle2 className="w-3 h-3 text-green-500" />}
                    </div>
                    <div className={`truncate font-bold opacity-80 ${workout.is_validated ? 'text-gray-600' : 'text-gray-300'}`}>
                      {workout.name}
                    </div>
                    <div className="flex items-center gap-1 mt-2 font-black uppercase text-[9px] tracking-widest">
                      <Clock className="w-3 h-3" />
                      {workout.duration_minutes} MIN
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderSideMenu = () => {
    if (!selectedWorkout) return null;

    // Get current week days for shifting
    const weekStart = startOfWeek(parseISO(selectedWorkout.date), { weekStartsOn: 1 });
    const weekDays = eachDayOfInterval({
      start: weekStart,
      end: endOfWeek(weekStart, { weekStartsOn: 1 })
    });

    return (
      <div className={`fixed inset-y-0 right-0 w-full md:w-[450px] bg-white shadow-[-20px_0_50px_rgba(0,0,0,0.1)] transform transition-transform duration-500 ease-in-out z-50 ${isSideMenuOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        <div className="p-8 h-full flex flex-col">
          <div className="flex items-center justify-between mb-10">
            <div className="flex items-center gap-2">
              <div className="w-3 h-8 bg-black rounded-full" />
              <h2 className="text-2xl font-black text-black uppercase tracking-tighter">Détails</h2>
            </div>
            <button onClick={() => setIsSideMenuOpen(false)} className="p-2 hover:bg-gray-100 rounded-xl transition-colors">
              <X className="w-8 h-8 text-black" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-8 pr-2 custom-scrollbar">
            <div>
              <span className="inline-block px-4 py-1.5 rounded-full text-[10px] font-black bg-yellow-400 text-black uppercase tracking-widest mb-4">
                {selectedWorkout.workout_type}
              </span>
              <h3 className="text-4xl font-black text-black leading-none uppercase tracking-tighter">{selectedWorkout.name}</h3>
              <p className="text-gray-400 font-bold mt-4 uppercase text-xs tracking-widest">{format(parseISO(selectedWorkout.date), 'EEEE d MMMM yyyy', { locale: fr })}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 border border-gray-100 p-5 rounded-3xl">
                <div className="text-gray-400 text-[10px] font-black uppercase tracking-widest mb-2">Durée</div>
                <div className="text-2xl font-black flex items-center gap-2">
                  <Clock className="w-5 h-5 text-black" />
                  {selectedWorkout.duration_minutes}<span className="text-sm">MIN</span>
                </div>
              </div>
              <div className="bg-gray-50 border border-gray-100 p-5 rounded-3xl">
                <div className="text-gray-400 text-[10px] font-black uppercase tracking-widest mb-2">Intensité</div>
                <div className="text-2xl font-black flex items-center gap-2">
                  <Activity className="w-5 h-5 text-black" />
                  {selectedWorkout.difficulty_level}<span className="text-sm">/10</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-black text-xs text-black uppercase tracking-widest mb-4 flex items-center gap-2">
                <AlignLeft className="w-4 h-4" />
                Description
              </h4>
              <p className="text-gray-600 text-sm leading-relaxed font-medium bg-gray-50 p-6 rounded-3xl border border-gray-100 italic">
                "{selectedWorkout.description_short}"
              </p>
            </div>

            <div>
              <h4 className="font-black text-xs text-black uppercase tracking-widest mb-4">Déplacer la séance</h4>
              <div className="grid grid-cols-7 gap-2">
                {weekDays.map(day => {
                  const isCurrent = isSameDay(day, parseISO(selectedWorkout.date));
                  return (
                    <button
                      key={day.toISOString()}
                      onClick={() => shiftWorkout(selectedWorkout, day)}
                      disabled={isCurrent}
                      className={`h-12 flex flex-col items-center justify-center rounded-xl transition-all ${
                        isCurrent
                          ? 'bg-black text-white shadow-lg scale-110 z-10'
                          : 'bg-gray-100 hover:bg-gray-200 text-gray-500'
                      }`}
                    >
                      <span className="text-[10px] font-black uppercase">{format(day, 'EEE', { locale: fr }).substring(0, 3)}</span>
                      <span className="text-xs font-black">{format(day, 'd')}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {selectedWorkout.is_validated && (
              <div className="bg-green-500 text-white rounded-3xl p-6 shadow-xl shadow-green-100">
                <div className="flex items-center gap-3 font-black uppercase tracking-widest mb-4">
                  <CheckCircle2 className="w-6 h-6" />
                  Séance Complétée
                </div>
                <div className="space-y-2">
                  <div className="text-sm opacity-90 font-bold">
                    Difficulté ressentie : <span className="text-lg font-black">{selectedWorkout.perceived_difficulty}/10</span>
                  </div>
                  {selectedWorkout.athlete_comment && (
                    <div className="text-sm bg-white/10 p-4 rounded-2xl italic font-medium">
                      "{selectedWorkout.athlete_comment}"
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="mt-10">
            <Link 
              href={`/workouts/${selectedWorkout.id}`}
              className="w-full flex items-center justify-center gap-3 bg-black hover:bg-gray-900 text-white font-black uppercase tracking-widest py-5 rounded-2xl transition-all shadow-2xl active:scale-[0.98]"
            >
              <ExternalLink className="w-5 h-5" />
              Ouvrir la fiche
            </Link>
          </div>
        </div>
      </div>
    );
  };

  return (
    <main className="min-h-screen bg-[#F8F9FA] p-4 md:p-12">
      <div className="max-w-[1600px] mx-auto bg-white rounded-[2.5rem] shadow-[0_40px_80px_-20px_rgba(0,0,0,0.08)] overflow-hidden border border-gray-100">
        <div className="p-6 md:p-12">
          {renderHeader()}
          <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
            {renderDays()}
            {renderCells()}
          </div>
        </div>
      </div>
      
      {renderSideMenu()}
      
      {/* Overlay when side menu is open */}
      {isSideMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/40 backdrop-blur-md z-40 transition-opacity duration-500"
          onClick={() => setIsSideMenuOpen(false)}
        />
      )}
    </main>
  );
}
