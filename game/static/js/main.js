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

    // Modal elements
    const htpModal = document.getElementById('how-to-play-modal');
    const helpButton = document.getElementById('help-button');
    const closeHtpModal = htpModal?.querySelector('.close-modal-htp');
    const profileButton = document.getElementById('profile-button');
    const profileModal = document.getElementById('profile-modal');
    const closeProfileModal = profileModal?.querySelector('.close-modal-htp');
    const loginForm = profileModal?.querySelector('form');

    // Function to disable help button
    function disableHelpButton() {
        if (helpButton) {
            helpButton.style.pointerEvents = 'none';
            helpButton.style.opacity = '0.5';
            helpButton.setAttribute('disabled', 'true');
            isModalOpen = true;
        }
    }

    // Function to enable help button
    function enableHelpButton() {
        if (helpButton) {
            helpButton.style.pointerEvents = 'auto';
            helpButton.style.opacity = '1';
            helpButton.removeAttribute('disabled');
            isModalOpen = false;
        }
    }

    // How to play modal handling
    if (helpButton) {
        helpButton.addEventListener('click', function(e) {
            if (isModalOpen) return;
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

    // Profile modal handling
    if (profileButton) {
        profileButton.addEventListener('click', function(e) {
            e.preventDefault();
            // Check if user is authenticated using a data attribute set in base.html
            if (profileButton.dataset.auth === "true") {
                window.location.href = profileButton.dataset.profileUrl;
            } else {
                profileModal.style.display = 'block';
            }
        });
    }

    // Close modal functions
    function closeHowToPlayModal() {
        htpModal.style.display = 'none';
        enableHelpButton();
    }

    function closeProfileModalFunc() {
        profileModal.style.display = 'none';
    }

    // Close button event listeners
    if (closeHtpModal) {
        closeHtpModal.addEventListener('click', closeHowToPlayModal);
    }

    if (closeProfileModal) {
        closeProfileModal.addEventListener('click', closeProfileModalFunc);
    }

    // Handle login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);

            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                }
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
                return response.json();
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }

    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === htpModal) {
            closeHowToPlayModal();
        }
        if (event.target === profileModal) {
            closeProfileModalFunc();
        }
    });

    // Handle close button inside the how-to-play modal content
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('close-modal-htp-button')) {
            closeHowToPlayModal();
        }
    });
});