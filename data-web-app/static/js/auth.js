/**
 * Road - Authentication Manager
 */

const Auth = {
    login: async (username, password) => {
        try {
            UI.showLoading();
            const response = await API.auth.login(username, password);
            
            state.token = response.access_token;
            state.user = response.user;
            
            Utils.setToStorage(CONFIG.storage.tokenKey, state.token);
            Utils.setToStorage(CONFIG.storage.userKey, state.user);
            
            UI.setUsername(state.user.username);
            Auth.updateUI();
            
            await TripManager.list();
            
            UI.showToast('Connexion réussie !', 'success');
            return true;
        } catch (error) {
            UI.showToast(error.message || 'Échec de la connexion', 'error');
            if (UI.elements.loginError) {
                UI.elements.loginError.textContent = error.message || 'Nom d\'utilisateur ou mot de passe incorrect';
            }
            return false;
        } finally {
            UI.hideLoading();
        }
    },
    
    logout: async () => {
        try {
            await API.auth.logout();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            state.token = null;
            state.user = null;
            state.trips = [];
            state.currentTrip = null;
            state.currentSteps = [];
            
            Utils.removeFromStorage(CONFIG.storage.tokenKey);
            Utils.removeFromStorage(CONFIG.storage.userKey);
            Utils.removeFromStorage(CONFIG.storage.currentTripKey);
            
            Auth.updateUI();
            UI.showToast('Déconnexion réussie', 'info');
        }
    },
    
    isAuthenticated: () => {
        return !!state.token;
    },
    
    restoreSession: async () => {
        const token = Utils.getFromStorage(CONFIG.storage.tokenKey);
        const user = Utils.getFromStorage(CONFIG.storage.userKey);
        
        if (token && user) {
            state.token = token;
            state.user = user;
            
            try {
                await API.auth.verify();
                UI.setUsername(state.user.username);
                Auth.updateUI();
                
                await TripManager.list();
                
                return true;
            } catch (error) {
                console.error('Session restoration failed:', error);
                Auth.logout();
                return false;
            }
        }
        
        return false;
    },
    
    updateUI: () => {
        if (Auth.isAuthenticated()) {
            UI.hide(UI.elements.loginScreen);
            UI.show(UI.elements.mainApp);
        } else {
            UI.show(UI.elements.loginScreen);
            UI.hide(UI.elements.mainApp);
        }
    }
};
