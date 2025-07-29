/**
 * Enhanced Template Editor JavaScript
 * Handles interactive template building with drag-and-drop functionality
 */

class EnhancedTemplateEditor {
    constructor() {
        this.fields = [];
        this.currentFieldType = null;
        this.editingFieldIndex = -1;
        this.dataTables = [];
        
        this.initializeEventListeners();
        this.initializeSortable();
        this.loadDataTables();
    }
    
    initializeEventListeners() {
        // Field type selection
        document.querySelectorAll('.field-type-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const fieldType = card.dataset.type;
                this.selectFieldType(fieldType);
            });
        });
        
        // Save template
        document.getElementById('saveTemplate').addEventListener('click', () => {
            this.saveTemplate();
        });
        
        // Preview template
        document.getElementById('previewTemplate').addEventListener('click', () => {
            this.previewTemplate();
        });
        
        // Export template
        document.getElementById('exportTemplate').addEventListener('click', () => {
            this.exportTemplate();
        });
        
        // Field configuration form
        document.getElementById('saveFieldConfig').addEventListener('click', () => {
            this.saveFieldConfiguration();
        });
        
        // Conditional logic toggle
        document.getElementById('enableConditionalLogic').addEventListener('change', (e) => {
            document.getElementById('conditionalLogicConfig').style.display = 
                e.target.checked ? 'block' : 'none';
        });
        
        // Field ID auto-generation
        document.getElementById('fieldName').addEventListener('input', (e) => {
            const fieldId = document.getElementById('fieldId');
            if (!fieldId.value) {
                fieldId.value = this.generateFieldId(e.target.value);
            }
        });
    }
    
    initializeSortable() {
        const container = document.getElementById('fieldsContainer');
        Sortable.create(container, {
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            handle: '.drag-handle',
            onEnd: (evt) => {
                // Reorder fields array
                const item = this.fields.splice(evt.oldIndex, 1)[0];
                this.fields.splice(evt.newIndex, 0, item);
                this.updatePreview();
                this.updateFieldNumbers();
            }
        });
    }
    
    selectFieldType(fieldType) {
        // Remove previous selection
        document.querySelectorAll('.field-type-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Add selection to clicked card
        event.target.closest('.field-type-card').classList.add('selected');
        
        this.currentFieldType = fieldType;
        this.editingFieldIndex = -1; // New field
        
        // Show field configuration modal
        this.showFieldConfigModal(fieldType);
    }
    
    showFieldConfigModal(fieldType, fieldData = null) {
        const modal = new bootstrap.Modal(document.getElementById('fieldConfigModal'));
        
        // Reset form
        document.getElementById('fieldConfigForm').reset();
        
        // Set field type specific configuration
        this.configureFieldTypeSettings(fieldType);
        
        // If editing existing field, populate form
        if (fieldData) {
            this.populateFieldForm(fieldData);
        }
        
        modal.show();
    }
    
    configureFieldTypeSettings(fieldType) {
        const configContainer = document.getElementById('fieldTypeConfig');
        configContainer.innerHTML = '';
        
        switch (fieldType) {
            case 'text':
            case 'textarea':
                configContainer.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <label class="form-label">Placeholder Text</label>
                            <input type="text" class="form-control" id="placeholder">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Maximum Length</label>
                            <input type="number" class="form-control" id="maxLength" value="255">
                        </div>
                    </div>
                    ${fieldType === 'textarea' ? `
                    <div class="mt-3">
                        <label class="form-label">Rows</label>
                        <input type="number" class="form-control" id="rows" value="3" min="2" max="10">
                    </div>
                    ` : ''}
                `;
                break;
                
            case 'select':
            case 'multiselect':
            case 'radio':
            case 'checkbox':
                configContainer.innerHTML = `
                    <div class="mb-3">
                        <label class="form-label">Options</label>
                        <div id="optionsContainer">
                            <div class="input-group mb-2">
                                <input type="text" class="form-control option-value" placeholder="Option value">
                                <input type="text" class="form-control option-label" placeholder="Option label">
                                <button class="btn btn-outline-danger" type="button" onclick="this.closest('.input-group').remove()">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                        <button type="button" class="btn btn-outline-primary btn-sm" onclick="this.addOption()">
                            <i class="bi bi-plus"></i> Add Option
                        </button>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="allowOther">
                        <label class="form-check-label" for="allowOther">Allow "Other" option</label>
                    </div>
                `;
                break;
                
            case 'data_table_lookup':
                this.configureDataTableLookup(configContainer);
                break;
                
            case 'dependent_field':
                this.configureDependentField(configContainer);
                break;
                
            case 'autocomplete':
                configContainer.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <label class="form-label">Minimum Search Length</label>
                            <input type="number" class="form-control" id="minSearchLength" value="1" min="1">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Maximum Results</label>
                            <input type="number" class="form-control" id="maxResults" value="10" min="1">
                        </div>
                    </div>
                    <div class="mt-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="allowCustom" checked>
                            <label class="form-check-label" for="allowCustom">Allow custom values</label>
                        </div>
                    </div>
                `;
                break;
                
            case 'date':
                configContainer.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <label class="form-label">Minimum Date</label>
                            <input type="date" class="form-control" id="minDate">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Maximum Date</label>
                            <input type="date" class="form-control" id="maxDate">
                        </div>
                    </div>
                `;
                break;
                
            case 'file_upload':
                configContainer.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <label class="form-label">Maximum File Size (MB)</label>
                            <input type="number" class="form-control" id="maxFileSize" value="10" min="1">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Allowed File Types</label>
                            <input type="text" class="form-control" id="allowedTypes" placeholder="pdf,doc,docx,txt">
                        </div>
                    </div>
                    <div class="mt-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="multipleFiles">
                            <label class="form-check-label" for="multipleFiles">Allow multiple files</label>
                        </div>
                    </div>
                `;
                break;
                
            case 'rating':
                configContainer.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <label class="form-label">Maximum Rating</label>
                            <input type="number" class="form-control" id="maxRating" value="5" min="3" max="10">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Rating Style</label>
                            <select class="form-select" id="ratingStyle">
                                <option value="stars">Stars</option>
                                <option value="numbers">Numbers</option>
                                <option value="scale">Scale</option>
                            </select>
                        </div>
                    </div>
                    <div class="mt-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="allowHalf">
                            <label class="form-check-label" for="allowHalf">Allow half ratings</label>
                        </div>
                    </div>
                `;
                break;
        }
    }
    
    configureDataTableLookup(container) {
        container.innerHTML = `
            <div class="data-table-config">
                <h6><i class="bi bi-table"></i> Data Table Configuration</h6>
                <div class="mb-3">
                    <label class="form-label">Select Data Table</label>
                    <select class="form-select" id="dataTableSelect">
                        <option value="">Select a data table...</option>
                    </select>
                    <div class="form-text">
                        <button type="button" class="btn btn-link btn-sm p-0" onclick="this.openDataTableModal()">
                            View available data tables
                        </button>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="searchable" checked>
                            <label class="form-check-label" for="searchable">Enable search</label>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="multiSelect">
                            <label class="form-check-label" for="multiSelect">Multiple selection</label>
                        </div>
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-md-6">
                        <label class="form-label">Min Search Length</label>
                        <input type="number" class="form-control" id="minSearchLength" value="2" min="1">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Max Results</label>
                        <input type="number" class="form-control" id="maxResults" value="10" min="1">
                    </div>
                </div>
            </div>
        `;
        
        // Populate data table options
        this.populateDataTableSelect();
    }
    
    configureDependentField(container) {
        const parentFields = this.fields.map((field, index) => ({
            value: field.field_id,
            label: field.field_name,
            index: index
        }));
        
        if (parentFields.length === 0) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle"></i>
                    You need to create other fields first before adding a dependent field.
                </div>
            `;
            return;
        }
        
        container.innerHTML = `
            <div class="conditional-logic">
                <h6><i class="bi bi-diagram-3"></i> Dependency Configuration</h6>
                <div class="mb-3">
                    <label class="form-label">Depends On Field</label>
                    <select class="form-select" id="parentField" onchange="this.updateDependentOptions()">
                        <option value="">Select parent field...</option>
                        ${parentFields.map(field => 
                            `<option value="${field.value}">${field.label}</option>`
                        ).join('')}
                    </select>
                </div>
                <div id="dependentOptionsConfig">
                    <!-- Options will be populated based on parent field selection -->
                </div>
            </div>
        `;
    }
    
    updateDependentOptions() {
        const parentFieldId = document.getElementById('parentField').value;
        const parentField = this.fields.find(f => f.field_id === parentFieldId);
        const container = document.getElementById('dependentOptionsConfig');
        
        if (!parentField || !parentField.config.options) {
            container.innerHTML = `
                <div class="alert alert-info">
                    Select a parent field with options to configure dependencies.
                </div>
            `;
            return;
        }
        
        container.innerHTML = `
            <div class="mb-3">
                <label class="form-label">Options Based on Parent Field Value</label>
                ${parentField.config.options.map(option => `
                    <div class="border rounded p-3 mb-2">
                        <h6>When "${parentField.field_name}" = "${option.label}"</h6>
                        <div id="options-${option.value}">
                            <div class="input-group mb-2">
                                <input type="text" class="form-control" placeholder="Option value" name="dep-value-${option.value}">
                                <input type="text" class="form-control" placeholder="Option label" name="dep-label-${option.value}">
                                <button class="btn btn-outline-danger" type="button" onclick="this.closest('.input-group').remove()">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                        <button type="button" class="btn btn-outline-primary btn-sm" onclick="this.addDependentOption('${option.value}')">
                            <i class="bi bi-plus"></i> Add Option
                        </button>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    addDependentOption(parentValue) {
        const container = document.getElementById(`options-${parentValue}`);
        const optionHtml = `
            <div class="input-group mb-2">
                <input type="text" class="form-control" placeholder="Option value" name="dep-value-${parentValue}">
                <input type="text" class="form-control" placeholder="Option label" name="dep-label-${parentValue}">
                <button class="btn btn-outline-danger" type="button" onclick="this.closest('.input-group').remove()">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', optionHtml);
    }
    
    addOption() {
        const container = document.getElementById('optionsContainer');
        const optionHtml = `
            <div class="input-group mb-2">
                <input type="text" class="form-control option-value" placeholder="Option value">
                <input type="text" class="form-control option-label" placeholder="Option label">
                <button class="btn btn-outline-danger" type="button" onclick="this.closest('.input-group').remove()">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', optionHtml);
    }
    
    saveFieldConfiguration() {
        const form = document.getElementById('fieldConfigForm');
        const formData = new FormData(form);
        
        // Collect basic field data
        const fieldData = {
            field_id: document.getElementById('fieldId').value,
            field_name: document.getElementById('fieldName').value,
            field_type: this.currentFieldType,
            is_required: document.getElementById('fieldRequired').checked ? 1 : 0,
            config: {},
            validation_rules: {},
            dependencies: []
        };
        
        // Collect field-specific configuration
        this.collectFieldTypeConfig(fieldData);
        
        // Collect validation rules
        this.collectValidationRules(fieldData);
        
        // Collect conditional logic
        if (document.getElementById('enableConditionalLogic').checked) {
            this.collectConditionalLogic(fieldData);
        }
        
        // Add or update field
        if (this.editingFieldIndex >= 0) {
            this.fields[this.editingFieldIndex] = fieldData;
        } else {
            this.fields.push(fieldData);
        }
        
        // Update UI
        this.updateFieldsList();
        this.updatePreview();
        this.updateStatistics();
        
        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('fieldConfigModal')).hide();
    }
    
    collectFieldTypeConfig(fieldData) {
        switch (fieldData.field_type) {
            case 'text':
            case 'textarea':
                fieldData.config.placeholder = document.getElementById('placeholder')?.value || '';
                fieldData.config.maxLength = parseInt(document.getElementById('maxLength')?.value) || 255;
                if (fieldData.field_type === 'textarea') {
                    fieldData.config.rows = parseInt(document.getElementById('rows')?.value) || 3;
                }
                break;
                
            case 'select':
            case 'multiselect':
            case 'radio':
            case 'checkbox':
                fieldData.config.options = this.collectOptions();
                fieldData.config.allowOther = document.getElementById('allowOther')?.checked || false;
                break;
                
            case 'data_table_lookup':
                fieldData.config.dataTableId = document.getElementById('dataTableSelect')?.value || '';
                fieldData.config.searchable = document.getElementById('searchable')?.checked || true;
                fieldData.config.multiSelect = document.getElementById('multiSelect')?.checked || false;
                fieldData.config.minSearchLength = parseInt(document.getElementById('minSearchLength')?.value) || 2;
                fieldData.config.maxResults = parseInt(document.getElementById('maxResults')?.value) || 10;
                break;
                
            case 'dependent_field':
                fieldData.config.dependsOn = document.getElementById('parentField')?.value || '';
                fieldData.config.optionsMap = this.collectDependentOptions();
                break;
                
            case 'file_upload':
                fieldData.config.maxFileSize = parseInt(document.getElementById('maxFileSize')?.value) || 10;
                fieldData.config.allowedTypes = (document.getElementById('allowedTypes')?.value || '').split(',').map(t => t.trim());
                fieldData.config.multipleFiles = document.getElementById('multipleFiles')?.checked || false;
                break;
                
            case 'rating':
                fieldData.config.maxRating = parseInt(document.getElementById('maxRating')?.value) || 5;
                fieldData.config.ratingStyle = document.getElementById('ratingStyle')?.value || 'stars';
                fieldData.config.allowHalf = document.getElementById('allowHalf')?.checked || false;
                break;
        }
    }
    
    collectOptions() {
        const options = [];
        const optionGroups = document.querySelectorAll('#optionsContainer .input-group');
        
        optionGroups.forEach(group => {
            const value = group.querySelector('.option-value').value.trim();
            const label = group.querySelector('.option-label').value.trim();
            
            if (value) {
                options.push({
                    value: value,
                    label: label || value
                });
            }
        });
        
        return options;
    }
    
    collectDependentOptions() {
        const optionsMap = {};
        const parentFieldId = document.getElementById('parentField')?.value;
        const parentField = this.fields.find(f => f.field_id === parentFieldId);
        
        if (!parentField || !parentField.config.options) {
            return optionsMap;
        }
        
        parentField.config.options.forEach(option => {
            const valueInputs = document.querySelectorAll(`input[name="dep-value-${option.value}"]`);
            const labelInputs = document.querySelectorAll(`input[name="dep-label-${option.value}"]`);
            
            const options = [];
            valueInputs.forEach((valueInput, index) => {
                const value = valueInput.value.trim();
                const label = labelInputs[index]?.value.trim();
                
                if (value) {
                    options.push({
                        value: value,
                        label: label || value
                    });
                }
            });
            
            optionsMap[option.value] = options;
        });
        
        return optionsMap;
    }
    
    collectValidationRules(fieldData) {
        // Basic validation rules based on field type
        if (fieldData.field_type === 'text' || fieldData.field_type === 'textarea') {
            const minLength = document.getElementById('minLength')?.value;
            const maxLength = document.getElementById('maxLength')?.value;
            
            if (minLength) fieldData.validation_rules.minLength = parseInt(minLength);
            if (maxLength) fieldData.validation_rules.maxLength = parseInt(maxLength);
        }
    }
    
    collectConditionalLogic(fieldData) {
        // This would collect conditional logic rules
        // Implementation depends on the UI design for conditional logic
    }
    
    updateFieldsList() {
        const container = document.getElementById('fieldsContainer');
        const emptyMessage = document.getElementById('emptyFieldsMessage');
        
        if (this.fields.length === 0) {
            container.innerHTML = '';
            emptyMessage.style.display = 'block';
            return;
        }
        
        emptyMessage.style.display = 'none';
        
        container.innerHTML = this.fields.map((field, index) => `
            <div class="field-card sortable-field" data-index="${index}">
                <div class="field-actions">
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="templateEditor.editField(${index})">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="templateEditor.deleteField(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                    <span class="drag-handle ms-2">
                        <i class="bi bi-grip-vertical"></i>
                    </span>
                </div>
                
                <div class="d-flex align-items-center mb-2">
                    <i class="bi ${this.getFieldTypeIcon(field.field_type)} field-type-icon"></i>
                    <strong>${field.field_name}</strong>
                    ${field.is_required ? '<span class="badge bg-warning ms-2">Required</span>' : ''}
                </div>
                
                <div class="text-muted small mb-2">
                    Type: ${this.getFieldTypeLabel(field.field_type)} | ID: ${field.field_id}
                </div>
                
                ${this.renderFieldPreview(field)}
                
                ${field.dependencies && field.dependencies.length > 0 ? `
                    <div class="dependency-rule">
                        <i class="bi bi-diagram-3"></i> Has ${field.dependencies.length} dependency rule(s)
                    </div>
                ` : ''}
            </div>
        `).join('');
    }
    
    renderFieldPreview(field) {
        let preview = '<div class="field-preview">';
        
        switch (field.field_type) {
            case 'text':
                preview += `<input type="text" class="form-control" placeholder="${field.config.placeholder || ''}" disabled>`;
                break;
                
            case 'textarea':
                preview += `<textarea class="form-control" rows="${field.config.rows || 3}" placeholder="${field.config.placeholder || ''}" disabled></textarea>`;
                break;
                
            case 'select':
                preview += '<select class="form-select" disabled>';
                preview += '<option>Select an option...</option>';
                (field.config.options || []).forEach(option => {
                    preview += `<option>${option.label}</option>`;
                });
                preview += '</select>';
                break;
                
            case 'radio':
                (field.config.options || []).slice(0, 3).forEach(option => {
                    preview += `
                        <div class="form-check">
                            <input class="form-check-input" type="radio" disabled>
                            <label class="form-check-label">${option.label}</label>
                        </div>
                    `;
                });
                if (field.config.options && field.config.options.length > 3) {
                    preview += `<div class="text-muted small">... and ${field.config.options.length - 3} more options</div>`;
                }
                break;
                
            case 'checkbox':
                (field.config.options || []).slice(0, 3).forEach(option => {
                    preview += `
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" disabled>
                            <label class="form-check-label">${option.label}</label>
                        </div>
                    `;
                });
                break;
                
            case 'data_table_lookup':
                preview += '<select class="form-select" disabled>';
                preview += '<option>Search data table...</option>';
                preview += '</select>';
                preview += `<small class="text-muted">Connected to data table: ${field.config.dataTableId || 'Not selected'}</small>`;
                break;
                
            case 'dependent_field':
                preview += '<select class="form-select" disabled>';
                preview += '<option>Depends on other field...</option>';
                preview += '</select>';
                preview += `<small class="text-muted">Depends on: ${field.config.dependsOn || 'Not configured'}</small>`;
                break;
                
            case 'file_upload':
                preview += '<input type="file" class="form-control" disabled>';
                preview += `<small class="text-muted">Max size: ${field.config.maxFileSize || 10}MB, Types: ${(field.config.allowedTypes || []).join(', ') || 'Any'}</small>`;
                break;
                
            case 'rating':
                const stars = '★'.repeat(field.config.maxRating || 5);
                preview += `<div class="text-warning">${stars}</div>`;
                break;
                
            default:
                preview += `<input type="${field.field_type}" class="form-control" disabled>`;
        }
        
        preview += '</div>';
        return preview;
    }
    
    getFieldTypeIcon(fieldType) {
        const iconMap = {
            'text': 'bi-input-cursor-text',
            'textarea': 'bi-textarea-t',
            'select': 'bi-menu-button-wide',
            'multiselect': 'bi-menu-button-wide',
            'radio': 'bi-record-circle',
            'checkbox': 'bi-check-square',
            'data_table_lookup': 'bi-table',
            'dependent_field': 'bi-diagram-3',
            'autocomplete': 'bi-search',
            'date': 'bi-calendar-date',
            'file_upload': 'bi-file-earmark-arrow-up',
            'rating': 'bi-star',
            'toggle': 'bi-toggle-on'
        };
        
        return iconMap[fieldType] || 'bi-input-cursor';
    }
    
    getFieldTypeLabel(fieldType) {
        const labelMap = {
            'text': 'Text Input',
            'textarea': 'Multi-line Text',
            'select': 'Dropdown',
            'multiselect': 'Multi-Select',
            'radio': 'Radio Buttons',
            'checkbox': 'Checkboxes',
            'data_table_lookup': 'Data Lookup',
            'dependent_field': 'Dependent Field',
            'autocomplete': 'Autocomplete',
            'date': 'Date Picker',
            'file_upload': 'File Upload',
            'rating': 'Star Rating',
            'toggle': 'Toggle Switch'
        };
        
        return labelMap[fieldType] || fieldType;
    }
    
    editField(index) {
        this.editingFieldIndex = index;
        const field = this.fields[index];
        this.currentFieldType = field.field_type;
        this.showFieldConfigModal(field.field_type, field);
    }
    
    deleteField(index) {
        if (confirm('Are you sure you want to delete this field?')) {
            this.fields.splice(index, 1);
            this.updateFieldsList();
            this.updatePreview();
            this.updateStatistics();
        }
    }
    
    updatePreview() {
        const container = document.getElementById('previewContainer');
        
        if (this.fields.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="bi bi-eye-slash" style="font-size: 3rem;"></i>
                    <p class="mt-3">Add fields to see preview</p>
                </div>
            `;
            return;
        }
        
        const templateName = document.getElementById('templateName').value || 'New Template';
        const templateDescription = document.getElementById('templateDescription').value;
        
        let previewHtml = `
            <h5>${templateName}</h5>
            ${templateDescription ? `<p class="text-muted">${templateDescription}</p>` : ''}
            <hr>
        `;
        
        this.fields.forEach(field => {
            previewHtml += `
                <div class="mb-3">
                    <label class="form-label">
                        ${field.field_name}
                        ${field.is_required ? '<span class="text-danger">*</span>' : ''}
                    </label>
                    ${this.renderFieldPreview(field)}
                </div>
            `;
        });
        
        container.innerHTML = previewHtml;
    }
    
    updateStatistics() {
        document.getElementById('fieldCount').textContent = this.fields.length;
        document.getElementById('requiredCount').textContent = this.fields.filter(f => f.is_required).length;
        document.getElementById('dependencyCount').textContent = this.fields.filter(f => f.dependencies && f.dependencies.length > 0).length;
    }
    
    updateFieldNumbers() {
        document.querySelectorAll('.field-card').forEach((card, index) => {
            card.dataset.index = index;
        });
    }
    
    generateFieldId(fieldName) {
        return fieldName.toLowerCase()
                      .replace(/[^a-z0-9\s]/gi, '')
                      .replace(/\s+/g, '_')
                      .substring(0, 50);
    }
    
    populateFieldForm(fieldData) {
        document.getElementById('fieldId').value = fieldData.field_id;
        document.getElementById('fieldName').value = fieldData.field_name;
        document.getElementById('fieldRequired').checked = fieldData.is_required;
        
        // Populate field-specific configuration
        // This would need to be implemented for each field type
    }
    
    populateDataTableSelect() {
        const select = document.getElementById('dataTableSelect');
        if (!select) return;
        
        select.innerHTML = '<option value="">Select a data table...</option>';
        
        this.dataTables.forEach(table => {
            const option = document.createElement('option');
            option.value = table.id;
            option.textContent = `${table.display_name} (${table.record_count || 0} records)`;
            select.appendChild(option);
        });
    }
    
    loadDataTables() {
        // This would load data tables from the server
        // For now, using mock data
        this.dataTables = [
            { id: 1, table_name: 'departments', display_name: 'Departments', record_count: 4 },
            { id: 2, table_name: 'categories', display_name: 'Issue Categories', record_count: 8 }
        ];
    }
    
    saveTemplate() {
        const templateData = {
            name: document.getElementById('templateName').value,
            description: document.getElementById('templateDescription').value,
            category: document.getElementById('templateCategory').value,
            fields: this.fields
        };
        
        if (!templateData.name) {
            alert('Please enter a template name');
            return;
        }
        
        if (this.fields.length === 0) {
            alert('Please add at least one field');
            return;
        }
        
        // Send to server
        fetch('/enhanced/api/templates/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(templateData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Template saved successfully!');
            } else {
                alert('Error saving template: ' + data.message);
            }
        })
        .catch(error => {
            alert('Error saving template: ' + error.message);
        });
    }
    
    previewTemplate() {
        // Open template in a new window for preview
        const templateData = {
            name: document.getElementById('templateName').value || 'Template Preview',
            description: document.getElementById('templateDescription').value,
            fields: this.fields
        };
        
        const previewWindow = window.open('', '_blank', 'width=800,height=600');
        previewWindow.document.write(this.generatePreviewHTML(templateData));
    }
    
    generatePreviewHTML(templateData) {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <title>${templateData.name} - Preview</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-4">
                    <h2>${templateData.name}</h2>
                    ${templateData.description ? `<p class="text-muted">${templateData.description}</p>` : ''}
                    <hr>
                    <form>
                        ${templateData.fields.map(field => `
                            <div class="mb-3">
                                <label class="form-label">
                                    ${field.field_name}
                                    ${field.is_required ? '<span class="text-danger">*</span>' : ''}
                                </label>
                                ${this.renderFieldPreview(field)}
                            </div>
                        `).join('')}
                        <button type="button" class="btn btn-primary">Submit</button>
                    </form>
                </div>
            </body>
            </html>
        `;
    }
    
    exportTemplate() {
        const templateData = {
            name: document.getElementById('templateName').value,
            description: document.getElementById('templateDescription').value,
            category: document.getElementById('templateCategory').value,
            fields: this.fields,
            version: '1.0',
            exported_at: new Date().toISOString()
        };
        
        const dataStr = JSON.stringify(templateData, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `${templateData.name.replace(/[^a-z0-9]/gi, '_')}_template.json`;
        link.click();
    }
}

// Initialize the template editor when the page loads
let templateEditor;
document.addEventListener('DOMContentLoaded', function() {
    templateEditor = new EnhancedTemplateEditor();
    
    // Make some methods globally accessible for onclick handlers
    window.addOption = templateEditor.addOption.bind(templateEditor);
    window.addDependentOption = templateEditor.addDependentOption.bind(templateEditor);
    window.updateDependentOptions = templateEditor.updateDependentOptions.bind(templateEditor);
});
