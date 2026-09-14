'use client';

import { useEffect, useState } from 'react';

interface Trip {
  id: number;
  name: string;
  status: string;
  start_date: string;
  end_date: string;
}

export default function Home() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/trips')
      .then((res) => res.json())
      .then((data) => {
        setTrips(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center p-24">
      <h1 className="text-4xl font-bold mb-8">Application d'Entraînement</h1>
      
      <div className="w-full max-w-4xl">
        <h2 className="text-2xl font-semibold mb-4">Liste des Voyages</h2>
        {loading ? (
          <p>Chargement...</p>
        ) : trips.length === 0 ? (
          <p>Aucun voyage trouvé.</p>
        ) : (
          <div className="grid gap-4">
            {trips.map((trip) => (
              <div key={trip.id} className="p-4 border rounded shadow">
                <h3 className="text-xl font-bold">{trip.name}</h3>
                <p>Status: {trip.status}</p>
                <p>Du {new Date(trip.start_date).toLocaleDateString()} au {new Date(trip.end_date).toLocaleDateString()}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
