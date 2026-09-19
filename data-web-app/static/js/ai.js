/**
 * Road - AI Manager
 */

const AIManager = {
    sendMessage: async () => {
        const input = UI.elements.aiMessageInput;
        const message = input.value.trim();
        
        if (!message) return;
        
        if (!state.currentTrip) {
            UI.showToast('Veuillez sélectionner un voyage d\'abord', 'error');
            return;
        }
        
        try {
            UI.showLoading();
            input.disabled = true;
            if (UI.elements.aiSendBtn) {
                UI.elements.aiSendBtn.disabled = true;
            }
            
            AIManager.addMessage('user', message);
            input.value = '';
            
            const response = await API.ai.chat({
                trip_id: state.currentTrip.id,
                message: message,
                history: []
            });
            
            if (response.success && response.response) {
                AIManager.addMessage('assistant', response.response.message);
                
                if (response.response.proposals && response.response.proposals.length > 0) {
                    AIManager.showProposals(response.response.proposals);
                }
                
                await AIManager.getSuggestions();
            }
        } catch (error) {
            UI.showToast(error.message || 'Échec de l\'envoi du message', 'error');
        } finally {
            input.disabled = false;
            if (UI.elements.aiSendBtn) {
                UI.elements.aiSendBtn.disabled = false;
            }
            UI.hideLoading();
        }
    },
    
    addMessage: (role, content) => {
        const messagesContainer = UI.elements.aiChatMessages;
        if (!messagesContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        let avatar = '';
        if (role !== 'user') {
            avatar = '<div class="ai-avatar small"><i class="fas fa-robot"></i></div>';
        }
        
        messageDiv.innerHTML = `
            ${avatar}
            <div class="message-content">${content}</div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    },
    
    showProposals: (proposals) => {
        const suggestionsContainer = UI.elements.suggestionsGrid;
        if (!suggestionsContainer) return;
        
        suggestionsContainer.innerHTML = '';
        
        proposals.forEach((proposal, index) => {
            const card = document.createElement('div');
            card.className = 'suggestion-card';
            card.dataset.index = index;
            
            const color = Utils.getCategoryColor(proposal.category);
            
            card.innerHTML = `
                <h5>${proposal.name}</h5>
                <p>${proposal.description || 'Aucune description'}</p>
                <div class="suggestion-meta">
                    <span class="badge" style="background: ${color};">${proposal.category}</span>
                </div>
            `;
            
            if (proposal.google_maps_link) {
                card.addEventListener('click', () => {
                    window.open(proposal.google_maps_link, '_blank');
                });
                card.style.cursor = 'pointer';
            }
            
            suggestionsContainer.appendChild(card);
        });
        
        UI.show(UI.elements.aiSuggestions);
    },
    
    getSuggestions: async () => {
        if (!state.currentTrip) return;
        
        try {
            const response = await API.ai.getSuggestions({
                trip_id: state.currentTrip.id,
                query: ''
            });
            
            if (response.suggestions && response.suggestions.length > 0) {
                AIManager.showProposals(response.suggestions);
            }
        } catch (error) {
            console.error('Error getting suggestions:', error);
        }
    }
};
