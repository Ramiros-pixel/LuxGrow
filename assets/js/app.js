/**
 * LuxGrow Dashboard Application
 * Handles Real-time Data, Navigation, and Charting
 */

// Configuration
const CONFIG = {
    UPDATE_INTERVAL: 3000,
    ENDPOINTS: {
        LUX: '/api/realtime/lux',
        DHT: '/api/realtime/dht',
        CONDITION: '/api/realtime/condition',
        SERVO_MODE: '/api/servo/mode',
        SERVO_COMMAND: '/api/servo/command',
        SERVO_STATUS: '/api/servo/status'
    },
    MAX_CHART_POINTS: 20
};

// Global Chart Instance
let mainChart = null;

// UI Elements
const ui = {
    lux: document.getElementById('lux-value'),
    temp: document.getElementById('temperature'),
    humidity: document.getElementById('humidity'),
    lastUpdate: document.getElementById('last-update'),
    conditionDisplay: document.getElementById('condition-display'),
    classIcon: document.getElementById('class-icon'),
    refreshBtn: document.getElementById('btn-refresh'),
    // Servo UI
    servoModeToggle: document.getElementById('servo-mode-toggle'),
    servoModeText: document.getElementById('servo-mode-text'),
    servoAngleDisplay: document.getElementById('servo-angle-display'),
    servoProgressBar: document.getElementById('servo-progress-bar'),
    servoManualControls: document.getElementById('manual-controls'),
    servoAutoMessage: document.getElementById('auto-message'),
    servoRxSlider: document.getElementById('servo-slider'),
    servoBtnSet: document.getElementById('btn-set-angle'),
    servoBtnCmds: document.querySelectorAll('.btn-servo')
};

// Navigation Handling
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.view-section');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();

            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));

            // Add active class to clicked link
            link.classList.add('active');

            // Get target section
            const targetId = link.getAttribute('data-target');

            // Hide all sections
            sections.forEach(s => s.classList.remove('active-view'));

            // Show target section
            document.getElementById(targetId).classList.add('active-view');
        });
    });
}

// Chart Initialization
function initChart() {
    const ctx = document.getElementById('liveChart').getContext('2d');

    mainChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Lux',
                    data: [],
                    borderColor: '#30D158',
                    backgroundColor: 'rgba(48, 209, 88, 0.1)',
                    yAxisID: 'y',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Temperature (°C)',
                    data: [],
                    borderColor: '#FFB340',
                    backgroundColor: 'rgba(255, 179, 64, 0.1)',
                    yAxisID: 'y1',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: {
                    grid: { color: '#333' },
                    ticks: { color: '#aaa' }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: { color: '#333' },
                    ticks: { color: '#30D158' }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: { color: '#FFB340' }
                }
            },
            plugins: {
                legend: { labels: { color: '#fff' } }
            }
        }
    });
}

// Update Chart Logic
function updateChart(timestamp, lux, temp) {
    if (!mainChart) return;

    // Add new data
    mainChart.data.labels.push(timestamp);
    mainChart.data.datasets[0].data.push(lux);
    mainChart.data.datasets[1].data.push(temp);

    // Remove old data if exceeding limit
    if (mainChart.data.labels.length > CONFIG.MAX_CHART_POINTS) {
        mainChart.data.labels.shift();
        mainChart.data.datasets[0].data.shift();
        mainChart.data.datasets[1].data.shift();
    }

    mainChart.update();
}

// Servo Logic
async function fetchServoStatus() {
    try {
        const res = await fetch(CONFIG.ENDPOINTS.SERVO_STATUS);
        const data = await res.json();

        updateServoUI(data);
    } catch (error) {
        console.error("Error fetching servo status:", error);
    }
}

function updateServoUI(data) {
    const mode = data.mode || 'manual';
    const lastCmd = data.last_command || {};
    const angle = lastCmd.angle !== undefined ? lastCmd.angle : 90;

    // Update Mode Display
    const isAuto = mode === 'auto';
    if (ui.servoModeToggle) ui.servoModeToggle.checked = isAuto;
    if (ui.servoModeText) {
        ui.servoModeText.textContent = isAuto ? 'Automatic' : 'Manual';
        ui.servoModeText.style.color = isAuto ? '#30D158' : 'var(--primary-color)';
    }

    // Toggle Visibility of Manual Controls
    if (ui.servoManualControls) {
        if (isAuto) {
            ui.servoManualControls.style.opacity = '0.3';
            ui.servoManualControls.style.pointerEvents = 'none';
            if (ui.servoAutoMessage) ui.servoAutoMessage.style.display = 'block';
        } else {
            ui.servoManualControls.style.opacity = '1';
            ui.servoManualControls.style.pointerEvents = 'all';
            if (ui.servoAutoMessage) ui.servoAutoMessage.style.display = 'none';
        }
    }

    // Update Angle Display
    if (ui.servoAngleDisplay) ui.servoAngleDisplay.textContent = `${angle}°`;
    if (ui.servoProgressBar) ui.servoProgressBar.style.width = `${(angle / 180) * 100}%`;
    if (ui.servoRxSlider) ui.servoRxSlider.value = angle;
}

