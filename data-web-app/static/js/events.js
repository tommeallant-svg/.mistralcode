/**
 * Road - Event Listeners
 */

const EventListeners = {
    init: () => {
        EventListeners.auth();
        EventListeners.header();
        EventListeners.sidebar();
        EventListeners.home();
        EventListeners.tripDetail();
        EventListeners.modals();
        EventListeners.AI();
        EventListeners.filters();
    },
    
    auth: () => {
        if (UI.elements.loginForm) {
            UI.elements.loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = UI.elements.username.value.trim();
                const password = UI.elements.password.value.trim();
                
                if (!username || !password) {
                    UI.showToast('Veuillez entrer un nom d\'utilisateur et un mot de passe', 'error');
                    return;
                }
                
                await Auth.login(username, password);
            });
        }
        
        if (UI.elements.username) {
            UI.elements.username.addEventListener('input', () => {
                if (UI.elements.loginError) {
                    UI.elements.loginError.textContent = '';
                }
            });
        }
    },
    
    header: () => {
        if (UI.elements.logoutBtn) {
            UI.elements.logoutBtn.addEventListener('click', async () => {
                await Auth.logout();
            });
        }
        
        if (UI.elements.menuToggle) {
            UI.elements.menuToggle.addEventListener('click', () => {
                UI.elements.sidebar.classList.toggle('expanded');
            });
        }
        
        if (UI.elements.backToHome) {
            UI.elements.backToHome.addEventListener('click', () => {
                ViewManager.showHome();
            });
        }
    },
    
    sidebar: () => {
        if (UI.elements.navHome) {
            UI.elements.navHome.addEventListener('click', (e) => {
                e.preventDefault();
                ViewManager.showHome();
                UI.elements.sidebar.classList.remove('expanded');
            });
        }
        
        if (UI.elements.navNewTrip) {
            UI.elements.navNewTrip.addEventListener('click', (e) => {
                e.preventDefault();
                TripManager.showNewTripModal();
                UI.elements.sidebar.classList.remove('expanded');
            });
        }
        
        if (UI.elements.navMyTrips) {
            UI.elements.navMyTrips.addEventListener('click', (e) => {
                e.preventDefault();
                ViewManager.showHome();
                UI.elements.sidebar.classList.remove('expanded');
            });
        }
    },
    
    home: () => {
        if (UI.elements.newTripBtn) {
            UI.elements.newTripBtn.addEventListener('click', () => {
                TripManager.showNewTripModal();
            });
        }
        
        if (UI.elements.createFirstTrip) {
            UI.elements.createFirstTrip.addEventListener('click', () => {
                TripManager.showNewTripModal();
            });
        }
        
        if (UI.elements.filterBtn) {
            UI.elements.filterBtn.addEventListener('click', () => {
                UI.toggle(UI.elements.filtersPanel);
            });
        }
    },
    
    tripDetail: () => {
        if (UI.elements.backToTrips) {
            UI.elements.backToTrips.addEventListener('click', () => {
                ViewManager.showHome();
            });
        }
        
        if (UI.elements.editTripBtn) {
            UI.elements.editTripBtn.addEventListener('click', () => {
                if (state.currentTrip) {
                    TripManager.showEditTripModal(state.currentTrip.id);
                }
            });
        }
        
        if (UI.elements.duplicateTripBtn) {
            UI.elements.duplicateTripBtn.addEventListener('click', () => {
                if (state.currentTrip) {
                    TripManager.showDuplicateTripPrompt(state.currentTrip.id);
                }
            });
        }
        
        if (UI.elements.deleteTripBtn) {
            UI.elements.deleteTripBtn.addEventListener('click', () => {
                if (state.currentTrip) {
                    TripManager.showDeleteConfirmation(state.currentTrip.id);
                }
            });
        }
        
        if (UI.elements.addStepBtn) {
            UI.elements.addStepBtn.addEventListener('click', () => {
                StepManager.showNewStepModal();
            });
        }
    },
    
    modals: () => {
        if (UI.elements.tripForm) {
            UI.elements.tripForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const tripId = UI.elements.tripIdInput.value;
                const formData = {
                    name: UI.elements.tripName.value.trim(),
                    description: UI.elements.tripDescription.value.trim(),
                    status: UI.elements.tripStatus.value,
                    start_date: UI.elements.tripStartDate.value,
                    end_date: UI.elements.tripEndDate.value,
                    latitude: UI.elements.tripLatitude.value ? parseFloat(UI.elements.tripLatitude.value) : null,
                    longitude: UI.elements.tripLongitude.value ? parseFloat(UI.elements.tripLongitude.value) : null
                };
                
                if (tripId) {
                    await TripManager.update(tripId, formData);
                } else {
                    await TripManager.create(formData);
                }
            });
        }
        
        if (UI.elements.closeTripModal) {
            UI.elements.closeTripModal.addEventListener('click', () => {
                UI.hide(UI.elements.tripModal);
            });
        }
        
        if (UI.elements.cancelTripBtn) {
            UI.elements.cancelTripBtn.addEventListener('click', () => {
                UI.hide(UI.elements.tripModal);
            });
        }
        
        if (UI.elements.stepForm) {
            UI.elements.stepForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const stepId = UI.elements.stepIdInput.value;
                const formData = {
                    name: UI.elements.stepName.value.trim(),
                    category: UI.elements.stepCategory.value,
                    type: UI.elements.stepType.value,
                    color: UI.elements.stepColor.value,
                    start_datetime: UI.elements.stepStartDatetime.value,
                    end_datetime: UI.elements.stepEndDatetime.value || null,
                    location_start: UI.elements.stepLocationStart.value.trim() || null,
                    location_end: UI.elements.stepLocationEnd.value.trim() || null,
                    latitude_start: UI.elements.stepLatitudeStart.value ? parseFloat(UI.elements.stepLatitudeStart.value) : null,
                    longitude_start: UI.elements.stepLongitudeStart.value ? parseFloat(UI.elements.stepLongitudeStart.value) : null,
                    latitude_end: UI.elements.stepLatitudeEnd.value ? parseFloat(UI.elements.stepLatitudeEnd.value) : null,
                    longitude_end: UI.elements.stepLongitudeEnd.value ? parseFloat(UI.elements.stepLongitudeEnd.value) : null,
                    notes: UI.elements.stepNotes.value.trim() || null,
                    trip_id: parseInt(UI.elements.stepTripIdInput.value)
                };
                
                if (stepId) {
                    await StepManager.update(stepId, formData);
                } else {
                    await StepManager.create(formData);
                }
            });
        }
        
        if (UI.elements.closeStepModal) {
            UI.elements.closeStepModal.addEventListener('click', () => {
                UI.hide(UI.elements.stepModal);
            });
        }
        
        if (UI.elements.cancelStepBtn) {
            UI.elements.cancelStepBtn.addEventListener('click', () => {
                UI.hide(UI.elements.stepModal);
            });
        }
        
        if (UI.elements.stepCategory) {
            UI.elements.stepCategory.addEventListener('change', () => {
                StepManager.updateTypeOptions(UI.elements.stepCategory.value);
            });
        }
        
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', () => {
                const modal = overlay.closest('.modal');
                if (modal) {
                    UI.hide(modal);
                }
            });
        });
    },
    
    AI: () => {
        if (UI.elements.aiSendBtn) {
            UI.elements.aiSendBtn.addEventListener('click', () => {
                AIManager.sendMessage();
            });
        }
        
        if (UI.elements.aiMessageInput) {
            UI.elements.aiMessageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    AIManager.sendMessage();
                }
            });
        }
    },
    
    filters: () => {
        if (UI.elements.applyFilters) {
            UI.elements.applyFilters.addEventListener('click', async () => {
                state.filters.status = UI.elements.statusFilter.value;
                await TripManager.list();
                UI.hide(UI.elements.filtersPanel);
            });
        }
        
        if (UI.elements.clearFilters) {
            UI.elements.clearFilters.addEventListener('click', async () => {
                state.filters.status = '';
                UI.elements.statusFilter.value = '';
                await TripManager.list();
                UI.hide(UI.elements.filtersPanel);
            });
        }
        
        if (UI.elements.categoryFilters) {
            UI.elements.categoryFilters.addEventListener('click', async (e) => {
                if (e.target.classList.contains('filter-tab')) {
                    UI.elements.categoryFilters.querySelectorAll('.filter-tab').forEach(tab => {
                        tab.classList.remove('active');
                    });
                    e.target.classList.add('active');
                    
                    state.filters.category = e.target.dataset.category || '';
                    if (state.currentTrip) {
                        await StepManager.list(state.currentTrip.id);
                    }
                }
            });
        }
    }
};
