// Replace with your actual Gemini   key.
// NOTE: For production, NEVER put API keys directly in frontend code!
const API_KEY = 'API_KEY_GOES_HERE';

// Shared system instruction — both chats are identical in behavior/state.
const DEFAULT_SYSTEM_INSTRUCTION = `
    You are an Environmental Compliance Legal Assistant for small businesses. 
    Your goal is to help business owners navigate dense environmental regulations.

    STRICT RULES:
    1. Only answer questions related to environmental laws, wastewater, emissions, waste disposal, and green permits.
    2. Always attempt to cite specific local, state, or federal codes (e.g., Clean Water Act, EPA Title 40).
    3. If you don't know the specific rule for a specific county, provide the most relevant state-level rule and direct them to the local Environmental Protection Department.
    4. Use a professional, helpful tone.
    5. Disclaimer: State that you are an AI, not an attorney, and this is for informational purposes.
`;

class ChatWidget {
    constructor(container, systemInstruction = DEFAULT_SYSTEM_INSTRUCTION) {
        this.container = container;
        this.systemInstruction = systemInstruction;

        // Find the chat window inside this container (id starts with "chat-window")
        this.chatWindow = Array.from(container.querySelectorAll('div')).find(d => d.id && d.id.startsWith('chat-window')) || container.querySelector('.chat-window');
        this.input = container.querySelector('input[type="text"]');
        this.button = container.querySelector('button');

        if (!this.chatWindow || !this.input || !this.button) {
            console.warn('ChatWidget: missing elements in container', container);
            return;
        }

        this.button.addEventListener('click', () => this.send());
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.send();
        });
    }

    appendMessage(sender, text, className) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add(className);
        const msgId = 'msg-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
        msgDiv.id = msgId;
        msgDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
        this.chatWindow.appendChild(msgDiv);
        this.chatWindow.scrollTop = this.chatWindow.scrollHeight;
        return msgId;
    }

    updateMessage(id, sender, text) {
        const msgDiv = document.getElementById(id);
        if (msgDiv) {
            const formattedText = text.replace(/\n/g, '<br>');
            msgDiv.innerHTML = `<strong>${sender}:</strong> ${formattedText}`;
        }
    }

    async send() {
        const userText = this.input.value.trim();
        if (userText === '') return;

        // Display user's message in this chat only
        this.appendMessage('User', userText, 'user-msg');
        this.input.value = '';

        // Loading placeholder
        const loadingId = this.appendMessage('Bot', 'Loading...', 'bot-msg');

        try {
            const body = {
                contents: [{ parts: [{ text: `${this.systemInstruction}\n\nUser Question: ${userText}` }] }]
            };

            const response = await fetch("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent", {
                method: 'POST',
                headers: {
                    'x-goog-api-key': API_KEY,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();
            const botText = data?.candidates?.[0]?.content?.parts?.[0]?.text || 'Sorry, no response from model.';
            this.updateMessage(loadingId, 'Bot', botText);
        } catch (err) {
            console.error('ChatWidget error:', err);
            this.updateMessage(loadingId, 'Bot', 'Sorry, I encountered an error connecting to the server.');
        }
    }
}

// Initialize one ChatWidget per .chatbot-container and expose legacy sendRequest/sendRequest2 names
document.addEventListener('DOMContentLoaded', () => {
    const containers = document.querySelectorAll('.chatbot-container');
    const widgets = [];

    containers.forEach((container, idx) => {
        const widget = new ChatWidget(container, DEFAULT_SYSTEM_INSTRUCTION);
        widgets.push(widget);

        // Expose global functions for existing inline onclick attributes
        if (idx === 0) {
            window.sendRequest = () => widget.send();
        } else if (idx === 1) {
            window.sendRequest2 = () => widget.send();
        }
    });
});



function toggleExpand(element) {
    // 1. (Optional) Close any other open boxes first
    document.querySelectorAll('.timeline-content').forEach(card => {
        if (card !== element) card.classList.remove('active');
    });

    // 2. Toggle the 'active' class on the clicked box
    element.classList.toggle('active');

    // 3. Auto-scroll slightly to make sure the expanded box is in view
    if (element.classList.contains('active')) {
        setTimeout(() => {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
    }
}

function submitContact(event) {
    event.preventDefault();

    const button = document.querySelector(".contact-button");
    button.innerText = "Submitting...";
    button.disabled = true;

    setTimeout(() => {
        button.innerText = "Inquiry Submitted ✓";
        button.style.background = "#2e7d32";
        document.querySelector(".contact-form").reset();
    }, 800);
}