// Game result modal functions
let isModalOpen = false;
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

// Main DOMContentLoaded handler
document.addEventListener('DOMContentLoaded', function() {
    // Game result modal handling
    window.onclick = function(event) {
        const modal = document.getElementById('gameResultModal');
        if (event.target == modal) {
            closeModal();
        }
    };

    // How to play modal handling
    const htpModal = document.getElementById('how-to-play-modal');
    const helpButton = document.getElementById('help-button');
    const closeHtpModal = document.querySelector('.close-modal-htp');

     function disableHelpButton() {
        helpButton.style.pointerEvents = 'none';
        helpButton.style.opacity = '0.5';
        helpButton.setAttribute('disabled', 'true');
        isModalOpen = true;
    }

    // Function to enable help button
    function enableHelpButton() {
        helpButton.style.pointerEvents = 'auto';
        helpButton.style.opacity = '1';
        helpButton.removeAttribute('disabled');
        isModalOpen = false;
    }

    if (helpButton) {
        helpButton.addEventListener('click', function(e) {
            if (isModalOpen) return;  // Prevent clicks if modal is already open
            e.preventDefault();
            disableHelpButton();

            const url = this.getAttribute('href') || '/how-to-play/';

            fetch(url)
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.text();
                })
                .then(html => {
                    const contentDiv = document.querySelector('.modal-htp-content .how-to-play-content');
                    if (contentDiv) {
                        contentDiv.innerHTML = html;
                        htpModal.style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    enableHelpButton();
                    window.location.href = url;
                });
        });
    }

    // Close handlers - updated to use the new functions
    function closeHowToPlayModal() {
        htpModal.style.display = 'none';
        enableHelpButton();
    }

    if (closeHtpModal) {
        closeHtpModal.addEventListener('click', closeHowToPlayModal);
    }

    window.addEventListener('click', function(event) {
        if (event.target === htpModal) {
            closeHowToPlayModal();
        }
    });

    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('close-modal-htp-button')) {
            closeHowToPlayModal();
        }
    });
});