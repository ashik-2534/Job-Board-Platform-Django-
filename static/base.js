
    class GlobalAIAssistant {
        constructor() {
            this.currentPage = this.getCurrentPageType();
            this.userRole = '{{ user.profile.role|default:"visitor"|escapejs }}';
            this.isAuthenticated = {{ user.is_authenticated|yesno:"true,false" }};
            
            this.initializeGlobalFeatures();
            this.checkForWelcomeMessage();
        }
        
        getCurrentPageType() {
            const path = window.location.pathname;
            if (path.includes('/jobs/')) return 'job_detail';
            if (path.includes('/dashboard/')) return 'dashboard';
            if (path.includes('/profile/')) return 'profile';
            if (path.includes('/apply/')) return 'application';
            if (path === '/') return 'home';
            return 'other';
        }
        
        initializeGlobalFeatures() {
            // Right-click context menu for AI help
            document.addEventListener('contextmenu', (e) => {
                // Only show on specific elements or areas
                if (e.target.closest('.job-card, .profile-section, .form-group')) {
                    e.preventDefault();
                    this.showContextMenu(e.pageX, e.pageY);
                }
            });
            
            // Close context menu on click elsewhere
            document.addEventListener('click', () => {
                this.hideContextMenu();
            });
            
            // Keyboard shortcuts
            document.addEventListener('keydown', (e) => {
                // Alt + A to open AI assistant
                if (e.altKey && e.key === 'a') {
                    e.preventDefault();
                    this.openAIChat();
                }
                
                // Esc to close AI context menu
                if (e.key === 'Escape') {
                    this.hideContextMenu();
                }
            });
            
            // Track user activity for smart suggestions
            this.trackUserActivity();
        }
        
        showContextMenu(x, y) {
            const contextMenu = document.getElementById('ai-context-menu');
            contextMenu.style.left = x + 'px';
            contextMenu.style.top = y + 'px';
            contextMenu.classList.add('show');
        }
        
        hideContextMenu() {
            const contextMenu = document.getElementById('ai-context-menu');
            contextMenu.classList.remove('show');
        }
        
        checkForWelcomeMessage() {
            // Show welcome message for new users
            if (this.isAuthenticated && !localStorage.getItem('ai_welcome_shown')) {
                setTimeout(() => {
                    this.showGlobalNotification(
                        `Welcome! I'm your AI assistant. I can help you with ${this.getWelcomeMessage()}`,
                        5000
                    );
                    localStorage.setItem('ai_welcome_shown', 'true');
                }, 2000);
            }
        }
        
        getWelcomeMessage() {
            if (this.userRole === 'applicant') {
                return 'finding jobs, improving your profile, and application tips.';
            } else if (this.userRole === 'company') {
                return 'posting better jobs, finding candidates, and hiring advice.';
            } else {
                return 'navigating the platform and understanding how it works.';
            }
        }
        
        showGlobalNotification(message, duration = 3000) {
            const notification = document.getElementById('ai-global-notification');
            const textElement = document.getElementById('ai-notification-text');
            
            textElement.textContent = message;
            notification.classList.add('show');
            
            if (duration > 0) {
                setTimeout(() => {
                    this.hideAINotification();
                }, duration);
            }
        }
        
        hideAINotification() {
            const notification = document.getElementById('ai-global-notification');
            notification.classList.remove('show');
        }
        
        openAIChat() {
            // Try to open floating widget first
            const chatToggleBtn = document.getElementById('chat-toggle-btn');
            if (chatToggleBtn) {
                chatToggleBtn.click();
            } else {
                // Fallback to full chat page
                window.location.href = '/assistant/';
            }
        }
        
        getPageHelp() {
            const helpMessages = {
                'home': 'This is the homepage where you can browse featured jobs and get started.',
                'job_detail': 'This page shows detailed information about a specific job. Use the AI helper below to get personalized insights.',
                'dashboard': 'Your dashboard shows your activity and quick actions. The AI assistant can help with personalized recommendations.',
                'profile': 'Your profile page is where employers or job seekers can learn about you. The AI can suggest improvements.',
                'application': 'This is where you apply for jobs. The AI can help you write better cover letters and highlight relevant skills.'
            };
            
            const message = helpMessages[this.currentPage] || 'I can help you navigate this page and answer questions about the platform.';
            this.showGlobalNotification(message, 4000);
            this.hideContextMenu();
        }
        
        getQuickTips() {
            const tips = {
                'applicant': [
                    'Complete your profile to get better job matches.',
                    'Use keywords from job descriptions in your applications.',
                    'Apply within 24 hours of a job posting for better visibility.'
                ],
                'company': [
                    'Add salary ranges to get 40% more applications.',
                    'Respond to applications quickly to improve candidate experience.',
                    'Use specific job titles to attract qualified candidates.'
                ],
                'visitor': [
                    'Create an account to get personalized job recommendations.',
                    'Use the search filters to find jobs that match your preferences.',
                    'Check back regularly as new jobs are posted daily.'
                ]
            };
            
            const userTips = tips[this.userRole] || tips['visitor'];
            const randomTip = userTips[Math.floor(Math.random() * userTips.length)];
            
            this.showGlobalNotification(`💡 Tip: ${randomTip}`, 5000);
            this.hideContextMenu();
        }
        
        provideFeedback() {
            // Open a simple feedback modal or redirect to feedback form
            const feedback = prompt('How can we improve the AI assistant? Your feedback helps us serve you better:');
            
            if (feedback && feedback.trim()) {
                // Send feedback to backend
                fetch('/assistant/api/feedback/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        feedback_text: feedback,
                        page_type: this.currentPage,
                        user_role: this.userRole
                    })
                }).then(() => {
                    this.showGlobalNotification('Thank you for your feedback! 🙏', 3000);
                }).catch(() => {
                    this.showGlobalNotification('Feedback saved locally. Thank you! 📝', 3000);
                });
            }
            
            this.hideContextMenu();
        }
        
        trackUserActivity() {
            // Track page views for better AI suggestions
            const pageViews = JSON.parse(localStorage.getItem('ai_page_views') || '{}');
            pageViews[this.currentPage] = (pageViews[this.currentPage] || 0) + 1;
            localStorage.setItem('ai_page_views', JSON.stringify(pageViews));
            
            // Track time spent on page
            const startTime = Date.now();
            window.addEventListener('beforeunload', () => {
                const timeSpent = Date.now() - startTime;
                const pageTimes = JSON.parse(localStorage.getItem('ai_page_times') || '{}');
                pageTimes[this.currentPage] = (pageTimes[this.currentPage] || 0) + timeSpent;
                localStorage.setItem('ai_page_times', JSON.stringify(pageTimes));
            });
        }
    }
    
    // Global functions (called from other scripts)
    function hideAINotification() {
        if (window.globalAI) {
            window.globalAI.hideAINotification();
        }
    }
    
    function openAIChat() {
        if (window.globalAI) {
            window.globalAI.openAIChat();
        }
    }
    
    function getPageHelp() {
        if (window.globalAI) {
            window.globalAI.getPageHelp();
        }
    }
    
    function getQuickTips() {
        if (window.globalAI) {
            window.globalAI.getQuickTips();
        }
    }
    
    function provideFeedback() {
        if (window.globalAI) {
            window.globalAI.provideFeedback();
        }
    }
    
    // Initialize global AI assistant
    document.addEventListener('DOMContentLoaded', () => {
        window.globalAI = new GlobalAIAssistant();
        
        // Add AI keyboard shortcuts help
        document.addEventListener('keydown', (e) => {
            if (e.altKey && e.key === 'h') {
                e.preventDefault();
                alert('AI Assistant Shortcuts:\nAlt + A: Open AI Chat\nAlt + H: Show this help\nRight-click on job cards/forms: Context menu');
            }
        });
    });