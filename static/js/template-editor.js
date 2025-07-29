// Template Editor JavaScript
let fieldIndex = 0;
let availableDataTables = [];
let allFields = [];

// Initialize the template editor when DOM loads
document.addEventListener('DOMContentLoaded', function() {
    const templateData = document.getElementById('templateData');
    if (templateData) {
        const fieldCount = parseInt(templateData.dataset.fieldCount) || 3;
        const hasTemplate = templateData.dataset.hasTemplate === 'true';
        
        initializeFieldIndex(fieldCount);
        
        // Load available data tables
        loadAvailableDataTables();
        
        // Always update field numbers on page load to ensure consistency
        setTimeout(function() {
            updateAllFieldNumbers();
            updateFieldRelationshipDropdowns();
        }, 50);
        
        if (hasTemplate && templateData.dataset.fields) {
            try {
                const fields = JSON.parse(templateData.dataset.fields);
                allFields = fields;
                initializeExistingFields(fields);
            } catch (e) {
                console.error('Error parsing field data:', e);
            }
        } else {
            // Initialize default fields - textarea for body field
            setTimeout(function() {
                toggleFieldOptions(2, 'textarea');
            }, 100);
        }
    }
    
    // Initialize event delegation for dynamic elements
    initializeEventDelegation();
});

function loadAvailableDataTables() {
    fetch('/api/data-tables')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                availableDataTables = data.tables;
                updateAllTableSelects();
                
                // Initialize existing data sources after tables are loaded
                setTimeout(() => {
                    initializeExistingDataSources();
                }, 500);
            }
        })
        .catch(error => console.error('Error loading data tables:', error));
}

function updateAllTableSelects() {
    document.querySelectorAll('.table-select, .text-table-select').forEach(select => {
        updateTableSelect(select);
    });
}

function updateTableSelect(selectElement) {
    // Store current value
    const currentValue = selectElement.value;
    
    // Clear existing options except the first one
    while (selectElement.children.length > 1) {
        selectElement.removeChild(selectElement.lastChild);
    }
    
    // Add data table options
    availableDataTables.forEach(table => {
        const option = document.createElement('option');
        option.value = table.table_name;
        option.textContent = `${table.display_name} (${table.row_count} rows)`;
        selectElement.appendChild(option);
    });
    
    // Restore previous value if it still exists
    if (currentValue) {
        selectElement.value = currentValue;
    }
}

function initializeEventDelegation() {
    const fieldsContainer = document.getElementById('fieldsContainer');
    if (!fieldsContainer) return;
    
    // Handle field type changes
    fieldsContainer.addEventListener('change', function(e) {
        if (e.target.classList.contains('field-type-select')) {
            const fieldContainer = e.target.closest('.field-editor');
            const fieldIndex = fieldContainer.dataset.fieldIndex;
            if (fieldIndex !== undefined) {
                toggleFieldOptions(parseInt(fieldIndex), e.target.value);
            }
        }
        
        // Handle data source type changes
        if (e.target.classList.contains('data-source-type-select')) {
            handleDataSourceTypeChange(e.target);
        }
        
        // Handle table selections
        if (e.target.classList.contains('table-select')) {
            handleTableSelection(e.target);
        }
        
        // Handle text field data source changes
        if (e.target.classList.contains('text-data-source-select')) {
            handleTextDataSourceChange(e.target);
        }
        
        // Handle text table selections
        if (e.target.classList.contains('text-table-select')) {
            handleTextTableChange(e.target);
        }
    });
    
    // Handle remove field buttons
    fieldsContainer.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-field-btn') || 
            e.target.closest('.remove-field-btn')) {
            const fieldContainer = e.target.closest('.field-editor');
            if (fieldContainer) {
                const fieldIndex = parseInt(fieldContainer.dataset.fieldIndex);
                removeField(fieldIndex);
            }
        }
        
        // Handle add option buttons
        if (e.target.closest('[data-action="add-option"]')) {
            const fieldIndex = e.target.closest('[data-action="add-option"]').getAttribute('data-field-index');
            addOption(fieldIndex);
        }
        
        // Handle remove option buttons
        if (e.target.closest('[data-action="remove-option"]')) {
            e.target.closest('.row').remove();
        }
        
        // Handle add dependent field buttons
        if (e.target.classList.contains('add-dependent-field-btn') || 
            e.target.closest('.add-dependent-field-btn')) {
            e.preventDefault();
            const button = e.target.closest('.add-dependent-field-btn');
            const fieldIndex = button.dataset.fieldIndex;
            addDependentField(fieldIndex);
        }
        
        // Handle remove dependent field buttons
        if (e.target.classList.contains('remove-dependent-btn') || 
            e.target.closest('.remove-dependent-btn')) {
            e.preventDefault();
            removeDependentField(e.target.closest('.remove-dependent-btn'));
        }
    });
    
    // Handle input changes to update field relationship dropdowns
    fieldsContainer.addEventListener('input', function(e) {
        if (e.target.name && e.target.name.match(/^field_\d+_id$/)) {
            setTimeout(() => updateFieldRelationshipDropdowns(), 100);
        }
    });
}

