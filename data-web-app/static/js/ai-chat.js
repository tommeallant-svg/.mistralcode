/**
 * Road - AI Chat Integration
 * This file is loaded separately in HTML
 */

// AIManager is already defined in ai.js
// This file ensures AI functionality is available

// If AIManager is not defined, define a fallback
if (typeof AIManager === 'undefined') {
    const AIManager = {
        sendMessage: () => console.log('AIManager not loaded'),
        addMessage: () => console.log('AIManager not loaded'),
        showProposals: () => console.log('AIManager not loaded'),
        getSuggestions: () => console.log('AIManager not loaded')
    };
}
