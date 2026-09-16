/**
 * Road - Trip Manager
 */

const TripManager = {
    list: async () => {
        try {
            UI.showLoading();
            const response = await API.trips.listForTable({
                limit: 100,
                offset: 0,
                status: state.filters.status
            });
            
            state.trips = response;
            TripManager.renderTripTable();
            TripManager.updateHomeMap();
            
            if (state.trips.length === 0) {
                UI.show(UI.elements.noTrips);
                UI.hide(UI.elements.mapContainerHome);
            } else {
                UI.hide(UI.elements.noTrips);
                UI.show(UI.elements.mapContainerHome);
            }
            
            return response;
        } catch (error) {
            UI.showToast(error.message || 'Échec du chargement des voyages', 'error');
            return [];
        } finally {
            UI.hideLoading();
        }
    },
    
    get: async (id) => {
        try {
            UI.showLoading();
            const trip = await API.trips.get(id);
            state.currentTrip = trip;
            Utils.setToStorage(CONFIG.storage.currentTripKey, trip);
            return trip;
        } catch (error) {
            UI.showToast(error.message || 'Échec du chargement du voyage', 'error');
            return null;
        } finally {
            UI.hideLoading();
        }
    },
    
    create: async (data) => {
        try {
            UI.showLoading();
            const response = await API.trips.create(data);
            UI.showToast('Voyage créé avec succès !', 'success');
            await TripManager.list();
            UI.hide(UI.elements.tripModal);
            return response;
        } catch (error) {
            UI.showToast(error.message || 'Échec de la création du voyage', 'error');
            return null;
        } finally {
            UI.hideLoading();
        }
    },
    
    update: async (id, data) => {
        try {
            UI.showLoading();
            const response = await API.trips.update(id, data);
            UI.showToast('Voyage mis à jour avec succès !', 'success');
            await TripManager.list();
            if (state.currentTrip && state.currentTrip.id === id) {
                await TripManager.get(id);
                TripManager.renderTripDetail();
            }
            UI.hide(UI.elements.tripModal);
            return response;
        } catch (error) {
            UI.showToast(error.message || 'Échec de la mise à jour du voyage', 'error');
            return null;
        } finally {
            UI.hideLoading();
        }
    },
    
    delete: async (id) => {
        try {
            UI.showLoading();
            await API.trips.delete(id);
            UI.showToast('Voyage supprimé avec succès !', 'success');
            await TripManager.list();
            if (state.currentTrip && state.currentTrip.id === id) {
                ViewManager.showHome();
            }
            return true;
        } catch (error) {
            UI.showToast(error.message || 'Échec de la suppression du voyage', 'error');
            return false;
        } finally {
            UI.hideLoading();
        }
    },
    
    duplicate: async (id, newName) => {
        try {
            UI.showLoading();
            const response = await API.trips.duplicate(id, newName);
            UI.showToast('Voyage dupliqué avec succès !', 'success');
            await TripManager.list();
            return response;
        } catch (error) {
            UI.showToast(error.message || 'Échec de la duplication du voyage', 'error');
            return null;
        } finally {
            UI.hideLoading();
        }
    },
    
    updateHomeMap: () => {
        if (typeof MapManager !== 'undefined') {
            MapManager.updateHomeMap(state.trips);
        }
    },
    
    renderTripTable: () => {
        const tbody = UI.elements.tripTableBody;
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (state.trips.length === 0) return;
        
        state.trips.forEach(trip => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <button class="trip-view-btn" data-id="${trip.id}" style="background: none; border: none; text-align: left; cursor: pointer; padding: 0; font-weight: 500; color: var(--primary);">
                        ${Utils.truncate(trip.name, 50)}
                    </button>
                </td>
                <td><span class="badge badge-${trip.status}">${trip.status}</span></td>
                <td>${Utils.formatDate(trip.date_creation)}</td>
                <td>${Utils.formatDate(trip.date_modification)}</td>
                <td>
                    <div class="action-btns">
                        <button class="action-btn view" title="Voir" data-id="${trip.id}"><i class="fas fa-eye"></i></button>
                        <button class="action-btn edit" title="Modifier" data-id="${trip.id}"><i class="fas fa-edit"></i></button>
                        <button class="action-btn duplicate" title="Dupliquer" data-id="${trip.id}"><i class="fas fa-copy"></i></button>
                        <button class="action-btn delete" title="Supprimer" data-id="${trip.id}"><i class="fas fa-trash"></i></button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        TripManager.setupTripTableListeners();
    },
    
    setupTripTableListeners: () => {
        document.querySelectorAll('.trip-view-btn, .action-btn.view').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const tripId = btn.dataset.id;
                ViewManager.showTripDetail(tripId);
            });
        });
        
        document.querySelectorAll('.action-btn.edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const tripId = btn.dataset.id;
                TripManager.showEditTripModal(tripId);
            });
        });
        
        document.querySelectorAll('.action-btn.duplicate').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const tripId = btn.dataset.id;
                TripManager.showDuplicateTripPrompt(tripId);
            });
        });
        
        document.querySelectorAll('.action-btn.delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const tripId = btn.dataset.id;
                TripManager.showDeleteConfirmation(tripId);
            });
        });
    },
    
    showNewTripModal: () => {
        const modal = UI.elements.tripModal;
        const form = UI.elements.tripForm;
        
        if (!modal || !form) return;
        
        form.reset();
        UI.elements.tripIdInput.value = '';
        UI.elements.tripModalTitle.textContent = 'Nouveau Voyage';
        
        const now = new Date();
        const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
        
        UI.elements.tripStartDate.value = Utils.formatDateForInput(now);
        UI.elements.tripEndDate.value = Utils.formatDateForInput(tomorrow);
        
        UI.show(modal);
    },
    
    showEditTripModal: async (tripId) => {
        try {
            const trip = await TripManager.get(tripId);
            if (!trip) return;
            
            const modal = UI.elements.tripModal;
            const form = UI.elements.tripForm;
            
            if (!modal || !form) return;
            
            UI.elements.tripIdInput.value = trip.id;
            UI.elements.tripName.value = trip.name || '';
            UI.elements.tripStatus.value = trip.status || 'brouillon';
            UI.elements.tripDescription.value = trip.description || '';
            UI.elements.tripStartDate.value = Utils.formatDateForInput(trip.start_date);
            UI.elements.tripEndDate.value = Utils.formatDateForInput(trip.end_date);
            UI.elements.tripLatitude.value = trip.latitude || '';
            UI.elements.tripLongitude.value = trip.longitude || '';
            
            UI.elements.tripModalTitle.textContent = 'Modifier le Voyage';
            UI.show(modal);
        } catch (error) {
            UI.showToast(error.message || 'Échec du chargement du voyage', 'error');
        }
    },
    
    showDuplicateTripPrompt: (tripId) => {
        const trip = state.trips.find(t => t.id === parseInt(tripId));
        if (!trip) return;
        
        const newName = prompt('Entrez le nom du nouveau voyage:', `${trip.name} (copie)`);
        if (newName && newName.trim()) {
            TripManager.duplicate(tripId, newName.trim());
        }
    },
    
    showDeleteConfirmation: (tripId) => {
        const trip = state.trips.find(t => t.id === parseInt(tripId));
        if (!trip) return;
        
        if (confirm(`Voulez-vous vraiment supprimer le voyage "${trip.name}" ?`)) {
            TripManager.delete(tripId);
        }
    },
    
    renderTripDetail: () => {
        if (!state.currentTrip) {
            ViewManager.showHome();
            return;
        }
        
        const trip = state.currentTrip;
        
        if (UI.elements.tripDetailBreadcrumb) {
            UI.elements.tripDetailBreadcrumb.textContent = trip.name;
        }
        
        if (UI.elements.tripStatusBadge) {
            UI.elements.tripStatusBadge.innerHTML = `<span class="badge badge-${trip.status}">${trip.status}</span>`;
        }
        
        if (UI.elements.tripDetailName) {
            UI.elements.tripDetailName.textContent = trip.name || 'Voyage sans nom';
        }
        
        if (UI.elements.tripDates) {
            const start = Utils.formatDate(trip.start_date);
            const end = Utils.formatDate(trip.end_date);
            UI.elements.tripDates.innerHTML = `<i class="fas fa-calendar"></i> <span>${start} - ${end}</span>`;
        }
        
        if (UI.elements.tripDetailDescription) {
            UI.elements.tripDetailDescription.textContent = trip.description || 'Aucune description';
        }
        
        if (UI.elements.tripLocation) {
            if (trip.latitude && trip.longitude) {
                UI.elements.tripLocation.textContent = `${trip.latitude.toFixed(6)}, ${trip.longitude.toFixed(6)}`;
            } else {
                UI.elements.tripLocation.textContent = 'Localisation non définie';
            }
        }
        
        if (UI.elements.tripStepsCount) {
            UI.elements.tripStepsCount.textContent = `${trip.steps_count || 0} ${trip.steps_count === 1 ? 'étape' : 'étapes'}`;
        }
        
        if (UI.elements.tripCreatedDate) {
            UI.elements.tripCreatedDate.textContent = Utils.formatDate(trip.created_at, 'long');
        }
        
        if (UI.elements.tripUpdatedDate) {
            UI.elements.tripUpdatedDate.textContent = Utils.formatDate(trip.updated_at, 'long');
        }
        
        StepManager.list(trip.id);
        
        if (typeof MapManager !== 'undefined') {
            MapManager.updateTripMap(trip, trip.steps || []);
        }
    }
};
