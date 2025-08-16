// JobBoard Chatbot JavaScript Implementation
class JobBoardChatbot {
    constructor() {
        this.sessionId = localStorage.getItem('jobboard_chatbot_session_id');
        this.isOpen = false;
        this.isProcessing = false;
        this.messageQueue = [];
        
        this.initializeElements();
        this.bindEvents();
        this.loadChatHistory();
    }
    
    initializeElements() {
        this.chatButton = document.getElementById('chatToggle');
        this.chatWidget = document.getElementById('chatWidget');
        this.chatClose = document.getElementById('chatClose');
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.chatSend = document.getElementById('chatSend');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.clearChatBtn = document.getElementById('clearChat');
        
        // Check if elements exist
        if (!this.chatButton || !this.chatWidget) {
            console.error('Chatbot elements not found');
            return;
        }
    }
    
    bindEvents() {
        // Main chat controls
        this.chatButton?.addEventListener('click', () => this.toggleChat());
        this.chatClose?.addEventListener('click', () => this.closeChat());
        this.chatSend?.addEventListener('click', () => this.sendMessage());
        this.clearChatBtn?.addEventListener('click', () => this.clearChat());
        
        // Input handling
        this.chatInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Visual feedback for input
        this.chatInput?.addEventListener('input', (e) => {
            const hasText = e.target.value.trim().length > 0;
            this.chatSend?.classList.toggle('active', hasText);
        });
        
        // Escape key to close chat
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeChat();
            }
        });
        
        // Auto-scroll when new messages arrive
        this.setupScrollObserver();
    }
    
    setupScrollObserver() {
        if (!this.chatMessages) return;
        
        // Auto-scroll to bottom when messages are added
        const observer = new MutationObserver(() => {
            this.scrollToBottom();
        });
        
        observer.observe(this.chatMessages, {
            childList: true,
            subtree: true
        });
    }
    
    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }
    
    openChat() {
        if (!this.chatWidget) return;
        
        this.chatWidget.style.display = 'flex';
        this.isOpen = true;
        
        // Focus input after a short delay
        setTimeout(() => {
            this.chatInput?.focus();
        }, 100);
        
        // Update button icon
        if (this.chatButton) {
            this.chatButton.innerHTML = '<i class="fas fa-times"></i>';
            this.chatButton.setAttribute('aria-label', 'Close AI Assistant');
        }
        
        // Mark as opened for analytics (optional)
        this.trackEvent('chatbot_opened');
    }
    
    closeChat() {
        if (!this.chatWidget) return;
        
        this.chatWidget.style.display = 'none';
        this.isOpen = false;
        
        // Update button icon
        if (this.chatButton) {
            this.chatButton.innerHTML = '<i class="fas fa-comments"></i>';
            this.chatButton.setAttribute('aria-label', 'Open AI Assistant');
        }
        
        // Clear any processing state
        this.hideTyping();
        this.isProcessing = false;
        if (this.chatSend) this.chatSend.disabled = false;
        
        this.trackEvent('chatbot_closed');
    }
    
    async sendMessage() {
        const message = this.chatInput?.value.trim();
        if (!message || this.isProcessing) return;
        
        this.isProcessing = true;
        if (this.chatSend) this.chatSend.disabled = true;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        if (this.chatInput) this.chatInput.value = '';
        this.updateSendButton();
        
        // Show typing indicator
        this.showTyping();
        
        try {
            const response = await this.callChatbotAPI(message);
            this.hideTyping();
            
            if (response.error) {
                this.addMessage(response.error, 'bot', 'error');
            } else {
                this.addMessage(response.response, 'bot');
                
                // Save session ID
                if (response.session_id) {
                    this.sessionId = response.session_id;
                    localStorage.setItem('jobboard_chatbot_session_id', this.sessionId);
                }
            }
            
            this.trackEvent('message_sent', { message_length: message.length });
            
        } catch (error) {
            console.error('Chatbot error:', error);
            this.hideTyping();
            this.addMessage(
                'I apologize, but I\'m experiencing technical difficulties. Please try again in a moment.', 
                'bot', 
                'error'
            );
        } finally {
            this.isProcessing = false;
            if (this.chatSend) this.chatSend.disabled = false;
            this.chatInput?.focus();
        }
    }
    
    async callChatbotAPI(message) {
        const csrfToken = this.getCSRFToken();
        
        const response = await fetch('/chatbot/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                message: message,
                session_id: this.sessionId
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    addMessage(content, type, messageClass = '') {
        if (!this.chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type} ${messageClass}`.trim();
        
        // Format message content for bot messages
        if (type === 'bot') {
            content = this.formatBotMessage(content);
        } else {
            content = this.escapeHtml(content);
        }
        
        messageDiv.innerHTML = content;
        
        // Add timestamp as data attribute
        messageDiv.setAttribute('data-timestamp', new Date().toISOString());
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Clean up old messages if too many
        this.cleanupOldMessages();
    }
    
    formatBotMessage(content) {
        // Escape HTML first, then apply formatting
        content = this.escapeHtml(content);
        
        // Convert simple markdown-style formatting
        content = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
        
        // Convert URLs to links
        content = content.replace(
            /(https?:\/\/[^\s<>"']+)/gi,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        return content;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    cleanupOldMessages() {
        const messages = this.chatMessages?.querySelectorAll('.message');
        const maxMessages = 50;
        
        if (messages && messages.length > maxMessages) {
            // Remove oldest messages, but keep the welcome message
            const messagesToRemove = messages.length - maxMessages;
            for (let i = 1; i <= messagesToRemove; i++) {
                if (messages[i] && !messages[i].classList.contains('welcome')) {
                    messages[i].remove();
                }
            }
        }
    }
    
    showTyping() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'block';
            this.scrollToBottom();
        }
    }
    
    hideTyping() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'none';
        }
    }
    
    scrollToBottom() {
        if (this.chatMessages) {
            setTimeout(() => {
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }, 50);
        }
    }
    
    updateSendButton() {
        if (!this.chatSend || !this.chatInput) return;
        
        const hasText = this.chatInput.value.trim().length > 0;
        this.chatSend.classList.toggle('active', hasText);
    }
    
    async loadChatHistory() {
        if (!this.sessionId) return;
        
        try {
            const response = await fetch(
                `/chatbot/api/history/?session_id=${encodeURIComponent(this.sessionId)}`
            );
            
            if (response.ok) {
                const data = await response.json();
                this.renderChatHistory(data.history);
            }
        } catch (error) {
            console.log('Could not load chat history:', error.message);
        }
    }
    
    renderChatHistory(history) {
        if (!history || history.length === 0) return;
        
        // Clear current messages except welcome message
        const welcomeMessage = this.chatMessages?.querySelector('.message.bot');
        if (this.chatMessages) {
            this.chatMessages.innerHTML = '';
            
            // Re-add welcome message if no history
            if (welcomeMessage && history.length === 0) {
                this.chatMessages.appendChild(welcomeMessage);
                return;
            }
        }
        
        // Add history messages
        history.forEach(msg => {
            if (msg.type !== 'system') {
                this.addMessage(msg.content, msg.type);
            }
        });
    }
    
    async clearChat() {
        if (!confirm('Are you sure you want to clear the chat history? This action cannot be undone.')) {
            return;
        }
        
        try {
            // Clear server session
            if (this.sessionId) {
                await fetch('/chatbot/api/clear/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken(),
                    },
                    body: JSON.stringify({
                        session_id: this.sessionId
                    })
                });
            }
            
            // Clear local storage
            localStorage.removeItem('jobboard_chatbot_session_id');
            this.sessionId = null;
            
            // Reset chat messages to welcome message
            this.resetWelcomeMessage();
            
            this.trackEvent('chat_cleared');
            
        } catch (error) {
            console.error('Error clearing chat:', error);
            this.addMessage(
                'Failed to clear chat history. Please try again.',
                'bot',
                'error'
            );
        }
    }
    
    resetWelcomeMessage() {
        if (!this.chatMessages) return;
        
        // Get user context from body data attributes
        const body = document.body;
        const isAuthenticated = body.getAttribute('data-authenticated') === 'true';
        const userRole = body.getAttribute('data-user-role');
        
        let welcomeContent = `
            <strong>👋 Hi there!</strong><br>
            I'm your JobBoard assistant. I can help you with:
            <br><br>
        `;
        
        if (isAuthenticated) {
            if (userRole === 'company') {
                welcomeContent += `
                    • Managing your job postings<br>
                    • Viewing applications<br>
                    • Company profile optimization<br>
                    • Understanding our platform features<br>
                `;
            } else {
                welcomeContent += `
                    • Finding relevant jobs<br>
                    • Application tips and guidance<br>
                    • Profile optimization<br>
                    • Understanding job requirements<br>
                `;
            }
        } else {
            welcomeContent += `
                • Finding and browsing jobs<br>
                • Understanding our platform<br>
                • Registration and getting started<br>
                • General platform questions<br>
            `;
        }
        
        welcomeContent += `
            <br>
            How can I help you today?
        `;
        
        this.chatMessages.innerHTML = `<div class="message bot welcome">${welcomeContent}</div>`;
    }
    
    getCSRFToken() {
        // Try to get CSRF token from cookies first
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        // Fallback: try to get from meta tag
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.getAttribute('content');
        }
        
        // Fallback: try to get from form
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            return csrfInput.value;
        }
        
        console.warn('CSRF token not found');
        return '';
    }
    
    // Analytics/tracking helper
    trackEvent(eventName, data = {}) {
        // You can integrate with Google Analytics, Mixpanel, etc.
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, {
                event_category: 'chatbot',
                ...data
            });
        }
        
        // Log for debugging
        console.log('Chatbot event:', eventName, data);
    }
    
    // Public methods for external integration
    openChatWithMessage(message) {
        this.openChat();
        if (this.chatInput && message) {
            this.chatInput.value = message;
            this.updateSendButton();
        }
    }
    
    addQuickReply(text, callback) {
        // Future feature: add quick reply buttons
        console.log('Quick reply feature not yet implemented');
    }
    
    // Utility method to check if chatbot is available
    isAvailable() {
        return !!(this.chatButton && this.chatWidget && this.chatMessages);
    }
    
    // Method to handle connection errors
    handleConnectionError(error) {
        console.error('Chatbot connection error:', error);
        this.addMessage(
            'I\'m having trouble connecting right now. Please check your internet connection and try again.',
            'bot',
            'error'
        );
    }
    
    // Destroy method for cleanup
    destroy() {
        // Remove event listeners
        this.chatButton?.removeEventListener('click', this.toggleChat);
        this.chatClose?.removeEventListener('click', this.closeChat);
        this.chatSend?.removeEventListener('click', this.sendMessage);
        
        // Clear timers and intervals if any
        // ... cleanup code
        
        console.log('Chatbot destroyed');
    }
}

// Global error handler for chatbot
window.addEventListener('error', function(event) {
    if (event.filename && event.filename.includes('chatbot.js')) {
        console.error('Chatbot JavaScript error:', event.error);
    }
});

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    try {
        window.jobboardChatbot = new JobBoardChatbot();
        
        // Add to window for debugging
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            window.chatbot = window.jobboardChatbot;
            console.log('JobBoard Chatbot initialized (debug mode)');
        }
        
    } catch (error) {
        console.error('Failed to initialize JobBoard Chatbot:', error);
    }
});

// Optional: Add chatbot to page load performance metrics
window.addEventListener('load', function() {
    if (window.jobboardChatbot && window.jobboardChatbot.isAvailable()) {
        console.log('JobBoard Chatbot ready');
    }
});