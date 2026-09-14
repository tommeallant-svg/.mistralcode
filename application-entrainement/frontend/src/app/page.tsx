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
  ArrowRightLeft
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
    <div className="flex items-center justify-between mb-8">
      <div className="flex items-center gap-4">
        <h1 className="text-3xl font-bold text-gray-800 capitalize">
          {format(currentDate, 'MMMM yyyy', { locale: fr })}
        </h1>
        <div className="flex items-center bg-gray-100 rounded-lg p-1">
          <button 
            onClick={() => setView('month')}
            className={`px-4 py-2 rounded-md transition-all ${view === 'month' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-600'}`}
          >
            Mois
          </button>
          <button 
            onClick={() => setView('week')}
            className={`px-4 py-2 rounded-md transition-all ${view === 'week' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-600'}`}
          >
            Semaine
          </button>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button onClick={prev} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <ChevronLeft className="w-6 h-6" />
        </button>
        <button 
          onClick={() => setCurrentDate(new Date())}
          className="px-4 py-2 hover:bg-gray-100 rounded-md text-sm font-medium"
        >
          Aujourd'hui
        </button>
        <button onClick={next} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
          <ChevronRight className="w-6 h-6" />
        </button>
      </div>
    </div>
  );

  const renderDays = () => {
    const days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
    return (
      <div className="grid grid-cols-7 mb-2 border-b border-gray-200">
        {days.map(day => (
          <div key={day} className="py-2 text-center text-sm font-semibold text-gray-500 uppercase">
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
      <div className="grid grid-cols-7 auto-rows-fr border-l border-t border-gray-200 min-h-[600px]">
        {days.map((day, idx) => {
          const dayWorkouts = (Array.isArray(workouts) ? workouts : []).filter(w => isSameDay(parseISO(w.date), day));
          return (
            <div 
              key={idx}
              className={`min-h-[120px] p-2 border-r border-b border-gray-200 transition-colors ${
                !isSameMonth(day, monthStart) && view === 'month' ? 'bg-gray-50 text-gray-400' : 'bg-white'
              } ${isSameDay(day, new Date()) ? 'bg-blue-50/30' : ''}`}
            >
              <span className={`text-sm font-medium ${isSameDay(day, new Date()) ? 'bg-blue-600 text-white w-6 h-6 flex items-center justify-center rounded-full' : ''}`}>
                {format(day, 'd')}
              </span>
              <div className="mt-2 space-y-1">
                {dayWorkouts.map(workout => (
                  <div 
                    key={workout.id}
                    onClick={() => handleWorkoutClick(workout)}
                    className={`p-2 rounded cursor-pointer text-xs border transition-all hover:shadow-md ${
                      workout.is_validated 
                        ? 'bg-green-50 border-green-200 text-green-700' 
                        : 'bg-blue-50 border-blue-200 text-blue-700'
                    }`}
                  >
                    <div className="font-bold uppercase flex items-center justify-between">
                      {workout.workout_type}
                      {workout.is_validated && <CheckCircle2 className="w-3 h-3" />}
                    </div>
                    {view === 'week' && <div className="truncate font-medium">{workout.name}</div>}
                    <div className="flex items-center gap-1 mt-1 opacity-80">
                      <Clock className="w-3 h-3" />
                      {workout.duration_minutes} min
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
      <div className={`fixed inset-y-0 right-0 w-96 bg-white shadow-2xl transform transition-transform duration-300 z-50 ${isSideMenuOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        <div className="p-6 h-full flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-800">Détails de la séance</h2>
            <button onClick={() => setIsSideMenuOpen(false)} className="p-1 hover:bg-gray-100 rounded-full">
              <X className="w-6 h-6" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-6">
            <div>
              <span className="inline-block px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800 uppercase mb-2">
                {selectedWorkout.workout_type}
              </span>
              <h3 className="text-2xl font-bold text-gray-900">{selectedWorkout.name}</h3>
              <p className="text-gray-500 mt-1">{format(parseISO(selectedWorkout.date), 'EEEE d MMMM', { locale: fr })}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 p-3 rounded-lg">
                <div className="text-gray-500 text-xs mb-1">Durée</div>
                <div className="font-bold flex items-center gap-2">
                  <Clock className="w-4 h-4 text-blue-500" />
                  {selectedWorkout.duration_minutes} min
                </div>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <div className="text-gray-500 text-xs mb-1">Difficulté prévue</div>
                <div className="font-bold">{selectedWorkout.difficulty_level} / 10</div>
              </div>
            </div>

            <div>
              <h4 className="font-bold text-sm text-gray-700 uppercase mb-2">Description</h4>
              <p className="text-gray-600 text-sm leading-relaxed">{selectedWorkout.description_short}</p>
            </div>

            <div>
              <h4 className="font-bold text-sm text-gray-700 uppercase mb-2 border-b pb-1">Déplacer vers (cette semaine)</h4>
              <div className="flex flex-wrap gap-2 mt-2">
                {weekDays.map(day => (
                  <button
                    key={day.toISOString()}
                    onClick={() => shiftWorkout(selectedWorkout, day)}
                    disabled={isSameDay(day, parseISO(selectedWorkout.date))}
                    className={`px-3 py-1 rounded text-xs transition-colors ${
                      isSameDay(day, parseISO(selectedWorkout.date))
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                    }`}
                  >
                    {format(day, 'EEE', { locale: fr })}
                  </button>
                ))}
              </div>
            </div>

            {selectedWorkout.is_validated && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center gap-2 text-green-700 font-bold mb-2">
                  <CheckCircle2 className="w-5 h-5" />
                  Séance validée
                </div>
                <div className="text-sm text-green-800">
                  <span className="font-semibold">Ressenti:</span> {selectedWorkout.perceived_difficulty}/10
                </div>
                {selectedWorkout.athlete_comment && (
                  <div className="text-sm text-green-800 mt-1 italic">
                    "{selectedWorkout.athlete_comment}"
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="mt-6 pt-6 border-t">
            <Link 
              href={`/workouts/${selectedWorkout.id}`}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition-all shadow-lg hover:shadow-blue-200"
            >
              <ExternalLink className="w-5 h-5" />
              Accéder à la vue séance
            </Link>
          </div>
        </div>
      </div>
    );
  };

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-100">
        <div className="p-8">
          {renderHeader()}
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            {renderDays()}
            {renderCells()}
          </div>
        </div>
      </div>
      
      {renderSideMenu()}
      
      {/* Overlay when side menu is open */}
      {isSideMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
          onClick={() => setIsSideMenuOpen(false)}
        />
      )}
    </main>
  );
}