function initializeFieldIndex(count) {
    fieldIndex = count;
}

function addField() {
    const container = document.getElementById('fieldsContainer');
    const template = document.getElementById('fieldTemplate').innerHTML;
    
    // Replace INDEX placeholders with actual field index
    const newField = template.replace(/INDEX/g, fieldIndex);
    
    // Create new field container
    const fieldDiv = document.createElement('div');
    fieldDiv.innerHTML = newField;
    
    // Ensure the field editor has the correct class and data attribute
    const fieldEditor = fieldDiv.querySelector('.field-editor');
    if (fieldEditor) {
        fieldEditor.setAttribute('data-field-index', fieldIndex);
        
        // Update the field number display
        const fieldNumberHeader = fieldEditor.querySelector('h6');
        if (fieldNumberHeader) {
            fieldNumberHeader.textContent = `Field ${fieldIndex + 1}`;
        }
    }
    
    // Append to container
    container.appendChild(fieldDiv.firstElementChild);
    fieldIndex++;
    
    // Re-number all existing fields to ensure proper sequential numbering
    updateAllFieldNumbers();
    
    // Initialize field options for the new field
    setTimeout(function() {
        const newFieldElement = container.querySelector(`[data-field-index="${fieldIndex - 1}"]`);
        if (newFieldElement) {
            const typeSelect = newFieldElement.querySelector('.field-type-select');
            if (typeSelect) {
                toggleFieldOptions(fieldIndex - 1, typeSelect.value);
            }
        }
    }, 100);
}

function removeField(index) {
    const fieldDiv = document.querySelector(`[data-field-index="${index}"]`);
    if (fieldDiv) {
        fieldDiv.remove();
        // Re-number all remaining fields after removal
        updateAllFieldNumbers();
    }
}

// New function to update field numbering
function updateAllFieldNumbers() {
    const fieldEditors = document.querySelectorAll('.field-editor');
    fieldEditors.forEach((fieldEditor, index) => {
        // Update data attribute
        fieldEditor.setAttribute('data-field-index', index);
        
        // Update field number display
        const fieldNumberHeader = fieldEditor.querySelector('h6');
        if (fieldNumberHeader) {
            fieldNumberHeader.textContent = `Field ${index + 1}`;
        }
        
        // Update all form field names to use correct index
        const inputs = fieldEditor.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            const name = input.getAttribute('name');
            if (name && name.startsWith('field_')) {
                // Replace the index in the field name
                const newName = name.replace(/field_\d+_/, `field_${index}_`);
                input.setAttribute('name', newName);
            }
        });
        
        // Update remove button data-index
        const removeBtn = fieldEditor.querySelector('.remove-field-btn');
        if (removeBtn) {
            removeBtn.setAttribute('data-index', index);
        }
    });
}

function toggleFieldOptions(index, fieldType) {
    const fieldEditor = document.querySelector(`[data-field-index="${index}"]`);
    if (!fieldEditor) return;
    
    // Hide all type-specific options first
    const allOptions = fieldEditor.querySelectorAll('.field-type-option');
    allOptions.forEach(option => {
        option.style.display = 'none';
    });
    
    // Show relevant options based on field type
    const relevantOptions = fieldEditor.querySelectorAll(`[data-types*="${fieldType}"]`);
    relevantOptions.forEach(option => {
        option.style.display = 'block';
    });
    
    // Initialize data source handlers for the field
    if (fieldType === 'text') {
        initializeTextFieldDataSource(index);
    } else if (fieldType === 'select' || fieldType === 'radio') {
        initializeSelectFieldDataSource(index);
    }
}

function initializeTextFieldDataSource(fieldIndex) {
    const dataSourceSelect = document.querySelector(`select[name="field_${fieldIndex}_text_data_source"]`);
    if (dataSourceSelect) {
        handleTextDataSourceChange(dataSourceSelect);
    }
}

function initializeSelectFieldDataSource(fieldIndex) {
    const dataSourceTypeSelect = document.querySelector(`select[name="field_${fieldIndex}_data_source_type"]`);
    if (dataSourceTypeSelect) {
        handleDataSourceTypeChange(dataSourceTypeSelect);
    }
}

