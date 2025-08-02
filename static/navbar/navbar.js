// The JavaScript code is functionally correct and requires no changes.
document.addEventListener('DOMContentLoaded', function() {
    const aiNavBtn = document.querySelector('.ai-assistant-nav-btn');
    const aiNotification = document.getElementById('nav-ai-notification');
    
    function checkAINotification() {
        const hasUnreadMessages = localStorage.getItem('ai_has_unread_messages');
        if (hasUnreadMessages === 'true') {
            aiNotification.style.display = 'block';
        }
    }
    
    aiNavBtn.addEventListener('click', function() {
        aiNotification.style.display = 'none';
        localStorage.setItem('ai_has_unread_messages', 'false');
    });
    
    window.addEventListener('storage', function(e) {
        if (e.key === 'ai_has_unread_messages' && e.newValue === 'true') {
            aiNotification.style.display = 'block';
        }
    });
    
    checkAINotification();
});
