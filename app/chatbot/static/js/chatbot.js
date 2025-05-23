// static/js/chatbot.js
document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.querySelector('.chatbot-container');
    const jwtToken = localStorage.getItem('jwt_token');

    async function sendMessage() {
        const input = document.getElementById('userInput');
        const messagesDiv = document.getElementById('chatMessages');
        
        // Validación
        if (!input.value.trim()) return;

        // Mostrar mensaje del usuario
        messagesDiv.innerHTML += `
            <div class="message user">
                <div class="bubble">${input.value}</div>
            </div>
        `;

        try {
            const response = await fetch('/chatbot/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${jwtToken}`
                },
                body: JSON.stringify({ message: input.value })
            });

            const data = await response.json();
            
            // Mostrar respuesta del bot
            messagesDiv.innerHTML += `
                <div class="message bot">
                    <div class="bubble">${data.reply}</div>
                </div>
            `;

        } catch (error) {
            console.error('Error:', error);
            messagesDiv.innerHTML += `
                <div class="message bot error">
                    <div class="bubble">⚠️ Error de conexión</div>
                </div>
            `;
        }
        
        input.value = '';
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
});
