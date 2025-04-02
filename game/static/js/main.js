function showResultModal(result) {
    const modal = document.getElementById('gameResultModal');
    const title = document.getElementById('resultTitle');
    const message = document.getElementById('resultMessage');

    if (result === 'X') {
        title.textContent = '🎉 Bravo! 🎉';
        message.textContent = 'Player X Wins the Game!';
    } else if (result === 'O') {
        title.textContent = '🎉 Bravo! 🎉';
        message.textContent = 'Player O Wins the Game!';
    } else {
        title.textContent = 'Game Over';
        message.textContent = 'The game ended in a stalemate!';
    }

    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('gameResultModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('gameResultModal');
    if (event.target == modal) {
        closeModal();
    }
}

// Initialize modal if game is over on page load
document.addEventListener('DOMContentLoaded', function() {
    // This will be called by the template if needed
});