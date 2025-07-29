/**
 * Enhanced Case Form JavaScript
 * Handles form interactions, field dependencies, validation, and data table lookups
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeEnhancedCaseForm();
});

function initializeEnhancedCaseForm() {
    console.log('Initializing Enhanced Case Form...');
    
    // Load template data
    const templateDataElement = document.getElementById('template-data');
    if (!templateDataElement) {
        console.error('Template data element not found');
        return;
    }
    
    const templateId = templateDataElement.dataset.templateId;
    const dependencies = JSON.parse(templateDataElement.dataset.dependencies || '[]');
    
    // Initialize data table lookups
    initializeDataTableLookups();
    
    // Initialize field dependencies
    if (dependencies.length > 0) {
        initializeFieldDependencies(dependencies);
    }
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize rating fields
    initializeRatingFields();
    
    console.log('Enhanced Case Form initialized successfully');
}

function initializeDataTableLookups() {
    const dataTableFields = document.querySelectorAll('.data-table-lookup');
    
    dataTableFields.forEach(field => {
        const tableId = field.dataset.tableId;
        const searchable = field.dataset.searchable === 'true';
        
        if (tableId) {
            loadDataTableOptions(field, tableId);
        }
        
        if (searchable) {
            // Convert to searchable select (could integrate with libraries like Select2)
            makeFieldSearchable(field);
        }
    });
}

function loadDataTableOptions(selectField, tableId) {
    if (!tableId) return;
    
    selectField.classList.add('loading');
    selectField.disabled = true;
    
    // Note: This would need to be updated to use the correct API endpoint
    // For now, using a placeholder endpoint
    fetch(`/enhanced/api/data-tables/${tableId}/records`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.records) {
                populateSelectOptions(selectField, data.records);
            } else {
                console.error('Failed to load data table options:', data.message);
                showFieldError(selectField, 'Failed to load options');
            }
        })
        .catch(error => {
            console.error('Error loading data table options:', error);
            showFieldError(selectField, 'Error loading options');
        })
        .finally(() => {
            selectField.classList.remove('loading');
            selectField.disabled = false;
        });
}

function populateSelectOptions(selectField, records) {
    // Clear existing options except the first one
    while (selectField.children.length > 1) {
        selectField.removeChild(selectField.lastChild);
    }
    
    records.forEach(record => {
        const option = document.createElement('option');
        option.value = record.id || record.value;
        option.textContent = record.display_name || record.label || record.name;
        selectField.appendChild(option);
    });
}

function makeFieldSearchable(field) {
    // This could be enhanced with libraries like Select2 or Choices.js
    // For now, just add a basic filter functionality
    
    const wrapper = document.createElement('div');
    wrapper.className = 'searchable-select-wrapper';
    
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'form-control searchable-select-input';
    searchInput.placeholder = 'Type to search...';
    
    field.style.display = 'none';
    field.parentNode.insertBefore(wrapper, field);
    wrapper.appendChild(searchInput);
    wrapper.appendChild(field);
    
    let originalOptions = Array.from(field.options);
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        
        // Clear current options
        while (field.children.length > 1) {
            field.removeChild(field.lastChild);
        }
        
        // Add filtered options
        originalOptions.slice(1).forEach(option => {
            if (option.textContent.toLowerCase().includes(searchTerm)) {
                field.appendChild(option.cloneNode(true));
            }
        });
        
        // Show the select temporarily for selection
        if (searchTerm) {
            field.style.display = 'block';
            field.size = Math.min(field.options.length, 8);
        } else {
            field.style.display = 'none';
        }
    });
    
    field.addEventListener('change', function() {
        if (this.value) {
            searchInput.value = this.options[this.selectedIndex].textContent;
            this.style.display = 'none';
        }
    });
}

function initializeFieldDependencies(dependencies) {
    console.log('Initializing field dependencies:', dependencies);
    
    dependencies.forEach(dependency => {
        const triggerField = document.querySelector(`[data-field-id="${dependency.triggerId}"]`);
        const targetField = document.querySelector(`[data-field-id="${dependency.targetId}"]`);
        
        if (triggerField && targetField) {
            // Add event listener to trigger field
            triggerField.addEventListener('change', function() {
                evaluateFieldDependency(dependency, this.value);
            });
            
            // Evaluate initial state
            evaluateFieldDependency(dependency, triggerField.value);
        }
    });
}

function evaluateFieldDependency(dependency, triggerValue) {
    const targetContainer = document.querySelector(`[data-field-id="${dependency.targetId}"]`).closest('.field-container');
    
    if (!targetContainer) return;
    
    let shouldShow = false;
    
    switch (dependency.condition) {
        case 'equals':
            shouldShow = triggerValue === dependency.value;
            break;
        case 'not_equals':
            shouldShow = triggerValue !== dependency.value;
            break;
        case 'contains':
            shouldShow = triggerValue.includes(dependency.value);
            break;
        case 'not_empty':
            shouldShow = triggerValue && triggerValue.trim() !== '';
            break;
        case 'empty':
            shouldShow = !triggerValue || triggerValue.trim() === '';
            break;
        default:
            shouldShow = true;
    }
    
    if (shouldShow) {
        targetContainer.style.display = 'block';
        targetContainer.classList.add('field-visible');
    } else {
        targetContainer.style.display = 'none';
        targetContainer.classList.remove('field-visible');
        
        // Clear the hidden field's value
        const targetField = targetContainer.querySelector('.case-field');
        if (targetField) {
            targetField.value = '';
        }
    }
}

function initializeFormValidation() {
    const form = document.getElementById('caseForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
        }
    });
    
    // Add real-time validation to fields
    const fields = form.querySelectorAll('.case-field');
    fields.forEach(field => {
        field.addEventListener('blur', function() {
            validateField(this);
        });
        
        field.addEventListener('input', function() {
            clearFieldError(this);
        });
    });
}

function validateForm() {
    const form = document.getElementById('caseForm');
    const fields = form.querySelectorAll('.case-field');
    let isValid = true;
    
    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const container = field.closest('.field-container');
    const isRequired = field.hasAttribute('required');
    const fieldType = field.type;
    let isValid = true;
    let errorMessage = '';
    
    // Skip validation for hidden fields
    if (container && container.style.display === 'none') {
        return true;
    }
    
    // Required field validation
    if (isRequired) {
        if (fieldType === 'checkbox' || fieldType === 'radio') {
            const checkedFields = container.querySelectorAll('input[type="' + fieldType + '"]:checked');
            if (checkedFields.length === 0) {
                isValid = false;
                errorMessage = 'This field is required';
            }
        } else if (!field.value || field.value.trim() === '') {
            isValid = false;
            errorMessage = 'This field is required';
        }
    }
    
    // Type-specific validation
    if (field.value) {
        switch (fieldType) {
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(field.value)) {
                    isValid = false;
                    errorMessage = 'Please enter a valid email address';
                }
                break;
            case 'url':
                try {
                    new URL(field.value);
                } catch {
                    isValid = false;
                    errorMessage = 'Please enter a valid URL';
                }
                break;
        }
        
        // Max length validation
        const maxLength = field.getAttribute('maxlength');
        if (maxLength && field.value.length > parseInt(maxLength)) {
            isValid = false;
            errorMessage = `Maximum length is ${maxLength} characters`;
        }
    }
    
    if (isValid) {
        showFieldSuccess(field);
    } else {
        showFieldError(field, errorMessage);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    const container = field.closest('.field-container');
    if (!container) return;
    
    container.classList.add('field-error');
    container.classList.remove('field-success');
    
    // Remove existing error message
    const existingError = container.querySelector('.field-error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error-message text-danger small mt-1';
    errorDiv.textContent = message;
    
    const label = container.querySelector('.form-label');
    if (label) {
        label.insertAdjacentElement('afterend', errorDiv);
    }
}

function showFieldSuccess(field) {
    const container = field.closest('.field-container');
    if (!container) return;
    
    container.classList.add('field-success');
    container.classList.remove('field-error');
    
    // Remove error message
    const existingError = container.querySelector('.field-error-message');
    if (existingError) {
        existingError.remove();
    }
}

function clearFieldError(field) {
    const container = field.closest('.field-container');
    if (!container) return;
    
    container.classList.remove('field-error');
    
    const existingError = container.querySelector('.field-error-message');
    if (existingError) {
        existingError.remove();
    }
}

function initializeRatingFields() {
    const ratingFields = document.querySelectorAll('.rating-field');
    
    ratingFields.forEach(field => {
        const inputs = field.querySelectorAll('input[type="radio"]');
        const labels = field.querySelectorAll('label');
        
        // Add hover effects for star ratings
        labels.forEach((label, index) => {
            label.addEventListener('mouseenter', function() {
                // Highlight all stars up to this one
                for (let i = 0; i <= index; i++) {
                    labels[i].style.color = '#ffc107';
                }
            });
            
            label.addEventListener('mouseleave', function() {
                // Reset to current selection
                const checkedInput = field.querySelector('input:checked');
                labels.forEach((lbl, i) => {
                    if (checkedInput && i <= Array.from(inputs).indexOf(checkedInput)) {
                        lbl.style.color = '#ffc107';
                    } else {
                        lbl.style.color = '#ddd';
                    }
                });
            });
        });
        
        // Update display when selection changes
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                const selectedIndex = Array.from(inputs).indexOf(this);
                labels.forEach((label, index) => {
                    if (index <= selectedIndex) {
                        label.style.color = '#ffc107';
                    } else {
                        label.style.color = '#ddd';
                    }
                });
            });
        });
    });
}

// Utility functions
function showToast(message, type = 'info') {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

// Export functions for external use
window.EnhancedCaseForm = {
    validateForm,
    showToast,
    showFieldError,
    showFieldSuccess,
    clearFieldError
};
