// Unlock audio context on first user interaction
document.addEventListener('click', () => {
    const alertSound = document.getElementById('alertSound');
    if (alertSound) {
        alertSound.play().then(() => {
            alertSound.pause();
            alertSound.currentTime = 0;
        }).catch(err => {
            console.log("Audio unlock failed (likely okay):", err);
        });
    }
}, { once: true });

// Initialize socket connection
const socket = io();
socket.on('connect', () => {
    console.log('Socket connected!');
});


// Handle incoming alert events
socket.on('alert', (message) => {
    console.log('Alert received:', message);
    const alertSound = document.getElementById('alertSound');
    if (alertSound) {
        alertSound.play().catch(error => {
            console.error("Playback error:", error);
        });
    }
});

// Start detection
function startDetection() {
    const alertSound = document.getElementById('alertSound');
    if (alertSound) {
        // Try to unlock audio again, if needed
        alertSound.play().then(() => {
            alertSound.pause();
            alertSound.currentTime = 0;
        }).catch(() => {
            // Silent fail, will work after user click
        });
    }

    fetch('/start')
        .then(response => response.json())
        .then(data => {
            const video = document.getElementById('video');
            video.src = "/video_feed?" + new Date().getTime();  // Bust cache
            document.getElementById('video-container').style.display = "block";
        })
        .catch(err => {
            console.error("Start failed:", err);
        });
}

// Stop detection
function stopDetection() {
    fetch('/stop')
        .then(response => response.json())
        .then(data => {
            const video = document.getElementById('video');
            video.src = "";
            document.getElementById('video-container').style.display = "none";
        })
        .catch(err => {
            console.error("Stop failed:", err);
        });
}
