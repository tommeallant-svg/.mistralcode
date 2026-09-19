/**
 * Road - View Manager
 */

const ViewManager = {
    showHome: () => {
        UI.hide(UI.elements.tripDetailView);
        UI.show(UI.elements.homeView);
        if (UI.elements.headerCenter) {
            UI.elements.headerCenter.style.display = 'block';
        }
        
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        if (UI.elements.navHome) {
            UI.elements.navHome.classList.add('active');
        }
        
        UI.hide(UI.elements.backToHome);
        if (UI.elements.menuToggle) {
            UI.show(UI.elements.menuToggle);
        }
        
        state.currentTrip = null;
        state.currentSteps = [];
        Utils.removeFromStorage(CONFIG.storage.currentTripKey);
        
        TripManager.list();
        UI.setViewTitle('Mes Voyages');
    },
    
    showTripDetail: async (tripId) => {
        try {
            const trip = await TripManager.get(tripId);
            if (!trip) {
                ViewManager.showHome();
                return;
            }
            
            UI.hide(UI.elements.homeView);
            UI.show(UI.elements.tripDetailView);
            
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            
            UI.show(UI.elements.backToHome);
            if (UI.elements.menuToggle) {
                UI.hide(UI.elements.menuToggle);
            }
            
            TripManager.renderTripDetail();
            UI.setViewTitle(`Voyage: ${trip.name}`);
            
            window.scrollTo(0, 0);
        } catch (error) {
            UI.showToast(error.message || 'Échec du chargement du voyage', 'error');
            ViewManager.showHome();
        }
    },
    
    showLogin: () => {
        UI.show(UI.elements.loginScreen);
        UI.hide(UI.elements.mainApp);
    }
};
