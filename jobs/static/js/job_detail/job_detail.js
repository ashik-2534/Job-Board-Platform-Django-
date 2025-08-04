class JobDetailAIHelper {
    constructor() {
                this.toggleBtn = document.getElementById('toggle-ai-helper');
        this.helperContent = document.getElementById('ai-helper-content');
        this.helperIcon = document.getElementById('ai-helper-icon');
        this.actionBtns = document.querySelectorAll('.ai-action-btn');
        this.miniChat = document.getElementById('ai-mini-chat');
        this.miniChatMessages = document.getElementById('mini-chat-messages');
        this.miniChatInput = document.getElementById('mini-chat-input');
        this.miniChatSend = document.getElementById('mini-chat-send');
        this.analysisContent = document.getElementById('job-analysis-content');
        this.salaryInsightsRow = document.getElementById('salary-insights-row');
        this.salaryInsightsContent = document.getElementById('salary-insights-content');

        this.isExpanded = true;
        this.jobData = this.extractJobData();

        this.initializeEventListeners();
        this.loadJobAnalysis();
    }

initializeEventListeners() {
        this.toggleBtn?.addEventListener('click', () => this.toggleHelper());
        this.actionBtns?.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const button = e.target.closest('.ai-action-btn');
                if (button) {
                    const message = button.dataset.message;
                    this.handleQuickAction(message, button);
                }
            });
        });
        this.miniChatSend?.addEventListener('click', () => this.sendMiniChatMessage());
        this.miniChatInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMiniChatMessage();
        });
    }


    extractJobData() {
        const container = document.getElementById('job-detail-container');
        if (!container) return {};
        return {
            title: container.dataset.title,
            company: container.dataset.company,
            location: container.dataset.location,
            jobType: container.dataset.jobtype,
            description: container.dataset.description,
            requirements: container.dataset.requirements,
            salary: container.dataset.salary || '$75,000 (Est.)',
            postedBy: container.dataset.postedby,
            datePosted: container.dataset.dateposted,
            userRole: container.dataset.userRole,
            isAuthenticated: container.dataset.authenticated === 'true'
        };
    }

    toggleHelper() {
        this.isExpanded = !this.isExpanded;
        if (this.helperContent && this.helperIcon) {
            this.helperContent.classList.toggle('collapsed', !this.isExpanded);
            this.helperIcon.className = this.isExpanded
                ? 'fas fa-chevron-up'
                : 'fas fa-chevron-down';
        }
    }


    async loadJobAnalysis() {
        if (this.analysisContent) {
            this.analysisContent.innerHTML = `
                <div class="text-center my-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading analysis...</span>
                    </div>
                    <p class="text-muted mt-2">Analyzing job details...</p>
                </div>
            `;
        }
        try {
            await this.delay(2000);
            const analysis = await this.generateJobAnalysis();
            this.renderJobAnalysis(analysis);
        } catch (err) {
            console.error(err);
            this.renderAnalysisError();
        }
    }
    async generateJobAnalysis() {
        const role = this.jobData.userRole;
        if (!this.jobData.isAuthenticated) {
            return [{
                title: 'Job Overview',
                content: `This **${this.jobData.title}** position at **${this.jobData.company}** appears to be a **${this.jobData.jobType}** role in **${this.jobData.location}**.`,
                type: 'info'
            }];
        }
        if (role === 'applicant') {
            return [{ title: 'Match Analysis', content: 'Mock: 78% match.', type: 'match' }];
        }
        if (role === 'company') {
            return [{ title: 'Post Performance', content: 'Mock: Good engagement.', type: 'performance' }];
        }
        return [];
    }

    renderJobAnalysis(analysis) {
        if (!this.analysisContent) return;
        this.analysisContent.innerHTML = '';
        analysis.forEach(item => {
            const div = document.createElement('div');
            div.className = 'job-analysis-item';
            div.innerHTML = `<h6><i class="fas fa-${this.getIconForType(item.type)} me-2"></i>${item.title}</h6><p>${item.content}</p>`;
            this.analysisContent.appendChild(div);
        });
        if (this.jobData.salary) this.showSalaryInsights();
    }

    renderAnalysisError() {
        if (this.analysisContent) {
            this.analysisContent.innerHTML = `<div class="alert alert-warning"><i class="fas fa-exclamation-triangle me-2"></i>Unable to load analysis.</div>`;
        }
    }

    getIconForType(type) {
        return { match: 'percentage', performance: 'chart-line', info: 'info-circle' }[type] || 'info-circle';
    }
async handleQuickAction(message, button) {
        let orig = '';
        if (button) {
            orig = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        }
        try {
            if (this.miniChat && this.miniChat.style.display === 'none') this.miniChat.style.display = 'block';
            if (this.miniChatMessages) this.addMiniChatMessage(message, 'user');
            const res = await this.getAIResponse(message);
            if (this.miniChatMessages) this.addMiniChatMessage(res, 'ai');
        } catch {
            this.addMiniChatMessage('Error. Try again.', 'ai');
        } finally {
            if (button) {
                button.disabled = false;
                button.innerHTML = orig;
            }
        }
    }

    async sendMiniChatMessage() {
        if (!this.miniChatInput?.value.trim()) return;
        const msg = this.miniChatInput.value.trim();
        this.miniChatInput.value = '';
        this.addMiniChatMessage(msg, 'user');
        const res = await this.getAIResponse(msg);
        this.addMiniChatMessage(res, 'ai');
    }

    addMiniChatMessage(message, sender) {
        const div = document.createElement('div');
        div.className = `mini-message ${sender}`;
        div.textContent = message;
        this.miniChatMessages?.appendChild(div);
        this.miniChatMessages.scrollTop = this.miniChatMessages.scrollHeight;
    }

    async getAIResponse(msg) {
        await this.delay(1500);
        return `AI Response to "${msg}" (Mock Mode)`;
    }

    showSalaryInsights() {
        if (!this.salaryInsightsRow || !this.salaryInsightsContent) return;
        this.salaryInsightsContent.innerHTML = `
            <div class="text-center">Salary insights for ${this.jobData.location}</div>`;
        this.salaryInsightsRow.style.display = 'block';
    }

    delay(ms) { return new Promise(r => setTimeout(r, ms)); }
}
document.addEventListener('DOMContentLoaded', () => new JobDetailAIHelper());