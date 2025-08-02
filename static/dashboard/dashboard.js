class DashboardAIIntegration {
    constructor() {
        this.aiQuickBtns = document.querySelectorAll('.ai-quick-btn');
        this.aiInsightsRow = document.getElementById('ai-insights-row');
        this.helpCountEl = document.getElementById('ai-help-count');
        
        this.initializeEventListeners();
        this.loadAIInsights();
        this.updateHelpCount();
    }
    
    initializeEventListeners() {
        // Quick action buttons
        this.aiQuickBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const message = e.target.closest('.ai-quick-btn').dataset.message;
                this.sendQuickMessage(message);
            });
        });
    }
    
    async sendQuickMessage(message) {
        // Open floating chat widget with the message
        if (window.FloatingChatWidget) {
            const widget = new FloatingChatWidget();
            widget.openChat();
            widget.chatInput.value = message;
            await widget.sendMessage();
        } else {
            // Fallback: redirect to full chat page
            window.location.href = `/assistant/?message=${encodeURIComponent(message)}`;
        }
        
        // Update help count
        this.incrementHelpCount();
    }
    
    async loadAIInsights() {
        // Show loading skeletons
        this.showInsightSkeletons();
        
        try {
            // Get personalized insights based on user activity
            const insights = await this.getPersonalizedInsights();
            this.renderInsights(insights);
        } catch (error) {
            console.error('Error loading AI insights:', error);
            this.hideInsightSkeletons();
        }
    }
    
    async getPersonalizedInsights() {
        // This would typically call your backend API
        // For now, return mock data based on user role
        const userRole = '{{ user.profile.role }}';
        
        if (userRole === 'company') {
            return [
                {
                    title: 'Optimize Your Job Posts',
                    description: 'Jobs with detailed requirements get 40% more qualified applications.',
                    action: 'Review My Posts',
                    actionMessage: 'Help me optimize my job postings',
                    icon: 'fas fa-chart-line',
                    color: 'success'
                },
                {
                    title: 'Candidate Response Time',
                    description: 'Respond to applications within 24 hours to improve candidate experience.',
                    action: 'View Applications',
                    actionMessage: 'Show me my pending applications',
                    icon: 'fas fa-clock',
                    color: 'warning'
                }
            ];
        } else {
            return [
                {
                    title: 'Profile Completeness',
                    description: 'Complete profiles get 3x more views from employers.',
                    action: 'Improve Profile',
                    actionMessage: 'How can I improve my profile completeness?',
                    icon: 'fas fa-user-check',
                    color: 'info'
                },
                {
                    title: 'New Job Matches',
                    description: 'Found 5 new jobs that match your skills and preferences.',
                    action: 'View Matches',
                    actionMessage: 'Show me jobs that match my skills',
                    icon: 'fas fa-bullseye',
                    color: 'primary'
                }
            ];
        }
    }
    
    showInsightSkeletons() {
        this.aiInsightsRow.innerHTML = `
            <div class="col-md-6">
                <div class="ai-insight-skeleton"></div>
            </div>
            <div class="col-md-6">
                <div class="ai-insight-skeleton"></div>
            </div>
        `;
    }
    
    renderInsights(insights) {
        this.aiInsightsRow.innerHTML = '';
        
        insights.forEach(insight => {
            const insightCard = document.createElement('div');
            insightCard.className = 'col-md-6';
            insightCard.innerHTML = `
                <div class="ai-insight-card">
                    <h6>
                        <i class="${insight.icon} text-${insight.color} me-2"></i>
                        ${insight.title}
                    </h6>
                    <p>${insight.description}</p>
                    <button class="btn btn-outline-${insight.color} btn-sm ai-insight-btn" 
                            data-message="${insight.actionMessage}">
                        ${insight.action}
                    </button>
                </div>
            `;
            
            this.aiInsightsRow.appendChild(insightCard);
        });
        
        // Add event listeners to new buttons
        document.querySelectorAll('.ai-insight-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const message = e.target.dataset.message;
                this.sendQuickMessage(message);
            });
        });
    }
    
    hideInsightSkeletons() {
        this.aiInsightsRow.innerHTML = '<p class="text-muted">Unable to load insights at this time.</p>';
    }
    
    updateHelpCount() {
        const count = localStorage.getItem('ai_help_count_today') || '0';
        if (this.helpCountEl) {
            this.helpCountEl.textContent = count;
        }
    }
    
    incrementHelpCount() {
        const today = new Date().toDateString();
        const lastDate = localStorage.getItem('ai_help_count_date');
        
        if (lastDate !== today) {
            // Reset count for new day
            localStorage.setItem('ai_help_count_today', '1');
            localStorage.setItem('ai_help_count_date', today);
        } else {
            // Increment count for same day
            const count = parseInt(localStorage.getItem('ai_help_count_today') || '0') + 1;
            localStorage.setItem('ai_help_count_today', count.toString());
        }
        
        this.updateHelpCount();
    }
}

// Initialize dashboard AI integration
document.addEventListener('DOMContentLoaded', () => {
    new DashboardAIIntegration();
});
