// ThreatVision AI Live Dashboard JavaScript

document.addEventListener('DOMContentLoaded', () => {
    initChart();
    startPolling();
});

let chart;

function initChart() {
    const ctx = document.getElementById('threatChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array(20).fill(''),
            datasets: [{
                label: 'Threat Score %',
                data: Array(20).fill(0),
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { display: false }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function startPolling() {
    setInterval(fetchTelemetry, 1000);
    setInterval(fetchHistory, 3000);
}

async function fetchTelemetry() {
    try {
        const res = await fetch('/statistics');
        const data = await res.json();
        
        document.getElementById('fps-display').innerText = `FPS: ${(data.fps || 30.0).toFixed(1)}`;
        document.getElementById('val-cpu').innerText = `${data.system?.cpu_percent || 12}%`;
        document.getElementById('val-ram').innerText = `${data.system?.memory_used_mb || 1.2} MB`;
        document.getElementById('val-detections').innerText = data.active_detections_count || 0;

        const threatScore = Math.round((data.threat_score || 0) * 100);
        const threatLevel = data.threat_level || 'SAFE';

        // Update Gauge Badge
        const badge = document.getElementById('threat-badge');
        badge.innerText = `${threatLevel} (${threatScore}%)`;
        badge.className = `threat-badge ${threatLevel.toLowerCase()}`;

        // Update Chart
        chart.data.datasets[0].data.push(threatScore);
        chart.data.datasets[0].data.shift();
        chart.update('none');
    } catch (e) {
        console.warn('Telemetry polling error', e);
    }
}

async function fetchHistory() {
    try {
        const res = await fetch('/history?limit=10');
        const incidents = await res.json();

        const tbody = document.getElementById('history-rows');
        if (!incidents || incidents.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No incidents recorded yet.</td></tr>';
            return;
        }

        tbody.innerHTML = incidents.map(inc => `
            <tr>
                <td><strong>${inc.incident_id}</strong></td>
                <td>${new Date(inc.timestamp).toLocaleTimeString()}</td>
                <td><span class="threat-badge ${inc.threat_level.toLowerCase()}" style="padding: 2px 8px; font-size: 0.75rem;">${inc.threat_level}</span></td>
                <td>${Math.round(inc.threat_score * 100)}%</td>
                <td>${inc.primary_threat || 'None'}</td>
                <td><a href="/reports/${inc.incident_id}.pdf" target="_blank" style="color:#38bdf8;">PDF Report</a></td>
            </tr>
        `).join('');
    } catch (e) {
        console.warn('History fetch error', e);
    }
}

function exportCSV() {
    window.open('/history/csv', '_blank');
}