async function setServoMode(isAuto) {
    const mode = isAuto ? 'auto' : 'manual';
    try {
        await fetch(CONFIG.ENDPOINTS.SERVO_MODE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode })
        });
        fetchServoStatus(); // Refresh UI immediately
    } catch (error) {
        console.error("Error setting servo mode:", error);
    }
}

async function sendServoCommand(command, angle) {
    try {
        const body = {};
        if (command) body.command = command;
        if (angle !== undefined) body.angle = parseInt(angle);

        await fetch(CONFIG.ENDPOINTS.SERVO_COMMAND, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        fetchServoStatus(); // Refresh UI immediately
    } catch (error) {
        console.error("Error sending servo command:", error);
    }
}

// Data Fetching Logic
async function fetchData() {
    try {
        if (ui.refreshBtn) ui.refreshBtn.textContent = 'Updating...';

        // 1. Trigger updates
        await fetch(CONFIG.ENDPOINTS.CONDITION, { method: 'POST', body: '{}', headers: { 'Content-Type': 'application/json' } });

        // 2. Fetch Data
        const [luxRes, dhtRes, condRes] = await Promise.all([
            fetch(CONFIG.ENDPOINTS.LUX),
            fetch(CONFIG.ENDPOINTS.DHT),
            fetch(CONFIG.ENDPOINTS.CONDITION)
        ]);

        // Also fetch servo status
        fetchServoStatus();

        const luxData = await luxRes.json();
        const dhtData = await dhtRes.json();
        const condData = await condRes.json();

        // 3. Update Dashboard UI
        const luxVal = luxData.lux || 0;
        const tempVal = dhtData.temperature || 0;
        const humVal = dhtData.humidity || 0;
        const condition = condData.klasifikasi || 'Unknown';

        // Update Text
        if (ui.lux) ui.lux.textContent = luxVal;
        if (ui.temp) ui.temp.textContent = tempVal;
        if (ui.humidity) ui.humidity.textContent = humVal;

        // Update Timestamp
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        if (ui.lastUpdate) ui.lastUpdate.textContent = `Last update: ${timeString}`;

        // 4. Update Classification UI
        updateClassificationUI(condition);

        // 5. Update Chart
        updateChart(timeString, luxVal, tempVal);

    } catch (error) {
        console.error("Fetch error:", error);
    } finally {
        if (ui.refreshBtn) ui.refreshBtn.textContent = 'Refresh Data';
    }
}

// Helper: Classification UI Update
function updateClassificationUI(condition) {
    if (!ui.conditionDisplay) return;

    ui.conditionDisplay.textContent = condition;
    ui.conditionDisplay.className = 'status-badge'; // Reset

    const lower = condition.toLowerCase();

    if (lower.includes('baik')) {
        ui.conditionDisplay.classList.add('status-good');
        ui.classIcon.textContent = '🌿'; // Healthy Plant
        ui.conditionDisplay.innerHTML = `✅ ${condition}`;
    } else if (lower.includes('rendah') || lower.includes('kurang')) {
        ui.conditionDisplay.classList.add('status-warning');
        ui.classIcon.textContent = '☁️'; // Low Light
        ui.conditionDisplay.innerHTML = `⚠️ ${condition}`;
    } else if (lower.includes('tinggi') || lower.includes('berlebih')) {
        ui.conditionDisplay.classList.add('status-danger');
        ui.classIcon.textContent = '☀️'; // High Light
        ui.conditionDisplay.innerHTML = `🔥 ${condition}`;
    } else {
        ui.conditionDisplay.classList.add('status-warning');
        ui.classIcon.textContent = '🤔';
    }
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initChart();

    // Initial Fetch
    fetchData();

    // Attach Listeners
    if (ui.refreshBtn) ui.refreshBtn.addEventListener('click', fetchData);

    // Servo Listeners
    if (ui.servoModeToggle) {
        ui.servoModeToggle.addEventListener('change', (e) => {
            setServoMode(e.target.checked);
        });
    }

    if (ui.servoBtnSet) {
        ui.servoBtnSet.addEventListener('click', () => {
            const angle = ui.servoRxSlider.value;
            sendServoCommand(null, angle);
        });
    }

    ui.servoBtnCmds.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const cmd = e.target.getAttribute('data-cmd');
            sendServoCommand(cmd);
        });
    });

    // Auto Update Interval
    setInterval(fetchData, CONFIG.UPDATE_INTERVAL);
});
