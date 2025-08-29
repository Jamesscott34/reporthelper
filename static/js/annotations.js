/**
 * Annotation System JavaScript
 *
 * Provides client-side annotation functionality including text selection,
 * annotation toolbar, real-time collaboration, and WebSocket integration.
 */

class AnnotationSystem {
    constructor(documentId, userId) {
        this.documentId = documentId;
        this.userId = userId;
        this.annotations = new Map();
        this.selectedText = null;
        this.websocket = null;
        this.toolbar = null;
        this.isSelecting = false;

        this.init();
    }

    /**
     * Initialize the annotation system
     */
    init() {
        this.createToolbar();
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadAnnotations();
    }

    /**
     * Create the floating annotation toolbar
     */
    createToolbar() {
        const toolbar = document.createElement('div');
        toolbar.id = 'annotation-toolbar';
        toolbar.className = 'annotation-toolbar';
        toolbar.style.display = 'none';
        toolbar.innerHTML = `
            <div class="annotation-toolbar-content">
                <button class="annotation-btn highlight-btn" data-type="highlight" title="Highlight (H)">
                    <i class="fas fa-highlighter"></i>
                </button>
                <button class="annotation-btn comment-btn" data-type="comment" title="Comment (C)">
                    <i class="fas fa-comment"></i>
                </button>
                <button class="annotation-btn sticky-btn" data-type="sticky_note" title="Sticky Note (S)">
                    <i class="fas fa-sticky-note"></i>
                </button>
                <button class="annotation-btn redact-btn" data-type="redaction" title="Redact (R)">
                    <i class="fas fa-eraser"></i>
                </button>
                <button class="annotation-btn close-btn" title="Close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(toolbar);
        this.toolbar = toolbar;

        // Add toolbar event listeners
        toolbar.addEventListener('click', (e) => {
            const btn = e.target.closest('.annotation-btn');
            if (!btn) return;

            if (btn.classList.contains('close-btn')) {
                this.hideToolbar();
            } else {
                const type = btn.dataset.type;
                this.createAnnotation(type);
            }
        });
    }

    /**
     * Setup event listeners for text selection and keyboard shortcuts
     */
    setupEventListeners() {
        const documentContent = document.querySelector('.document-content, .breakdown-content, .original-text');
        if (!documentContent) return;

        // Text selection events
        documentContent.addEventListener('mouseup', (e) => {
            this.handleTextSelection(e);
        });

        documentContent.addEventListener('touchend', (e) => {
            this.handleTextSelection(e);
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (!this.selectedText) return;

            switch(e.key.toLowerCase()) {
                case 'h':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.createAnnotation('highlight');
                    }
                    break;
                case 'c':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.createAnnotation('comment');
                    }
                    break;
                case 's':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.createAnnotation('sticky_note');
                    }
                    break;
                case 'r':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.createAnnotation('redaction');
                    }
                    break;
                case 'escape':
                    this.hideToolbar();
                    break;
            }
        });

        // Click outside to hide toolbar
        document.addEventListener('click', (e) => {
            if (!this.toolbar.contains(e.target) && !e.target.closest('.annotation')) {
                this.hideToolbar();
            }
        });
    }

    /**
     * Handle text selection events
     */
    handleTextSelection(e) {
        const selection = window.getSelection();

        if (selection.rangeCount === 0 || selection.isCollapsed) {
            this.hideToolbar();
            return;
        }

        const range = selection.getRangeAt(0);
        const selectedText = selection.toString().trim();

        if (selectedText.length === 0) {
            this.hideToolbar();
            return;
        }

        // Calculate character offsets
        const documentContent = document.querySelector('.document-content, .breakdown-content, .original-text');
        const offsets = this.calculateOffsets(range, documentContent);

        if (offsets) {
            this.selectedText = {
                text: selectedText,
                startOffset: offsets.start,
                endOffset: offsets.end,
                range: range.cloneRange()
            };

            this.showToolbar(e.clientX, e.clientY);

            // Broadcast selection to other users
            this.broadcastSelection(this.selectedText);
        }
    }

    /**
     * Calculate character offsets for selected text
     */
    calculateOffsets(range, container) {
        try {
            const preRange = document.createRange();
            preRange.selectNodeContents(container);
            preRange.setEnd(range.startContainer, range.startOffset);

            const start = preRange.toString().length;
            const end = start + range.toString().length;

            return { start, end };
        } catch (error) {
            console.error('Error calculating offsets:', error);
            return null;
        }
    }

    /**
     * Show the annotation toolbar at specified coordinates
     */
    showToolbar(x, y) {
        const toolbar = this.toolbar;
        toolbar.style.display = 'block';
        toolbar.style.left = `${x}px`;
        toolbar.style.top = `${y - 60}px`;

        // Ensure toolbar stays within viewport
        const rect = toolbar.getBoundingClientRect();
        if (rect.right > window.innerWidth) {
            toolbar.style.left = `${window.innerWidth - rect.width - 10}px`;
        }
        if (rect.top < 0) {
            toolbar.style.top = `${y + 20}px`;
        }
    }

    /**
     * Hide the annotation toolbar
     */
    hideToolbar() {
        this.toolbar.style.display = 'none';
        this.selectedText = null;
        window.getSelection().removeAllRanges();
    }

    /**
     * Create a new annotation
     */
    async createAnnotation(type) {
        if (!this.selectedText) return;

        let content = '';
        let color = this.getDefaultColor(type);

        // For comments and sticky notes, prompt for content
        if (type === 'comment' || type === 'sticky_note') {
            content = prompt(`Enter your ${type.replace('_', ' ')}:`);
            if (!content) return;
        }

        // For redactions, confirm action
        if (type === 'redaction') {
            if (!confirm('Are you sure you want to redact this text?')) return;
            color = '#000000';
        }

        const annotationData = {
            annotation_type: type,
            start_offset: this.selectedText.startOffset,
            end_offset: this.selectedText.endOffset,
            content: content,
            color: color
        };

        try {
            const response = await this.apiRequest(`/api/documents/${this.documentId}/annotations/`, {
                method: 'POST',
                body: JSON.stringify(annotationData)
            });

            if (response.ok) {
                const annotation = await response.json();
                this.addAnnotationToDOM(annotation);
                this.annotations.set(annotation.id, annotation);
                this.hideToolbar();

                // Show success message
                this.showNotification(`${type.replace('_', ' ').charAt(0).toUpperCase() + type.replace('_', ' ').slice(1)} annotation created`, 'success');
            } else {
                throw new Error(`Failed to create annotation: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error creating annotation:', error);
            this.showNotification('Failed to create annotation', 'error');
        }
    }

    /**
     * Get default color for annotation type
     */
    getDefaultColor(type) {
        const colors = {
            highlight: '#ffff00',
            comment: '#87ceeb',
            sticky_note: '#ffd700',
            redaction: '#000000'
        };
        return colors[type] || '#ffff00';
    }

    /**
     * Add annotation overlay to DOM
     */
    addAnnotationToDOM(annotation) {
        const documentContent = document.querySelector('.document-content, .breakdown-content, .original-text');
        if (!documentContent) return;

        // Create annotation overlay
        const overlay = document.createElement('span');
        overlay.className = `annotation annotation-${annotation.annotation_type}`;
        overlay.dataset.annotationId = annotation.id;
        overlay.style.backgroundColor = annotation.color;
        overlay.title = `${annotation.annotation_type} by ${annotation.user.username}`;

        if (annotation.annotation_type === 'redaction') {
            overlay.style.color = 'transparent';
            overlay.style.backgroundColor = '#000000';
        }

        // Add click handler for viewing/editing
        overlay.addEventListener('click', (e) => {
            e.stopPropagation();
            this.showAnnotationDetails(annotation);
        });

        // Find and wrap the text
        this.wrapTextWithAnnotation(documentContent, annotation, overlay);
    }

    /**
     * Wrap text with annotation overlay
     */
    wrapTextWithAnnotation(container, annotation, overlay) {
        const walker = document.createTreeWalker(
            container,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        let currentOffset = 0;
        let node;

        while (node = walker.nextNode()) {
            const nodeLength = node.textContent.length;
            const nodeStart = currentOffset;
            const nodeEnd = currentOffset + nodeLength;

            // Check if annotation overlaps with this text node
            if (annotation.start_offset < nodeEnd && annotation.end_offset > nodeStart) {
                const overlapStart = Math.max(annotation.start_offset - nodeStart, 0);
                const overlapEnd = Math.min(annotation.end_offset - nodeStart, nodeLength);

                if (overlapStart < overlapEnd) {
                    // Split text node and wrap the overlapping part
                    const beforeText = node.textContent.substring(0, overlapStart);
                    const overlappingText = node.textContent.substring(overlapStart, overlapEnd);
                    const afterText = node.textContent.substring(overlapEnd);

                    const parent = node.parentNode;

                    // Replace the text node with the split parts
                    if (beforeText) {
                        parent.insertBefore(document.createTextNode(beforeText), node);
                    }

                    const annotationSpan = overlay.cloneNode(true);
                    annotationSpan.textContent = overlappingText;
                    parent.insertBefore(annotationSpan, node);

                    if (afterText) {
                        parent.insertBefore(document.createTextNode(afterText), node);
                    }

                    parent.removeChild(node);
                    break;
                }
            }

            currentOffset += nodeLength;
        }
    }

    /**
     * Show annotation details in a popup
     */
    showAnnotationDetails(annotation) {
        const popup = document.createElement('div');
        popup.className = 'annotation-popup';
        popup.innerHTML = `
            <div class="annotation-popup-content">
                <div class="annotation-popup-header">
                    <span class="annotation-type">${annotation.annotation_type.replace('_', ' ')}</span>
                    <span class="annotation-author">by ${annotation.user.username}</span>
                    <button class="annotation-popup-close">&times;</button>
                </div>
                <div class="annotation-popup-body">
                    ${annotation.content ? `<p class="annotation-content">${annotation.content}</p>` : ''}
                    <p class="annotation-text"><strong>Text:</strong> "${annotation.text_content}"</p>
                    <p class="annotation-date">${new Date(annotation.created_at).toLocaleString()}</p>
                </div>
                <div class="annotation-popup-actions">
                    <button class="btn btn-sm btn-primary edit-annotation" data-id="${annotation.id}">Edit</button>
                    <button class="btn btn-sm btn-danger delete-annotation" data-id="${annotation.id}">Delete</button>
                </div>
            </div>
        `;

        document.body.appendChild(popup);

        // Position popup
        const rect = event.target.getBoundingClientRect();
        popup.style.left = `${rect.left}px`;
        popup.style.top = `${rect.bottom + 5}px`;

        // Event listeners
        popup.querySelector('.annotation-popup-close').addEventListener('click', () => {
            document.body.removeChild(popup);
        });

        popup.querySelector('.edit-annotation').addEventListener('click', () => {
            this.editAnnotation(annotation.id);
            document.body.removeChild(popup);
        });

        popup.querySelector('.delete-annotation').addEventListener('click', () => {
            this.deleteAnnotation(annotation.id);
            document.body.removeChild(popup);
        });

        // Close on outside click
        setTimeout(() => {
            document.addEventListener('click', function closePopup(e) {
                if (!popup.contains(e.target)) {
                    document.body.removeChild(popup);
                    document.removeEventListener('click', closePopup);
                }
            });
        }, 100);
    }

    /**
     * Edit an existing annotation
     */
    async editAnnotation(annotationId) {
        const annotation = this.annotations.get(annotationId);
        if (!annotation) return;

        let newContent = annotation.content;

        if (annotation.annotation_type === 'comment' || annotation.annotation_type === 'sticky_note') {
            newContent = prompt(`Edit your ${annotation.annotation_type.replace('_', ' ')}:`, annotation.content);
            if (newContent === null) return;
        }

        try {
            const response = await this.apiRequest(`/api/documents/${this.documentId}/annotations/${annotationId}/`, {
                method: 'PATCH',
                body: JSON.stringify({ content: newContent })
            });

            if (response.ok) {
                const updatedAnnotation = await response.json();
                this.annotations.set(annotationId, updatedAnnotation);
                this.showNotification('Annotation updated', 'success');
            } else {
                throw new Error(`Failed to update annotation: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error updating annotation:', error);
            this.showNotification('Failed to update annotation', 'error');
        }
    }

    /**
     * Delete an annotation
     */
    async deleteAnnotation(annotationId) {
        if (!confirm('Are you sure you want to delete this annotation?')) return;

        try {
            const response = await this.apiRequest(`/api/documents/${this.documentId}/annotations/${annotationId}/`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.removeAnnotationFromDOM(annotationId);
                this.annotations.delete(annotationId);
                this.showNotification('Annotation deleted', 'success');
            } else {
                throw new Error(`Failed to delete annotation: ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error deleting annotation:', error);
            this.showNotification('Failed to delete annotation', 'error');
        }
    }

    /**
     * Remove annotation from DOM
     */
    removeAnnotationFromDOM(annotationId) {
        const elements = document.querySelectorAll(`[data-annotation-id="${annotationId}"]`);
        elements.forEach(element => {
            const parent = element.parentNode;
            parent.replaceChild(document.createTextNode(element.textContent), element);
            parent.normalize(); // Merge adjacent text nodes
        });
    }

    /**
     * Load existing annotations from server
     */
    async loadAnnotations() {
        try {
            const response = await this.apiRequest(`/api/documents/${this.documentId}/annotations/`);
            if (response.ok) {
                const data = await response.json();
                data.results.forEach(annotation => {
                    this.annotations.set(annotation.id, annotation);
                    this.addAnnotationToDOM(annotation);
                });
            }
        } catch (error) {
            console.error('Error loading annotations:', error);
        }
    }

    /**
     * Connect to WebSocket for real-time updates
     */
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/documents/${this.documentId}/`;

        this.websocket = new WebSocket(wsUrl);

        this.websocket.onopen = () => {
            console.log('WebSocket connected');
        };

        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.connectWebSocket(), 3000);
        };

        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    /**
     * Handle incoming WebSocket messages
     */
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'annotation_event':
                this.handleAnnotationEvent(data);
                break;
            case 'user_joined':
                this.showNotification(`${data.username} joined the document`, 'info');
                break;
            case 'user_left':
                this.showNotification(`${data.username} left the document`, 'info');
                break;
            case 'presence_update':
                this.handlePresenceUpdate(data);
                break;
        }
    }

    /**
     * Handle annotation events from WebSocket
     */
    handleAnnotationEvent(data) {
        const { action, annotation } = data;

        switch (action) {
            case 'created':
                if (annotation.user.id !== this.userId) {
                    this.annotations.set(annotation.id, annotation);
                    this.addAnnotationToDOM(annotation);
                    this.showNotification(`New ${annotation.annotation_type} by ${annotation.user.username}`, 'info');
                }
                break;
            case 'updated':
                if (annotation.user.id !== this.userId) {
                    this.annotations.set(annotation.id, annotation);
                    // Remove old and add updated
                    this.removeAnnotationFromDOM(annotation.id);
                    this.addAnnotationToDOM(annotation);
                }
                break;
            case 'deleted':
                if (annotation.user && annotation.user.id !== this.userId) {
                    this.removeAnnotationFromDOM(annotation.id);
                    this.annotations.delete(annotation.id);
                }
                break;
        }
    }

    /**
     * Handle presence updates from other users
     */
    handlePresenceUpdate(data) {
        // Show cursor positions, selections, etc. from other users
        // This is a placeholder for advanced collaboration features
        console.log('Presence update:', data);
    }

    /**
     * Broadcast text selection to other users
     */
    broadcastSelection(selection) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'presence_update',
                activity: 'selecting',
                selected_text: {
                    start_offset: selection.startOffset,
                    end_offset: selection.endOffset,
                    text: selection.text
                }
            }));
        }
    }

    /**
     * Make authenticated API requests
     */
    async apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            credentials: 'same-origin'
        };

        return fetch(url, { ...defaultOptions, ...options });
    }

    /**
     * Get CSRF token from DOM
     */
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    /**
     * Show notification to user
     */
    showNotification(message, type = 'info') {
        // Use existing notification system or create simple toast
        if (window.AIReportWriter && window.AIReportWriter.showNotification) {
            window.AIReportWriter.showNotification(message, type);
        } else {
            // Simple fallback
            const toast = document.createElement('div');
            toast.className = `alert alert-${type} annotation-toast`;
            toast.textContent = message;
            toast.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                min-width: 250px;
                padding: 10px 15px;
                border-radius: 4px;
            `;

            document.body.appendChild(toast);

            setTimeout(() => {
                if (toast.parentNode) {
                    document.body.removeChild(toast);
                }
            }, 3000);
        }
    }
}

// Initialize annotation system when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a document page with annotation support
    const documentId = document.body.dataset.documentId;
    const userId = document.body.dataset.userId;

    if (documentId && userId) {
        window.annotationSystem = new AnnotationSystem(parseInt(documentId), parseInt(userId));
    }
});

// Export for use in other scripts
window.AnnotationSystem = AnnotationSystem;
