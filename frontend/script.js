document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatWindow = document.getElementById('chat-window');
    const typingIndicator = document.getElementById('typing-indicator');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        appendMessage(message, 'user');
        chatInput.value = '';
        chatInput.style.height = 'auto'; // Reset height

        showTypingIndicator();

        try {
            const response = await fetch('https://kp-seo-auto-commenter.onrender.com/api/v1/agent/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ task: message }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            // Handle cases where the backend might send a JSON error instead of a stream
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const errorData = await response.json();
                console.error("Received JSON instead of stream:", errorData);
                const errorMessage = errorData.detail || JSON.stringify(errorData);
                appendMessage(`An error occurred: ${errorMessage}`, 'ai', true);
                hideTypingIndicator();
                return;
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let aiMessageContainer = appendMessage('', 'ai');
            let isFirstChunk = true;

            while (true) {
                const { value, done } = await reader.read();
                if (isFirstChunk) {
                    hideTypingIndicator();
                    isFirstChunk = false;
                }

                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                aiMessageContainer.innerHTML += marked.parse(chunk);
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }

        } catch (error) {
            hideTypingIndicator();
            console.error('Error running agent:', error);
            appendMessage('An error occurred. Please check the console for details.', 'ai', true);
        }
    });

    function appendMessage(content, type, isError = false) {
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('chat-message', `${type}-message`);
        
        if (isError) {
            messageWrapper.style.color = '#d9534f'; // Bootstrap's danger color
        }

        // Use marked.parse to render markdown content for AI messages
        if (type === 'ai') {
            messageWrapper.innerHTML = marked.parse(content);
        } else {
            messageWrapper.textContent = content;
        }

        chatWindow.appendChild(messageWrapper);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return messageWrapper; // Return for streaming updates
    }

    function showTypingIndicator() {
        typingIndicator.classList.remove('hidden');
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function hideTypingIndicator() {
        typingIndicator.classList.add('hidden');
    }

    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = `${chatInput.scrollHeight}px`;
    });
});
