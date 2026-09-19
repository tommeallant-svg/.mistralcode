/**
 * Road - API Client
 */

const API = {
    // Base request function
    request: async (endpoint, method = 'GET', data = null, headers = {}) => {
        const url = `${CONFIG.apiBaseUrl}${endpoint}`;
        const token = state.token;
        
        const defaultHeaders = {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        };
        
        const options = {
            method,
            headers: { ...defaultHeaders, ...headers }
        };
        
        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Network error' }));
                throw new Error(error.detail || 'Request failed');
            }
            
            if (response.status === 204) {
                return null;
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    // Authentication
    auth: {
        login: async (username, password) => {
            return API.request('/auth/login', 'POST', { username, password });
        },
        logout: async () => {
            return API.request('/auth/logout', 'POST');
        },
        me: async () => {
            return API.request('/auth/me', 'GET');
        },
        verify: async () => {
            return API.request('/auth/verify', 'POST');
        }
    },
    
    // Trips
    trips: {
        list: async (params = {}) => {
            const query = new URLSearchParams(params);
            return API.request(`/trips/?${query.toString()}`, 'GET');
        },
        listForTable: async (params = {}) => {
            const query = new URLSearchParams(params);
            return API.request(`/trips/table?${query.toString()}`, 'GET');
        },
        get: async (id) => {
            return API.request(`/trips/${id}`, 'GET');
        },
        create: async (data) => {
            return API.request('/trips/', 'POST', data);
        },
        update: async (id, data) => {
            return API.request(`/trips/${id}`, 'PUT', data);
        },
        delete: async (id) => {
            return API.request(`/trips/${id}`, 'DELETE');
        },
        duplicate: async (id, newName) => {
            return API.request(`/trips/${id}/duplicate?new_name=${encodeURIComponent(newName)}`, 'POST');
        },
        getMapData: async (id) => {
            return API.request(`/trips/${id}/map`, 'GET');
        }
    },
    
    // Steps
    steps: {
        list: async (tripId, params = {}) => {
            const query = new URLSearchParams({ trip_id: tripId, ...params });
            return API.request(`/steps/?${query.toString()}`, 'GET');
        },
        listForTable: async (tripId, params = {}) => {
            const query = new URLSearchParams({ trip_id: tripId, ...params });
            return API.request(`/steps/table?${query.toString()}`, 'GET');
        },
        get: async (id) => {
            return API.request(`/steps/${id}`, 'GET');
        },
        create: async (data) => {
            return API.request('/steps/', 'POST', data);
        },
        update: async (id, data) => {
            return API.request(`/steps/${id}`, 'PUT', data);
        },
        delete: async (id) => {
            return API.request(`/steps/${id}`, 'DELETE');
        },
        duplicate: async (id) => {
            return API.request(`/steps/${id}/duplicate`, 'POST');
        },
        reorder: async (data) => {
            return API.request('/steps/reorder', 'POST', data);
        },
        getCategories: async () => {
            return API.request('/steps/categories', 'GET');
        },
        getTransportTypes: async () => {
            return API.request('/steps/transport-types', 'GET');
        }
    },
    
    // AI
    ai: {
        chat: async (data) => {
            return API.request('/ai/chat', 'POST', data);
        },
        getSuggestions: async (params = {}) => {
            const query = new URLSearchParams(params);
            return API.request(`/ai/proposals/suggestions?${query.toString()}`, 'GET');
        },
        getHistory: async (tripId) => {
            return API.request(`/ai/conversation/${tripId}`, 'GET');
        },
        clearHistory: async (tripId) => {
            return API.request(`/ai/conversation/${tripId}`, 'DELETE');
        }
    }
};
