/**
 * Main JavaScript file for AI Report Writer
 */

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // File upload drag and drop functionality
    initializeFileUpload();

    // Initialize any other components
    initializeComponents();
});

/**
 * Initialize file upload drag and drop functionality
 */
function initializeFileUpload() {
    const fileInput = document.getElementById('document');
    const uploadArea = document.querySelector('.file-upload-area');

    if (fileInput && uploadArea) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        // Handle dropped files
        uploadArea.addEventListener('drop', handleDrop, false);
    }
}

/**
 * Prevent default drag behaviors
 */
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

/**
 * Highlight drop area
 */
function highlight(e) {
    const uploadArea = document.querySelector('.file-upload-area');
    if (uploadArea) {
        uploadArea.classList.add('dragover');
    }
}

/**
 * Unhighlight drop area
 */
function unhighlight(e) {
    const uploadArea = document.querySelector('.file-upload-area');
    if (uploadArea) {
        uploadArea.classList.remove('dragover');
    }
}

/**
 * Handle dropped files
 */
function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    const fileInput = document.getElementById('document');

    if (fileInput && files.length > 0) {
        fileInput.files = files;
        // Trigger change event
        $(fileInput).trigger('change');
    }
}

/**
 * Initialize other components
 */
function initializeComponents() {
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Confirm delete actions
    $('.delete-confirm').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });

    // Initialize any modals
    initializeModals();
}

/**
 * Initialize modals
 */
function initializeModals() {
    // Auto-hide modals after certain actions
    $('.modal').on('hidden.bs.modal', function() {
        // Reset any form data or state
        $(this).find('form').trigger('reset');
    });
}

/**
 * Show loading spinner
 */
function showLoading(message = 'Loading...') {
    const loadingHtml = `
        <div class="loading-overlay">
            <div class="loading-content">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 mb-0">${message}</p>
            </div>
        </div>
    `;
    
    if (!document.querySelector('.loading-overlay')) {
        document.body.insertAdjacentHTML('beforeend', loadingHtml);
    }
}

/**
 * Hide loading spinner
 */
function hideLoading() {
    const loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const notificationHtml = `
        <div class="alert alert-${type} alert-dismissible fade show notification" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Remove existing notifications
    $('.notification').remove();
    
    // Add new notification
    $('main').prepend(notificationHtml);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        $('.notification').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Validate file type
 */
function validateFileType(file) {
    const allowedTypes = ['.pdf', '.docx', '.doc', '.txt'];
    const fileName = file.name.toLowerCase();
    
    return allowedTypes.some(type => fileName.endsWith(type));
}

/**
 * Validate file size
 */
function validateFileSize(file, maxSize = 50 * 1024 * 1024) { // 50MB default
    return file.size <= maxSize;
}

/**
 * Handle file validation
 */
function handleFileValidation(file) {
    if (!validateFileType(file)) {
        showNotification('Invalid file type. Please upload PDF, DOCX, DOC, or TXT files.', 'danger');
        return false;
    }
    
    if (!validateFileSize(file)) {
        showNotification('File size too large. Maximum size is 50MB.', 'danger');
        return false;
    }
    
    return true;
}

// Export functions for global use
window.AIReportWriter = {
    showLoading,
    hideLoading,
    showNotification,
    formatFileSize,
    validateFileType,
    validateFileSize,
    handleFileValidation
}; 