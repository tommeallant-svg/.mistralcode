/**
 * Road - Step Manager
 */

const StepManager = {
    list: async (tripId) => {
        try {
            const response = await API.steps.listForTable(tripId, {
                category: state.filters.category
            });
            
            state.currentSteps = response;
            StepManager.renderStepTable();
            
            if (state.currentSteps.length === 0) {
                UI.show(UI.elements.noSteps);
            } else {
                UI.hide(UI.elements.noSteps);
            }
            
            return response;
        } catch (error) {
            UI.showToast(error.message || 'Échec du chargement des étapes', 'error');
            return [];
        }
    },
    
    get: async (id) => {
        try {
            UI.showLoading();
            const step = await API.steps.get(id);
            state.currentStep = step;
            return step;
        } catch (error) {
            UI.showToast(error.message || 'Échec du chargement de l\'étape', 'error');
            return null;
        } finally {
            UI.hideLoading();
        }
    },
    
    create: async (data) => {
        try {
            UI.showLoading();
            const response = await API.steps.create(data);
            UI.showToast('Étape créée avec succès !', 'success');
            
            if (state.currentTrip) {
                await StepManager.list(state.currentTrip.id);
                await TripManager.get(state.currentTrip.id);
                TripManager.renderTripDetail();
            }
            
            UI.hide(UI.elements.stepModal);
            return response;
        } catch (error) {
            UI.showToast(error.message || 'Échec de la création de l\'étape', 'error');
            return null;
        } finally {
            UI.hideLoading();
        }
    },
    
    update: async (id, data) => {
        try {
            UI.showLoading();
            const response = await API.steps.update(id, data);
            UI.showToast('Étape mise à jour avec succès !', 'success');
            
            if (state.currentTrip) {
                await StepManager.list(state.currentTrip.id);
                await TripManager.get(state.currentTrip.id);
                TripManager.renderTripDetail();
            }
            
            UI.hide(UI.elements.stepModal);
            return response;
        } catch (error) {
            UI.showToast(error.message || 'Échec de la mise à jour de l\'étape', 'error');
            return null;
        } finally {
            UI.hideLoading();
        }
    },
    
    delete: async (id) => {
        try {
            UI.showLoading();
            await API.steps.delete(id);
            UI.showToast('Étape supprimée avec succès !', 'success');
            
            if (state.currentTrip) {
                await StepManager.list(state.currentTrip.id);
                await TripManager.get(state.currentTrip.id);
                TripManager.renderTripDetail();
            }
            
            return true;
        } catch (error) {
            UI.showToast(error.message || 'Échec de la suppression de l\'étape', 'error');
            return false;
        } finally {
            UI.hideLoading();
        }
    },
    
    duplicate: async (id) => {
        try {
            UI.showLoading();
            const response = await API.steps.duplicate(id);
            UI.showToast('Étape dupliquée avec succès !', 'success');
            
            if (state.currentTrip) {
                await StepManager.list(state.currentTrip.id);
            }
            
            return response;
        } catch (error) {
            UI.showToast(error.message || 'Échec de la duplication de l\'étape', 'error');
            return null;
        } finally {
            UI.hideLoading();
        }
    },
    
    reorder: async (stepIds) => {
        try {
            UI.showLoading();
            const response = await API.steps.reorder({
                trip_id: state.currentTrip.id,
                step_ids: stepIds
            });
            
            UI.showToast('Ordre des étapes mis à jour !', 'success');
            
            if (state.currentTrip) {
                await StepManager.list(state.currentTrip.id);
            }
            
            return response;
        } catch (error) {
            UI.showToast(error.message || 'Échec de la réorganisation des étapes', 'error');
            return null;
        } finally {
            UI.hideLoading();
        }
    },
    
    renderStepTable: () => {
        const tbody = UI.elements.stepTableBody;
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (state.currentSteps.length === 0) return;
        
        const sortedSteps = [...state.currentSteps].sort((a, b) => a.order_index - b.order_index);
        
        sortedSteps.forEach(step => {
            const row = document.createElement('tr');
            row.dataset.id = step.id;
            row.dataset.order = step.order_index;
            row.className = 'step-row';
            
            const categoryColor = Utils.getCategoryColor(step.category);
            
            row.innerHTML = `
                <td class="sortable-handle" style="cursor: move;">
                    <i class="fas fa-grip-vertical"></i>
                </td>
                <td style="font-weight: 500;">${Utils.truncate(step.name, 30)}</td>
                <td>
                    <span class="category-cell">
                        <span class="category-indicator" style="background: ${categoryColor};"></span>
                        ${step.category}
                    </span>
                </td>
                <td>${step.type || '-'}</td>
                <td>${Utils.formatDate(step.start_datetime, 'dateTime')}</td>
                <td>${step.end_datetime ? Utils.formatDate(step.end_datetime, 'dateTime') : '-'}</td>
                <td>${step.location_start || step.location_end || '-'}</td>
                <td>
                    <div class="action-btns">
                        <button class="action-btn edit" title="Modifier" data-id="${step.id}"><i class="fas fa-edit"></i></button>
                        <button class="action-btn duplicate" title="Dupliquer" data-id="${step.id}"><i class="fas fa-copy"></i></button>
                        <button class="action-btn delete" title="Supprimer" data-id="${step.id}"><i class="fas fa-trash"></i></button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        StepManager.setupStepTableListeners();
    },
    
    setupStepTableListeners: () => {
        document.querySelectorAll('#step-table-body .action-btn.edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const stepId = btn.dataset.id;
                StepManager.showEditStepModal(stepId);
            });
        });
        
        document.querySelectorAll('#step-table-body .action-btn.duplicate').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const stepId = btn.dataset.id;
                StepManager.duplicate(stepId);
            });
        });
        
        document.querySelectorAll('#step-table-body .action-btn.delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const stepId = btn.dataset.id;
                StepManager.showDeleteConfirmation(stepId);
            });
        });
        
        StepManager.setupDragAndDrop();
    },
    
    setupDragAndDrop: () => {
        const tbody = UI.elements.stepTableBody;
        if (!tbody) return;
        
        let draggedRow = null;
        
        tbody.querySelectorAll('tr.step-row').forEach(row => {
            row.draggable = true;
            
            row.addEventListener('dragstart', (e) => {
                draggedRow = row;
                row.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
            });
            
            row.addEventListener('dragend', () => {
                row.classList.remove('dragging');
                draggedRow = null;
            });
        });
        
        tbody.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        });
        
        tbody.addEventListener('drop', (e) => {
            e.preventDefault();
            if (!draggedRow) return;
            
            const targetRow = e.target.closest('tr.step-row');
            if (!targetRow || targetRow === draggedRow) return;
            
            const rows = Array.from(tbody.querySelectorAll('tr.step-row'));
            const draggedIndex = rows.indexOf(draggedRow);
            const targetIndex = rows.indexOf(targetRow);
            
            if (draggedIndex === -1 || targetIndex === -1) return;
            
            if (draggedIndex < targetIndex) {
                tbody.insertBefore(draggedRow, targetRow.nextSibling);
            } else {
                tbody.insertBefore(draggedRow, targetRow);
            }
            
            const stepIds = [];
            rows.forEach((row, index) => {
                const stepId = parseInt(row.dataset.id);
                if (!isNaN(stepId)) {
                    stepIds.push(stepId);
                }
            });
            
            StepManager.reorder(stepIds);
        });
    },
    
    showNewStepModal: () => {
        if (!state.currentTrip) return;
        
        const modal = UI.elements.stepModal;
        const form = UI.elements.stepForm;
        
        if (!modal || !form) return;
        
        form.reset();
        UI.elements.stepIdInput.value = '';
        UI.elements.stepTripIdInput.value = state.currentTrip.id;
        UI.elements.stepModalTitle.textContent = 'Nouvelle Étape';
        
        UI.elements.stepColor.value = '#3B82F6';
        UI.elements.stepCategory.value = '';
        
        if (state.currentTrip.start_date) {
            UI.elements.stepStartDatetime.value = Utils.formatDateForInput(state.currentTrip.start_date);
        }
        
        UI.show(modal);
        StepManager.updateTypeOptions();
    },
    
    showEditStepModal: async (stepId) => {
        try {
            const step = await StepManager.get(stepId);
            if (!step) return;
            
            const modal = UI.elements.stepModal;
            const form = UI.elements.stepForm;
            
            if (!modal || !form) return;
            
            UI.elements.stepIdInput.value = step.id;
            UI.elements.stepTripIdInput.value = step.trip_id;
            UI.elements.stepName.value = step.name || '';
            UI.elements.stepCategory.value = step.category || '';
            UI.elements.stepType.value = step.type || '';
            UI.elements.stepColor.value = step.color || '#3B82F6';
            UI.elements.stepStartDatetime.value = Utils.formatDateForInput(step.start_datetime);
            UI.elements.stepEndDatetime.value = step.end_datetime ? Utils.formatDateForInput(step.end_datetime) : '';
            UI.elements.stepLocationStart.value = step.location_start || '';
            UI.elements.stepLocationEnd.value = step.location_end || '';
            UI.elements.stepLatitudeStart.value = step.latitude_start || '';
            UI.elements.stepLongitudeStart.value = step.longitude_start || '';
            UI.elements.stepLatitudeEnd.value = step.latitude_end || '';
            UI.elements.stepLongitudeEnd.value = step.longitude_end || '';
            UI.elements.stepNotes.value = step.notes || '';
            
            UI.elements.stepModalTitle.textContent = 'Modifier l\'Étape';
            UI.show(modal);
            
            StepManager.updateTypeOptions(step.category);
        } catch (error) {
            UI.showToast(error.message || 'Échec du chargement de l\'étape', 'error');
        }
    },
    
    showDeleteConfirmation: (stepId) => {
        const step = state.currentSteps.find(s => s.id === parseInt(stepId));
        if (!step) return;
        
        if (confirm(`Voulez-vous vraiment supprimer l'étape "${step.name}" ?`)) {
            StepManager.delete(stepId);
        }
    },
    
    updateTypeOptions: (category = '') => {
        const typeSelect = UI.elements.stepType;
        if (!typeSelect) return;
        
        typeSelect.innerHTML = '<option value="">Sélectionnez...</option>';
        
        if (category === 'transport') {
            CONFIG.transportTypes.transport.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = Utils.capitalize(type);
                typeSelect.appendChild(option);
            });
        } else if (CONFIG.categoryTypes[category]) {
            CONFIG.categoryTypes[category].forEach(type => {
                const option = document.createElement('option');
                option.value = type.toLowerCase();
                option.textContent = type;
                typeSelect.appendChild(option);
            });
        }
    }
};
