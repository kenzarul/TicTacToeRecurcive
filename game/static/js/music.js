
if (!window.backgroundMusic) {
    window.backgroundMusic = new Howl({
        src: ["/static/music/background_music.mp3"],
        autoplay: true,
        loop: true,
        volume: 0.1,
    });

    window.backgroundMusic.play();

    // Load Howler.js sound for button clicks
const clickSound = new Howl({
    src: ["/static/music/click.mp3"], // Replace with your sound file path
    volume: 0.6,
});

function playClickSound() {
    clickSound.play();
}

// Function to generate a unique game code
function generateCode(length = 6) {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
}
document.addEventListener("DOMContentLoaded", () => {
    // Add click sound to all elements with the "button" class
    document.querySelectorAll(".button").forEach((btn) => {
        btn.addEventListener("click", () => {
            playClickSound(); // Play the click sound
        });
    });
});

function navigateWithSound(event, url) {
    event.preventDefault(); // Prevent default navigation
    playClickSound(); // Play the click sound
    setTimeout(() => {
        window.location.href = url; // Navigate after sound plays
    }, 600); // Adjust the delay to match the sound duration
}

// Add event listeners to buttons
document.querySelectorAll("button").forEach(button => {
    button.addEventListener("click", () => {
        clickSound.play(); // Play click sound
    });
});

// Add code generation functionality to a specific button (e.g., "Generate Code")
document.querySelector("#generate-code-btn").addEventListener("click", () => {
    const gameCode = generateCode(); // Generate a new code
    alert("Your game code: " + gameCode); // Show the generated code
});


}
