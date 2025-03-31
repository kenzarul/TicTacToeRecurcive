
// Show modal when game ends
function checkGameResult() {
    const gameOver = "{{ game_over }}";
    const modal = document.getElementById('gameResultModal');
    const message = document.getElementById('resultMessage');

    if (gameOver === 'X') {
        message.textContent = 'Bravo! X Wins!';
        modal.style.display = 'block';
    } else if (gameOver === 'O') {
        message.textContent = 'Bravo! O Wins!';
        modal.style.display = 'block';
    } else if (gameOver === ' ') {
        message.textContent = 'Game Ended in Stalemate!';
        modal.style.display = 'block';
    }
}

function closeModal() {
    document.getElementById('gameResultModal').style.display = 'none';
}

// Check on page load
window.onload = checkGameResult;

// Also check after moves (if using AJAX)
// You might need to call checkGameResult() after each move if not refreshing the page
