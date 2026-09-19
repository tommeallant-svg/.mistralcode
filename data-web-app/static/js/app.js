/**
 * Road - Travel Management Application
 * Main Application Entry Point
 */

// Load configuration first
// CONFIG and state are defined in config.js

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize all modules
    UI.init();
    MapManager.init('home-map');
    MapManager.init('trip-detail-map');
    EventListeners.init();
    
    // Restore session
    const restored = await Auth.restoreSession();
    
    if (!restored) {
        Auth.updateUI();
    }
    
    // Set view title
    UI.setViewTitle('Mes Voyages');
    
    // Initialize step table drag and drop
    StepManager.setupDragAndDrop();
    
    console.log('Road application initialized');
});

// Also initialize if already loaded
document.readyState === 'complete' && document.addEventListener('DOMContentLoaded', async () => {
    UI.init();
    MapManager.init('home-map');
    MapManager.init('trip-detail-map');
    EventListeners.init();
    
    const restored = await Auth.restoreSession();
    
    if (!restored) {
        Auth.updateUI();
    }
    
    UI.setViewTitle('Mes Voyages');
    StepManager.setupDragAndDrop();
    
    console.log('Road application initialized');
});
