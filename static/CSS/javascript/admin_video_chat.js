const socket = io();

const endChatButton = document.getElementById('endChat');

if (endChatButton) {
    endChatButton.addEventListener('click', () => {
        // Émet un événement de fin de chat
        socket.emit('end-chat');
        alert('Chat session ended.');
        window.location.href = '/';  // Redirection vers la page d'accueil ou autre
    });
}