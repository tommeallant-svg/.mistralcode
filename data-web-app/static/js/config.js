/**
 * Road - Travel Management Application
 * Configuration
 */

const CONFIG = {
    apiBaseUrl: window.location.origin + '/api/v1',
    storage: {
        tokenKey: 'road_auth_token',
        userKey: 'road_user',
        currentTripKey: 'road_current_trip'
    },
    defaultCategoryColors: {
        transport: '#3B82F6',
        hébergement: '#10B981',
        activité: '#F59E0B',
        food: '#EF4444',
        sport: '#8B5CF6',
        hobbies: '#EC4899'
    },
    transportTypes: {
        transport: ['bateau', 'train', 'avion', 'voiture', 'scoot', 'vélo', 'marche', 'bus']
    },
    categoryTypes: {
        hébergement: ['Hôtel', 'Airbnb', 'Auberge', 'Camping', 'Appartement'],
        activité: ['Visite guidée', 'Musée', 'Randonnée', 'Shopping', 'Spectacle'],
        food: ['Restaurant', 'Café', 'Bar', 'Marché', 'Food truck'],
        sport: ['Gym', 'Piscine', 'Tennis', 'Golf', 'Randonnée'],
        hobbies: ['Photographie', 'Art', 'Musique', 'Lecture', 'Jeux']
    },
    dateFormat: {
        short: { year: 'numeric', month: 'short', day: 'numeric' },
        long: { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' },
        time: { hour: '2-digit', minute: '2-digit' },
        dateTime: { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }
    }
};

// State management
const state = {
    user: null,
    token: null,
    trips: [],
    currentTrip: null,
    currentSteps: [],
    currentStep: null,
    filters: {
        status: '',
        category: ''
    },
    maps: {
        home: null,
        trip: null
    },
    markers: {
        home: [],
        trip: []
    }
};
