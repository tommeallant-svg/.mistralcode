/**
 * Road - UI Manager
 */

const UI = {
    elements: {},
    
    init: () => {
        UI.elements = {
            // Auth
            loginScreen: document.getElementById('login-screen'),
            mainApp: document.getElementById('main-app'),
            loginForm: document.getElementById('login-form'),
            username: document.getElementById('username'),
            password: document.getElementById('password'),
            loginError: document.getElementById('login-error'),
            
            // Header
            header: document.querySelector('.header'),
            headerCenter: document.querySelector('.header-center'),
            menuToggle: document.getElementById('menu-toggle'),
            backToHome: document.getElementById('back-to-home'),
            userInfo: document.getElementById('user-info'),
            usernameDisplay: document.getElementById('username-display'),
            logoutBtn: document.getElementById('logout-btn'),
            currentViewTitle: document.getElementById('current-view-title'),
            
            // Sidebar
            sidebar: document.getElementById('sidebar'),
            sidebarUsername: document.getElementById('sidebar-username'),
            navHome: document.getElementById('nav-home'),
            navNewTrip: document.getElementById('nav-new-trip'),
            navMyTrips: document.getElementById('nav-my-trips'),
            
            // Views
            homeView: document.getElementById('home-view'),
            tripDetailView: document.getElementById('trip-detail-view'),
            
            // Home View
            filterBtn: document.getElementById('filter-btn'),
            filtersPanel: document.getElementById('filters-panel'),
            statusFilter: document.getElementById('status-filter'),
            applyFilters: document.getElementById('apply-filters'),
            clearFilters: document.getElementById('clear-filters'),
            newTripBtn: document.getElementById('new-trip-btn'),
            tripTableBody: document.getElementById('trip-table-body'),
            noTrips: document.getElementById('no-trips'),
            createFirstTrip: document.getElementById('create-first-trip'),
            
            // Trip Detail View
            backToTrips: document.getElementById('back-to-trips'),
            tripDetailBreadcrumb: document.getElementById('trip-detail-breadcrumb'),
            editTripBtn: document.getElementById('edit-trip-btn'),
            duplicateTripBtn: document.getElementById('duplicate-trip-btn'),
            deleteTripBtn: document.getElementById('delete-trip-btn'),
            
            // Trip Info Card
            tripStatusBadge: document.getElementById('trip-status-badge'),
            tripDetailName: document.getElementById('trip-detail-name'),
            tripDates: document.getElementById('trip-dates'),
            tripDetailDescription: document.getElementById('trip-detail-description'),
            tripLocation: document.getElementById('trip-location'),
            tripStepsCount: document.getElementById('trip-steps-count'),
            tripCreatedDate: document.getElementById('trip-created-date'),
            tripUpdatedDate: document.getElementById('trip-updated-date'),
            
            // Step Filters
            categoryFilters: document.getElementById('category-filters'),
            addStepBtn: document.getElementById('add-step-btn'),
            
            // Step Table
            stepTableBody: document.getElementById('step-table-body'),
            noSteps: document.getElementById('no-steps'),
            
            // AI Chat
            aiChatSection: document.getElementById('ai-chat-section'),
            aiChatMessages: document.getElementById('ai-chat-messages'),
            aiMessageInput: document.getElementById('ai-message-input'),
            aiSendBtn: document.getElementById('ai-send-btn'),
            aiSuggestions: document.getElementById('ai-suggestions'),
            suggestionsGrid: document.getElementById('suggestions-grid'),
            
            // Modals
            tripModal: document.getElementById('trip-modal'),
            tripModalTitle: document.getElementById('trip-modal-title'),
            tripForm: document.getElementById('trip-form'),
            tripIdInput: document.getElementById('trip-id-input'),
            tripName: document.getElementById('trip-name'),
            tripDescription: document.getElementById('trip-description'),
            tripStatus: document.getElementById('trip-status'),
            tripStartDate: document.getElementById('trip-start-date'),
            tripEndDate: document.getElementById('trip-end-date'),
            tripLatitude: document.getElementById('trip-latitude'),
            tripLongitude: document.getElementById('trip-longitude'),
            closeTripModal: document.getElementById('close-trip-modal'),
            cancelTripBtn: document.getElementById('cancel-trip-btn'),
            saveTripBtn: document.getElementById('save-trip-btn'),
            
            stepModal: document.getElementById('step-modal'),
            stepModalTitle: document.getElementById('step-modal-title'),
            stepForm: document.getElementById('step-form'),
            stepIdInput: document.getElementById('step-id-input'),
            stepName: document.getElementById('step-name'),
            stepCategory: document.getElementById('step-category'),
            stepType: document.getElementById('step-type'),
            stepColor: document.getElementById('step-color'),
            stepStartDatetime: document.getElementById('step-start-datetime'),
            stepEndDatetime: document.getElementById('step-end-datetime'),
            stepLocationStart: document.getElementById('step-location-start'),
            stepLocationEnd: document.getElementById('step-location-end'),
            stepLatitudeStart: document.getElementById('step-latitude-start'),
            stepLongitudeStart: document.getElementById('step-longitude-start'),
            stepLatitudeEnd: document.getElementById('step-latitude-end'),
            stepLongitudeEnd: document.getElementById('step-longitude-end'),
            stepNotes: document.getElementById('step-notes'),
            stepTripIdInput: document.getElementById('step-trip-id-input'),
            closeStepModal: document.getElementById('close-step-modal'),
            cancelStepBtn: document.getElementById('cancel-step-btn'),
            saveStepBtn: document.getElementById('save-step-btn'),
            
            // Loading
            loadingSpinner: document.getElementById('loading-spinner'),
            
            // Toast
            toastContainer: document.getElementById('toast-container')
        };
    },
    
    show: (element) => {
        if (element) element.classList.remove('hidden');
    },
    hide: (element) => {
        if (element) element.classList.add('hidden');
    },
    toggle: (element) => {
        if (element) element.classList.toggle('hidden');
    },
    
    showLoading: () => {
        UI.show(UI.elements.loadingSpinner);
    },
    hideLoading: () => {
        UI.hide(UI.elements.loadingSpinner);
    },
    
    showToast: (message, type = 'info', duration = 5000) => {
        const toastId = `toast-${Date.now()}`;
        const toastContainer = UI.elements.toastContainer;
        
        if (!toastContainer) return;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.id = toastId;
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            info: 'fa-info-circle',
            warning: 'fa-exclamation-triangle'
        };
        
        toast.innerHTML = `
            <i class="fas ${icons[type]}"></i>
            <span class="toast-message">${message}</span>
            <button class="toast-close"><i class="fas fa-times"></i></button>
        `;
        
        toastContainer.appendChild(toast);
        
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            UI.removeToast(toastId);
        });
        
        setTimeout(() => {
            UI.removeToast(toastId);
        }, duration);
    },
    
    removeToast: (toastId) => {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => {
                toast.remove();
            }, 300);
        }
    },
    
    setViewTitle: (title) => {
        if (UI.elements.currentViewTitle) {
            UI.elements.currentViewTitle.textContent = title;
        }
    },
    
    setUsername: (username) => {
        if (UI.elements.usernameDisplay) {
            UI.elements.usernameDisplay.textContent = username;
        }
        if (UI.elements.sidebarUsername) {
            UI.elements.sidebarUsername.textContent = username;
        }
    },
    
    // Get form data as object
    getFormData: (form) => {
        if (!form) return {};
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            if (value !== '') {
                data[key] = value;
            }
        }
        return data;
    },
    
    // Fill form with data
    fillForm: (form, data) => {
        if (!form || !data) return;
        for (const [key, value] of Object.entries(data)) {
            const input = form.elements[key];
            if (input) {
                if (input.type === 'checkbox' || input.type === 'radio') {
                    input.checked = input.value == value;
                } else {
                    input.value = value || '';
                }
            }
        }
    }
};
