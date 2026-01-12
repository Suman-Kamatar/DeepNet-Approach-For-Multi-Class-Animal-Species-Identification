const socket = io();

// UI Elements
const btnLive = document.getElementById('btn-live-mode');
const btnStatic = document.getElementById('btn-static-mode');
const liveControls = document.getElementById('live-controls');
const staticControls = document.getElementById('static-controls');
const streamImg = document.getElementById('stream');
const systemStatus = document.getElementById('system-status');
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const detectBtn = document.getElementById('detect-btn');
const fileNameDisplay = document.getElementById('file-name-display');
const logContainer = document.getElementById('log-container');
const emergencyOverlay = document.getElementById('emergency-alert');
const alertAnimalName = document.getElementById('alert-animal-name');
const safetyScore = document.getElementById('safety-score');
const staticInfo = document.getElementById('static-info');
const spinner = document.getElementById('loading-spinner');

let currentMode = 'live';
let liveActive = false;
let alertTimeout;

socket.on('detection', (data) => {
    if (!liveActive && currentMode === 'live') return;
    addLogEntry(data);
    if (data.type === 'danger') showEmergency(data.name);
});

function switchMode(mode) {
    if (liveActive) {
        alert("Please stop the live camera before switching modes.");
        return;
    }

    currentMode = mode;
    btnLive.classList.toggle('active', mode === 'live');
    btnStatic.classList.toggle('active', mode === 'static');
    liveControls.classList.toggle('hidden', mode === 'static');
    staticControls.classList.toggle('hidden', mode === 'live');

    // Clear display
    streamImg.src = "";
    streamImg.classList.add('placeholder-img');
    staticInfo.classList.add('hidden');
}

function controlCamera(action) {
    if (action === 'start') {
        liveActive = true;
        streamImg.src = "/video_feed?" + new Date().getTime();
        streamImg.classList.remove('placeholder-img');
        systemStatus.innerText = "LIVE DETECTION ACTIVE";
        systemStatus.className = "online";
        startBtn.disabled = true;
        stopBtn.disabled = false;
        btnStatic.disabled = true;
        const startMsg = document.createElement('div');
        startMsg.className = 'log-entry';
        startMsg.innerHTML = `<em>--- Live Session Started at ${new Date().toLocaleTimeString()} ---</em>`;
        logContainer.prepend(startMsg);
    } else {
        liveActive = false;
        streamImg.src = "";
        streamImg.classList.add('placeholder-img');
        systemStatus.innerText = "STANDBY";
        systemStatus.className = "offline";
        startBtn.disabled = false;
        stopBtn.disabled = true;
        btnStatic.disabled = false;
        // Tell server to stop capturing if possible, but keeping it simple for now
        fetch('/stop_camera');
    }
}

function handleFileSelect(input) {
    const file = input.files[0];
    if (file) {
        fileNameDisplay.innerText = file.name;
        detectBtn.disabled = false;

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            streamImg.src = e.target.result;
            streamImg.classList.remove('placeholder-img');
        };
        reader.readAsDataURL(file);
    }
}

async function uploadAndDetect() {
    const fileInput = document.getElementById('static-upload');
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('image', file);

    detectBtn.disabled = true;
    spinner.classList.remove('hidden');
    staticInfo.classList.add('hidden');

    try {
        const response = await fetch('/detect_static', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        streamImg.src = data.image; // Annotated image
        spinner.classList.add('hidden');
        detectBtn.disabled = false;

        if (data.detections.length > 0) {
            staticInfo.classList.remove('hidden');
            const list = data.detections.map(d => `<span class="badge ${d.type}">${d.name.toUpperCase()} (${Math.round(d.conf * 100)}%)</span>`).join(' ');
            staticInfo.innerHTML = `<strong>Results:</strong> ${list}`;
            data.detections.forEach(d => addLogEntry(d));
        } else {
            staticInfo.classList.remove('hidden');
            staticInfo.innerHTML = "No animals or people detected in this image.";
        }
    } catch (err) {
        console.error("Static analysis failed:", err);
        spinner.classList.add('hidden');
        detectBtn.disabled = false;
    }
}

function addLogEntry(data) {
    const emptyLog = logContainer.querySelector('.empty-log');
    if (emptyLog) emptyLog.remove();

    const entry = document.createElement('div');
    entry.className = `log-entry ${data.type}`;
    const time = new Date().toLocaleTimeString();

    entry.innerHTML = `
        <span style="font-size: 10px; opacity: 0.5; display: block">${time}</span>
        <strong>${data.name.toUpperCase()}</strong> detected (${Math.round(data.conf * 100)}%)
    `;

    logContainer.prepend(entry);
    if (logContainer.children.length > 500) logContainer.removeChild(logContainer.lastChild);
}

function showEmergency(animal) {
    alertAnimalName.innerText = animal.toUpperCase();
    emergencyOverlay.classList.remove('hidden');
    safetyScore.innerText = "INTRUDER DETECTED";
    safetyScore.className = "stat-value danger";

    clearTimeout(alertTimeout);
    alertTimeout = setTimeout(() => {
        emergencyOverlay.classList.add('hidden');
        safetyScore.innerText = "SECURE";
        safetyScore.className = "stat-value safe";
    }, 5000);
}