// Handle data source type changes for select/radio fields
function handleDataSourceTypeChange(selectElement) {
    const fieldIndex = selectElement.dataset.fieldIndex;
    const selectedType = selectElement.value;
    
    // Hide all data source config sections
    document.querySelectorAll(`#field_${fieldIndex}_options .data-source-config`).forEach(config => {
        config.style.display = 'none';
    });
    
    // Show the selected data source config
    const selectedConfig = document.querySelector(`#field_${fieldIndex}_options .data-source-config[data-source-type="${selectedType}"]`);
    if (selectedConfig) {
        selectedConfig.style.display = 'block';
    }
}

// Handle text field data source changes
function handleTextDataSourceChange(select) {
    const fieldIndex = select.dataset.fieldIndex;
    const dataSource = select.value;
    const tableConfig = document.getElementById(`field_${fieldIndex}_text_table_config`);
    
    if (dataSource === 'custom_table' && tableConfig) {
        tableConfig.style.display = 'block';
    } else if (tableConfig) {
        tableConfig.style.display = 'none';
    }
}

// Handle table selection for dropdowns
function handleTableSelection(selectElement) {
    const fieldIndex = selectElement.dataset.fieldIndex;
    const tableName = selectElement.value;
    
    if (tableName) {
        // Load table columns
        fetch(`/api/data-tables/${tableName}/columns`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateColumnSelects(fieldIndex, data.columns);
                    updateTableInfo(fieldIndex, data);
                }
            })
            .catch(error => console.error('Error loading table columns:', error));
    } else {
        // Hide column selects
        const tableColumns = document.getElementById(`field_${fieldIndex}_table_columns`);
        if (tableColumns) {
            tableColumns.style.display = 'none';
        }
    }
}

// Handle text table selection
function handleTextTableChange(select) {
    const fieldIndex = select.dataset.fieldIndex;
    const tableName = select.value;
    
    if (tableName) {
        // Load columns for the selected table
        fetch(`/api/data-tables/${tableName}/columns`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const textColumnSelect = document.querySelector(`select[name="field_${fieldIndex}_text_column"]`);
                    if (textColumnSelect) {
                        textColumnSelect.innerHTML = '<option value="">Select column...</option>';
                        data.columns.forEach(column => {
                            const option = document.createElement('option');
                            option.value = column.name;
                            option.textContent = `${column.display_name} (${column.type})`;
                            textColumnSelect.appendChild(option);
                        });
                    }
                }
            })
            .catch(error => {
                console.error('Error loading table columns:', error);
            });
    }
}

function updateColumnSelects(fieldIndex, columns) {
    const valueSelect = document.querySelector(`select[name="field_${fieldIndex}_value_column"]`);
    const labelSelect = document.querySelector(`select[name="field_${fieldIndex}_label_column"]`);
    const textColumnSelect = document.querySelector(`select[name="field_${fieldIndex}_text_column"]`);
    
    // Clear existing options
    if (valueSelect) {
        valueSelect.innerHTML = '<option value="">Select column...</option>';
    }
    if (labelSelect) {
        labelSelect.innerHTML = '<option value="">Select column...</option>';
    }
    if (textColumnSelect) {
        textColumnSelect.innerHTML = '<option value="">Select column...</option>';
    }
    
    // Add column options
    columns.forEach(column => {
        if (valueSelect) {
            const valueOption = document.createElement('option');
            valueOption.value = column.name;
            valueOption.textContent = `${column.display_name} (${column.type})`;
            valueSelect.appendChild(valueOption);
        }
        
        if (labelSelect) {
            const labelOption = document.createElement('option');
            labelOption.value = column.name;
            labelOption.textContent = `${column.display_name} (${column.type})`;
            labelSelect.appendChild(labelOption);
        }
        
        if (textColumnSelect) {
            const textOption = document.createElement('option');
            textOption.value = column.name;
            textOption.textContent = `${column.display_name} (${column.type})`;
            textColumnSelect.appendChild(textOption);
        }
    });
    
    // Show the column configuration
    const tableColumns = document.getElementById(`field_${fieldIndex}_table_columns`);
    if (tableColumns) {
        tableColumns.style.display = 'block';
    }
}

function updateTableInfo(fieldIndex, tableData) {
    const infoElement = document.getElementById(`field_${fieldIndex}_table_info`);
    if (infoElement) {
        infoElement.textContent = `${tableData.row_count} rows available in ${tableData.display_name}`;
    }
}

