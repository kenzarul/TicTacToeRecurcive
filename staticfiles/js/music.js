
if (!window.backgroundMusic) {
    window.backgroundMusic = new Howl({
        src: ["/static/music/background_music.mp3"],
        autoplay: true,
        loop: true,
        volume: 0.1,
    });

    window.backgroundMusic.play();


const clickSound = new Howl({
    src: ["/static/music/click.mp3"],
    volume: 0.6,
});

function playClickSound() {
    clickSound.play();
}


function generateCode(length = 6) {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
}
document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".button").forEach((btn) => {
        btn.addEventListener("click", () => {
            playClickSound();
        });
    });
});

function navigateWithSound(event, url) {
    event.preventDefault();
    playClickSound();
    setTimeout(() => {
        window.location.href = url;
    }, 600);
}


document.querySelectorAll("button").forEach(button => {
    button.addEventListener("click", () => {
        clickSound.play();
    });
});


document.querySelector("#generate-code-btn").addEventListener("click", () => {
    const gameCode = generateCode();
    alert("Your game code: " + gameCode);
});


}
