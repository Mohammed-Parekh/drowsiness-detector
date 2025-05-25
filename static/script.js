const socket = io(); // Connect to the server via Socket.IO

// Preload alert sound
const alertAudio = new Audio('/static/alert.wav');

socket.on('connect', () => {
    console.log('Connected to server for alert notifications');
});

// Listen for 'alert' events from backend
socket.on('alert', (message) => {
    console.log('Alert received:', message);
    alertAudio.play().catch((err) => {
        console.error('Failed to play sound:', err);
    });
});




function startDetection() {
    fetch('/start')
        .then(response => response.json())
        .then(data => {
            const video = document.getElementById('video');
            video.src = "/video_feed?" + new Date().getTime();  // Avoid caching
            document.getElementById('video-container').style.display = "block";
        })
        .catch(err => {
            console.error("Start failed:", err);
        });
}

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
