/**
 * Road - Map Manager
 */

const MapManager = {
    init: (containerId, options = {}) => {
        const container = document.getElementById(containerId);
        if (!container || window[`${containerId}_map`]) return;
        
        const defaultOptions = {
            center: [48.8566, 2.3522],
            zoom: 5,
            minZoom: 2,
            maxZoom: 18,
            worldCopyJump: true
        };
        
        const map = L.map(containerId, { ...defaultOptions, ...options });
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        window[`${containerId}_map`] = map;
        state.maps[containerId] = map;
        
        return map;
    },
    
    clear: (map) => {
        if (map) {
            map.eachLayer(layer => {
                if (layer instanceof L.Marker || layer instanceof L.Polyline) {
                    map.removeLayer(layer);
                }
            });
        }
    },
    
    addMarker: (map, lat, lng, options = {}) => {
        if (!map || lat === null || lng === null) return null;
        
        const defaultOptions = {
            draggable: false,
            riseOnHover: true
        };
        
        const marker = L.marker([lat, lng], { ...defaultOptions, ...options });
        marker.addTo(map);
        return marker;
    },
    
    addPolyline: (map, points, options = {}) => {
        if (!map || points.length < 2) return null;
        
        const defaultOptions = {
            color: '#3B82F6',
            weight: 3,
            opacity: 0.8,
            lineCap: 'round',
            lineJoin: 'round'
        };
        
        const polyline = L.polyline(points, { ...defaultOptions, ...options });
        polyline.addTo(map);
        return polyline;
    },
    
    fitToBounds: (map, markers) => {
        if (!map || !markers.length) return;
        
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds(), { padding: [50, 50] });
    },
    
    updateTripMap: (trip, steps) => {
        const map = state.maps['trip-detail-map'];
        if (!map) {
            MapManager.init('trip-detail-map');
            return;
        }
        
        MapManager.clear(map);
        
        const markers = [];
        
        // Add trip location if available
        if (trip && trip.latitude && trip.longitude) {
            const marker = MapManager.addMarker(map, trip.latitude, trip.longitude, {
                title: trip.name
            });
            if (marker) markers.push(marker);
        }
        
        // Process steps
        steps.forEach(step => {
            const color = Utils.getCategoryColor(step.category);
            const isTransport = step.category === 'transport';
            
            if (isTransport && step.latitude_start && step.longitude_start) {
                const startPoint = [step.latitude_start, step.longitude_start];
                const endPoint = [step.latitude_end || step.latitude_start, step.longitude_end || step.longitude_start];
                
                const startMarker = MapManager.addMarker(map, step.latitude_start, step.longitude_start, {
                    title: step.name + ' (Départ)',
                    icon: L.divIcon({
                        className: 'transport-marker',
                        html: `<i class="fas fa-flag" style="color: ${color}; font-size: 20px;"></i>`,
                        iconSize: [30, 30]
                    })
                });
                if (startMarker) markers.push(startMarker);
                
                if (step.latitude_end && step.longitude_end) {
                    const endMarker = MapManager.addMarker(map, step.latitude_end, step.longitude_end, {
                        title: step.name + ' (Arrivée)',
                        icon: L.divIcon({
                            className: 'transport-marker',
                            html: `<i class="fas fa-flag-checkered" style="color: ${color}; font-size: 20px;"></i>`,
                            iconSize: [30, 30]
                        })
                    });
                    if (endMarker) markers.push(endMarker);
                }
                
                if (step.latitude_end && step.longitude_end) {
                    MapManager.addPolyline(map, [startPoint, endPoint], {
                        color: color,
                        weight: 4
                    });
                }
            } else {
                const lat = step.latitude_start || step.latitude_end;
                const lng = step.longitude_start || step.longitude_end;
                
                if (lat && lng) {
                    const marker = MapManager.addMarker(map, lat, lng, {
                        title: step.name,
                        icon: L.divIcon({
                            className: 'category-marker',
                            html: `<i class="fas fa-map-marker-alt" style="color: ${color}; font-size: 20px;"></i>`,
                            iconSize: [30, 40],
                            iconAnchor: [15, 40]
                        })
                    });
                    if (marker) markers.push(marker);
                }
            }
        });
        
        if (markers.length > 0) {
            MapManager.fitToBounds(map, markers);
        }
        
        state.markers.trip = markers;
    },
    
    updateHomeMap: (trips) => {
        const map = state.maps['home-map'];
        if (!map) {
            MapManager.init('home-map');
            return;
        }
        
        MapManager.clear(map);
        
        const markers = [];
        
        trips.forEach(trip => {
            if (trip.latitude && trip.longitude) {
                const color = trip.steps_count > 0 ? Utils.getCategoryColor('activité') : '#666666';
                const marker = MapManager.addMarker(map, trip.latitude, trip.longitude, {
                    title: trip.name,
                    icon: L.divIcon({
                        className: 'trip-marker',
                        html: `<i class="fas fa-suitcase" style="color: ${color}; font-size: 16px;"></i>`,
                        iconSize: [30, 30]
                    })
                });
                if (marker) markers.push(marker);
            }
        });
        
        if (markers.length > 0) {
            MapManager.fitToBounds(map, markers);
        }
        
        state.markers.home = markers;
    }
};
