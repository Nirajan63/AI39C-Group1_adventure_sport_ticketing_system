// app/static/js/chatbot.js
// Global "Chat with us" widget controller. Loaded once from base.html so it
// runs on every page. Keeps conversation history in memory (per page load)
// and resends it with each request so the backend agent has multi-turn
// context without needing server-side session storage for chat history.

(function () {
    const STORAGE_KEY_NONE = null; // intentionally not using localStorage/sessionStorage
    let history = []; // [{role: 'user'|'assistant', content: '...'}]
    let sending = false;

    function $(id) {
        return document.getElementById(id);
    }

    function toggleChatbot() {
        const widget = $('chatbot-widget');
        if (!widget) return;
        widget.classList.toggle('open');
        if (widget.classList.contains('open')) {
            const input = $('chatbot-input');
            if (input) input.focus();
            if (history.length === 0) {
                renderMessage('bot', "Hi! I'm the SportAdventure assistant. Ask me about activities, prices, availability, or your bookings.");
            }
        }
    }

    function renderMessage(role, text, isError) {
        const container = $('chatbot-messages');
        if (!container) return;
        const div = document.createElement('div');
        div.className = 'msg ' + (role === 'user' ? 'user' : 'bot') + (isError ? ' error' : '');
        div.textContent = text;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    function setTyping(isTyping) {
        const typing = $('chatbot-typing');
        if (typing) typing.style.display = isTyping ? 'block' : 'none';
    }

    function setSending(isSending) {
        sending = isSending;
        const btn = $('chatbot-send-btn');
        const input = $('chatbot-input');
        if (btn) btn.disabled = isSending;
        if (input) input.disabled = isSending;
    }

    async function sendChatbotMessage() {
        if (sending) return;
        const input = $('chatbot-input');
        if (!input) return;
        const message = input.value.trim();
        if (!message) return;

        renderMessage('user', message);
        history.push({ role: 'user', content: message });
        input.value = '';

        setSending(true);
        setTyping(true);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message, history: history.slice(-10) })
            });

            const data = await response.json();
            const reply = data.reply || "Sorry, I couldn't generate a response.";
            renderMessage('bot', reply, !response.ok);
            history.push({ role: 'assistant', content: reply });
        } catch (err) {
            console.error('Chatbot error:', err);
            renderMessage('bot', "I'm having trouble connecting right now. Please try again in a moment.", true);
        } finally {
            setTyping(false);
            setSending(false);
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        const headerBtn = $('chatbot-toggle-btn');
        const sendBtn = $('chatbot-send-btn');
        const input = $('chatbot-input');

        if (headerBtn) headerBtn.addEventListener('click', toggleChatbot);
        if (sendBtn) sendBtn.addEventListener('click', sendChatbotMessage);
        if (input) {
            input.addEventListener('keydown', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    sendChatbotMessage();
                }
            });
        }
    });

    // Exposed for any inline handlers / debugging from the console.
    window.toggleChatbot = toggleChatbot;
    window.sendChatbotMessage = sendChatbotMessage;
})();
