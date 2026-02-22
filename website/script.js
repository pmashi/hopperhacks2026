// Replace with your actual Gemini API key. 
// NOTE: For production, NEVER put API keys directly in frontend code! 
    
const API_KEY = 'AIzaSyAEsaQ5TRudXCortFb8g6Z3WoAvHGz7M-Y'; 

async function sendRequest() {
    const inputField = document.getElementById('user-input');
    const userText = inputField.value.trim();
    const systemInstruction = `
        You are an Environmental Compliance Legal Assistant for small businesses. 
        Your goal is to help business owners navigate dense environmental regulations.
        
        STRICT RULES:
        1. Only answer questions related to environmental laws, wastewater, emissions, waste disposal, and green permits.
        2. Always attempt to cite specific local, state, or federal codes (e.g., Clean Water Act, EPA Title 40).
        3. If you don't know the specific rule for a specific county, provide the most relevant state-level rule and direct them to the local Environmental Protection Department.
        4. Use a professional, helpful tone. 
        5. Disclaimer: State that you are an AI, not an attorney, and this is for informational purposes.
    `;
    // Prevent sending empty messages
    if (userText === '') return;

    // 1. Display the user's message
    appendMessage('User', userText, 'user-msg');
    
    // Clear the input field
    inputField.value = '';

    // 2. Display a temporary "Thinking..." message
    const loadingId = appendMessage('Bot', 'Loading...', 'bot-msg');

    try {
        // 3. Make the fetch request to the Gemini API
        // We are using gemini-2.5-flash as it is the standard for fast, general text tasks
        const response = await fetch("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent", {
            method: 'POST',
            headers: {
                'x-goog-api-key': API_KEY,
                'Content-Type': 'application/json'                
            },
            body: JSON.stringify({
            contents: [{
    parts: [{
        text: `${systemInstruction}\n\nUser Question: ${userText}`
    }]
}]  
        })});

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Extract the text from the API response
        const botText = data.candidates[0].content.parts[0].text;

        // 4. Replace the "Thinking..." message with the actual response
        updateMessage(loadingId, 'Bot', botText);

    } catch (error) {
        console.error('Error fetching from Gemini API:', error);
        updateMessage(loadingId, 'Bot', 'Sorry, I encountered an error connecting to the server.');
    }
}

// Helper function to add a message to the chat window
function appendMessage(sender, text, className) {
    const chatWindow = document.getElementById('chat-window');
    const msgDiv = document.createElement('div');
    
    msgDiv.classList.add(className);
    
    // Generate a unique ID for the message div (useful for updating loading messages)
    const msgId = 'msg-' + Date.now();
    msgDiv.id = msgId;

    msgDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatWindow.appendChild(msgDiv);
    
    // Auto-scroll to the bottom of the chat window
    chatWindow.scrollTop = chatWindow.scrollHeight;

    return msgId;
}

// Helper function to update an existing message
function updateMessage(id, sender, text) {
    const msgDiv = document.getElementById(id);
    if (msgDiv) {
        // Replace newline characters with <br> tags so Gemini's formatting looks correct in HTML
        const formattedText = text.replace(/\n/g, '<br>');
        msgDiv.innerHTML = `<strong>${sender}:</strong> ${formattedText}`;
    }
}

// Allow users to send messages by pressing the "Enter" key
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('user-input').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendRequest();
        }
    });
});

