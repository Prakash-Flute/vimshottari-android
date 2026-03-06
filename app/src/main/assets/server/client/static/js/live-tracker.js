// Live Coordinates Auto-Update
let liveUpdateInterval;

function fetchLiveData() {
    const tbody = document.getElementById('liveTableBody');
    const container = document.getElementById('liveTableSection');
    
    if (tbody) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:20px;color:var(--accent-cyan);">Loading planetary data...</td></tr>';
    }
    
    const lat = document.getElementById('inputLat')?.value || 28.6139;
    const lon = document.getElementById('inputLon')?.value || 77.2090;
    const tz = document.getElementById('inputTz')?.value || 5.5;
    
    fetch(`/api/live-planets?lat=${lat}&lon=${lon}&tz=${tz}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                updateLiveTable(data.planets, data.timestamp);
                document.getElementById('lastUpdateTime').textContent = new Date().toLocaleTimeString();
            } else {
                throw new Error(data.error);
            }
        })
        .catch(err => {
            if (tbody) tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#ff4d7d;padding:20px;">⚠️ Error loading data</td></tr>';
        });
}

function updateLiveTable(planets, timestamp) {
    const tbody = document.getElementById('liveTableBody');
    const dateEl = document.getElementById('liveDateTime');
    
    if (dateEl) dateEl.textContent = timestamp || '';
    if (!tbody) return;
    
    tbody.innerHTML = '';
    const planetConfig = {
        'Sun': {icon: '☉', color: '#FFD700'},
        'Moon': {icon: '☽', color: '#C0C0C0'},
        'Mercury': {icon: '☿', color: '#FFA500'},
        'Venus': {icon: '♀', color: '#FF69B4'},
        'Mars': {icon: '♂', color: '#FF4500'},
        'Jupiter': {icon: '♃', color: '#DAA520'},
        'Saturn': {icon: '♄', color: '#F4A460'},
        'Rahu': {icon: '☊', color: '#9932CC'},
        'Ketu': {icon: '☋', color: '#708090'}
    };
    
    Object.entries(planets).forEach(([name, data]) => {
        if (!data) return;
        const config = planetConfig[name] || {icon: '●', color: '#fff'};
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <div class="planet-cell">
                    <span class="planet-icon" style="color: ${config.color}">${config.icon}</span>
                    <span style="color: ${config.color}">${name}</span>
                </div>
            </td>
            <td class="coordinates">${data.longitude || '--'}°</td>
            <td>${data.sign_name || '--'}</td>
            <td style="font-family: 'Orbitron', monospace; color: var(--accent-cyan);">${data.dms || '--'}</td>
            <td style="color: #ffa500;">${data.nakshatra_name || '--'} (${data.pada || '--'})</td>
            <td>${data.is_retro ? '<span class="retro-badge">⚠ RETRO</span>' : '<span style="color: #00ff88;">Direct</span>'}</td>
            <td style="color: rgba(255,255,255,0.4); font-size: 0.85rem;">${data.speed ? data.speed.toFixed(4) : '--'}</td>
        `;
        tbody.appendChild(row);
    });
    
    // Auto refresh every 2 minutes
    if (liveUpdateInterval) clearInterval(liveUpdateInterval);
    liveUpdateInterval = setInterval(fetchLiveData, 120000);
}

function updateClock() {
    const now = new Date();
    const date = now.toLocaleDateString('en-GB');
    const time = now.toLocaleTimeString('en-US', {hour12:false});
    const clockEl = document.getElementById('clock');
    if (clockEl) clockEl.textContent = date + ' ' + time;
}

setInterval(updateClock, 1000);
if (document.getElementById('clock')) updateClock();