function addOption(fieldIndex) {
    const optionsContainer = document.getElementById(`field_${fieldIndex}_options_container`);
    if (!optionsContainer) return;
    
    const optionCount = optionsContainer.children.length;
    
    const optionDiv = document.createElement('div');
    optionDiv.className = 'row mb-2';
    optionDiv.innerHTML = `
        <div class="col-md-4">
            <input type="text" class="form-control form-control-sm" 
                   name="field_${fieldIndex}_option_${optionCount}_value" 
                   placeholder="Option value">
        </div>
        <div class="col-md-6">
            <input type="text" class="form-control form-control-sm" 
                   name="field_${fieldIndex}_option_${optionCount}_label" 
                   placeholder="Option label (displayed to user)">
        </div>
        <div class="col-md-2">
            <button type="button" class="btn btn-sm btn-outline-danger" 
                    data-action="remove-option">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `;
    
    optionsContainer.appendChild(optionDiv);
}

function initializeExistingFields(fields) {
    fields.forEach(function(field, index) {
        if (field.type) {
            setTimeout(function() {
                toggleFieldOptions(index, field.type);
            }, 100);
        }
    });
}

// Initialize data source configurations for existing fields
function initializeExistingDataSources() {
    // Initialize field types first
    document.querySelectorAll('.field-type-select').forEach(select => {
        toggleFieldOptions(parseInt(select.closest('.field-editor').dataset.fieldIndex), select.value);
    });
    
    // Initialize dropdown data sources
    document.querySelectorAll('.data-source-type-select').forEach(select => {
        handleDataSourceTypeChange(select);
    });
    
    // Initialize text field data sources
    document.querySelectorAll('.text-data-source-select').forEach(select => {
        handleTextDataSourceChange(select);
    });
    
    // Initialize table selections
    document.querySelectorAll('.table-select, .text-table-select').forEach(select => {
        if (select.value) {
            if (select.classList.contains('text-table-select')) {
                handleTextTableChange(select);
            } else {
                handleTableSelection(select);
            }
        }
    });
}

// ========== DEPENDENT FIELDS FUNCTIONALITY ==========

// Update field relationship dropdowns (for dependent fields)
function updateFieldRelationshipDropdowns() {
    // Get all current field IDs
    const currentFields = [];
    document.querySelectorAll('input[name*="_id"]').forEach(input => {
        if (input.name.match(/^field_\d+_id$/)) {
            const fieldId = input.value.trim();
            if (fieldId) {
                currentFields.push({
                    id: fieldId,
                    name: input.closest('.field-editor').querySelector('input[name*="_name"]').value || fieldId
                });
            }
        }
    });
    
    // Update all dependent field dropdowns
    document.querySelectorAll('select[name*="_dependent_"][name$="_field_id"]').forEach(select => {
        const currentValue = select.value;
        select.innerHTML = '<option value="">Select field to populate...</option>';
        
        currentFields.forEach(field => {
            const option = document.createElement('option');
            option.value = field.id;
            option.textContent = `${field.name} (${field.id})`;
            if (field.id === currentValue) {
                option.selected = true;
            }
            select.appendChild(option);
        });
    });
    
    // Update all "depends on" dropdowns
    document.querySelectorAll('select[name*="_depends_on"]').forEach(select => {
        const currentValue = select.value;
        select.innerHTML = '<option value="">Select parent field...</option>';
        
        currentFields.forEach(field => {
            const option = document.createElement('option');
            option.value = field.id;
            option.textContent = `${field.name} (${field.id})`;
            if (field.id === currentValue) {
                option.selected = true;
            }
            select.appendChild(option);
        });
    });
}

// Add new dependent field row
function addDependentField(fieldIndex) {
    const container = document.getElementById(`field_${fieldIndex}_dependent_fields_container`);
    if (!container) return;
    
    const existingRows = container.querySelectorAll('.dependent-field-row');
    const depIndex = existingRows.length;
    
    const rowHTML = `
        <div class="row mb-2 dependent-field-row">
            <div class="col-md-4">
                <select class="form-control" name="field_${fieldIndex}_dependent_${depIndex}_field_id">
                    <option value="">Select field to populate...</option>
                </select>
            </div>
            <div class="col-md-4">
                <input type="text" class="form-control" name="field_${fieldIndex}_dependent_${depIndex}_source_column" 
                       placeholder="Source column name">
            </div>
            <div class="col-md-3">
                <div class="form-check">
                    <input type="checkbox" class="form-check-input" name="field_${fieldIndex}_dependent_${depIndex}_auto_populate" checked>
                    <label class="form-check-label">Auto-populate</label>
                </div>
            </div>
            <div class="col-md-1">
                <button type="button" class="btn btn-sm btn-outline-danger remove-dependent-btn">
                    <i class="bi bi-x"></i>
                </button>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', rowHTML);
    updateFieldRelationshipDropdowns();
}

// Remove dependent field row
function removeDependentField(button) {
    const row = button.closest('.dependent-field-row');
    if (row) {
        row.remove();
    }
}

// ========== END DEPENDENT FIELDS FUNCTIONALITY ==========
