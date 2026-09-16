'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { 
  ChevronLeft, 
  Plus, 
  Trash2, 
  Save,
  Dumbbell,
  Activity,
  Type,
  Layout,
  Clock,
  Zap,
  RotateCcw
} from 'lucide-react';
import Link from 'next/link';
import { fetchWithAuth, getAuthUser } from '@/lib/api';
import { CatalogWorkout, CatalogInterval } from '@/types/workout';

export default function CatalogEditPage() {
  const { id } = useParams();
  const router = useRouter();
  const isNew = id === 'new';
  
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [workout, setWorkout] = useState<Partial<CatalogWorkout>>({
    name: '',
    workout_type: 'Fractionné',
    category: 'Fractionné',
    perceived_difficulty: 5,
    scheme: [
      { type: 'Echauffement', repetitions: 1, duration: 15, pace_vma: 65 },
      { type: 'Fraction', repetitions: 10, duration: 1, pace_vma: 100 },
      { type: 'Récupération', repetitions: 10, duration: 1, pace_vma: 60 },
      { type: 'Retour calme', repetitions: 1, duration: 10, pace_vma: 65 }
    ]
  });

  useEffect(() => {
    const user = getAuthUser();
    if (user?.role !== 'coach') {
      router.push('/');
      return;
    }
    if (!isNew) {
      fetchWorkout();
    }
  }, [id]);

  const fetchWorkout = async () => {
    try {
      const res = await fetchWithAuth(`/api/catalog`);
      if (res.ok) {
        const data = await res.json();
        const found = data.find((w: any) => w.id === parseInt(id as string));
        if (found) {
          setWorkout(found);
        } else {
          router.push('/catalog');
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const addInterval = () => {
    setWorkout({
      ...workout,
      scheme: [...(workout.scheme || []), { type: 'Nouveau', repetitions: 1, duration: 1, pace_vma: 80 }]
    });
  };

  const removeInterval = (index: number) => {
    const newScheme = [...(workout.scheme || [])];
    newScheme.splice(index, 1);
    setWorkout({ ...workout, scheme: newScheme });
  };

  const updateInterval = (index: number, field: keyof CatalogInterval, value: any) => {
    const newScheme = [...(workout.scheme || [])];
    newScheme[index] = { ...newScheme[index], [field]: value };
    setWorkout({ ...workout, scheme: newScheme });
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const url = isNew ? '/api/catalog' : `/api/catalog/${id}`;
      const method = isNew ? 'POST' : 'PATCH';
      const res = await fetchWithAuth(url, {
        method,
        body: JSON.stringify(workout)
      });
      if (res.ok) {
        router.push('/catalog');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center font-black uppercase text-gray-400 tracking-widest">Chargement...</div>;

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-20">
      <div className="bg-white border-b border-gray-100 sticky top-0 z-50 px-6 py-6">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <Link href="/catalog" className="flex items-center gap-2 text-gray-400 hover:text-black transition-colors font-black uppercase text-xs tracking-widest">
            <ChevronLeft className="w-5 h-5" />
            <span>Catalogue</span>
          </Link>
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-black text-black uppercase tracking-tighter">
              {isNew ? 'Nouvel Entraînement' : 'Éditer la Séance'}
            </h1>
          </div>
          <button 
            onClick={handleSave} 
            disabled={saving}
            className="flex items-center gap-2 bg-black text-white px-8 py-3 rounded-2xl font-black uppercase text-xs tracking-widest hover:bg-gray-800 transition-all disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Enregistrement...' : 'Enregistrer'}</span>
          </button>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 mt-12 space-y-12">
        {/* Basic Info Card */}
        <section className="bg-white rounded-[3rem] p-10 shadow-sm border border-gray-100 space-y-8">
          <div className="flex items-center gap-3">
            <div className="bg-yellow-400 p-2 rounded-xl">
              <Type className="w-5 h-5 text-black" />
            </div>
            <h2 className="text-xl font-black text-black uppercase tracking-tight">Informations Générales</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-gray-400">Nom de la séance</label>
              <input 
                type="text" 
                value={workout.name} 
                onChange={e => setWorkout({...workout, name: e.target.value})}
                placeholder="ex: VMA Courte 30/30"
                className="w-full bg-gray-50 border-none rounded-2xl px-6 py-4 font-bold text-black outline-none focus:ring-2 focus:ring-black transition-all"
              />
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-gray-400">Type de séance</label>
              <select 
                value={workout.workout_type} 
                onChange={e => setWorkout({...workout, workout_type: e.target.value})}
                className="w-full bg-gray-50 border-none rounded-2xl px-6 py-4 font-bold text-black outline-none focus:ring-2 focus:ring-black transition-all appearance-none"
              >
                <option value="VO2 Max">VO2 Max</option>
                <option value="Seuil">Seuil</option>
                <option value="Tempo">Tempo</option>
                <option value="Fractionné">Fractionné</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-gray-400">Difficulté estimée (1-10)</label>
              <div className="flex items-center gap-4">
                <input 
                  type="range" min="1" max="10" step="1"
                  value={workout.perceived_difficulty} 
                  onChange={e => setWorkout({...workout, perceived_difficulty: parseInt(e.target.value)})}
                  className="flex-1 h-2 bg-gray-100 rounded-full appearance-none cursor-pointer accent-black"
                />
                <span className="w-12 h-12 bg-black text-white rounded-xl flex items-center justify-center font-black">{workout.perceived_difficulty}</span>
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-gray-400">Catégorie</label>
              <input 
                type="text" 
                value={workout.category} 
                readOnly
                className="w-full bg-gray-100 border-none rounded-2xl px-6 py-4 font-bold text-gray-400 outline-none"
              />
            </div>
          </div>
        </section>

        {/* Scheme Editor */}
        <section className="space-y-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-black p-2 rounded-xl">
                <Layout className="w-5 h-5 text-white" />
              </div>
              <h2 className="text-xl font-black text-black uppercase tracking-tight">Schéma d'entraînement</h2>
            </div>
            <button 
              onClick={addInterval}
              className="flex items-center gap-2 bg-white text-black border border-gray-200 px-6 py-3 rounded-2xl font-black uppercase text-[10px] tracking-widest hover:bg-black hover:text-white transition-all shadow-sm"
            >
              <Plus className="w-4 h-4" />
              Ajouter un bloc
            </button>
          </div>

          <div className="space-y-4">
            {workout.scheme?.map((interval, idx) => (
              <div key={idx} className="bg-white rounded-[2.5rem] p-8 shadow-sm border border-gray-100 group hover:border-black transition-all relative overflow-hidden">
                <div className="absolute top-0 left-0 w-2 h-full bg-gray-100 group-hover:bg-black transition-all" />
                
                <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-end">
                  <div className="md:col-span-3 space-y-2">
                    <label className="text-[9px] font-black uppercase tracking-widest text-gray-400">Type de bloc</label>
                    <input 
                      type="text" 
                      value={interval.type} 
                      onChange={e => updateInterval(idx, 'type', e.target.value)}
                      className="w-full bg-gray-50 border-none rounded-xl px-4 py-3 font-bold text-black outline-none focus:ring-2 focus:ring-black transition-all"
                    />
                  </div>
                  
                  <div className="md:col-span-2 space-y-2">
                    <label className="text-[9px] font-black uppercase tracking-widest text-gray-400 flex items-center gap-1">
                      <RotateCcw className="w-3 h-3" /> Répétitions
                    </label>
                    <input 
                      type="number" 
                      value={interval.repetitions} 
                      onChange={e => updateInterval(idx, 'repetitions', parseInt(e.target.value))}
                      className="w-full bg-gray-50 border-none rounded-xl px-4 py-3 font-bold text-black outline-none focus:ring-2 focus:ring-black transition-all"
                    />
                  </div>

                  <div className="md:col-span-3 space-y-2">
                    <label className="text-[9px] font-black uppercase tracking-widest text-gray-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" /> Volume (min ou m)
                    </label>
                    <div className="flex items-center gap-2">
                      <input 
                        type="number" step="0.5"
                        value={interval.duration || interval.distance} 
                        onChange={e => updateInterval(idx, interval.duration ? 'duration' : 'distance', parseFloat(e.target.value))}
                        className="w-full bg-gray-50 border-none rounded-xl px-4 py-3 font-bold text-black outline-none focus:ring-2 focus:ring-black transition-all"
                      />
                      <button 
                        onClick={() => {
                          if (interval.duration) {
                            updateInterval(idx, 'distance', interval.duration);
                            updateInterval(idx, 'duration', undefined as any);
                          } else {
                            updateInterval(idx, 'duration', interval.distance);
                            updateInterval(idx, 'distance', undefined as any);
                          }
                        }}
                        className="bg-gray-100 px-3 py-3 rounded-xl text-[10px] font-black uppercase hover:bg-gray-200 transition-all"
                      >
                        {interval.duration ? 'MIN' : 'M'}
                      </button>
                    </div>
                  </div>

                  <div className="md:col-span-3 space-y-2">
                    <label className="text-[9px] font-black uppercase tracking-widest text-gray-400 flex items-center gap-1">
                      <Zap className="w-3 h-3" /> Allure (% VMA)
                    </label>
                    <div className="flex items-center gap-2">
                      <input 
                        type="number" 
                        value={interval.pace_vma} 
                        onChange={e => updateInterval(idx, 'pace_vma', parseInt(e.target.value))}
                        className="w-full bg-gray-50 border-none rounded-xl px-4 py-3 font-bold text-black outline-none focus:ring-2 focus:ring-black transition-all"
                      />
                      <span className="font-black text-gray-400">%</span>
                    </div>
                  </div>

                  <div className="md:col-span-1 flex justify-end">
                    <button 
                      onClick={() => removeInterval(idx)}
                      className="p-3 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-xl transition-all"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
