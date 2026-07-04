document.addEventListener('DOMContentLoaded', async () => {
    const profileRaw = localStorage.getItem("verte_user_profile");
    if (!profileRaw) { window.location.href = "index.html"; return; }
    const profile = JSON.parse(profileRaw);
    
    await Promise.all([loadDashboardData(profile), loadRecentScans(profile.username)]);

    const scanTrigger = document.getElementById('scan-trigger');
    const cameraInput = document.getElementById('cameraInput');
    
    scanTrigger.addEventListener('click', () => cameraInput.click());
    cameraInput.addEventListener('change', handleImageUpload);
});

async function loadDashboardData(profile) {
    try {
        document.getElementById('dashboard-username').textContent = profile.username;
        document.getElementById('dashboard-avatar').src = profile.avatar || 'assets/avatars/avatar1.webp';
        
        const response = await fetch(`http://localhost:5000/api/user/${profile.username}`);
        const data = await response.json();
        document.getElementById('dashboard-userxp').textContent = `${data.total_xp || 0} XP`;
    } catch (err) { console.error("Dashboard Load Error:", err); }
}

async function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const trigger = document.getElementById('scan-trigger');
    trigger.textContent = "ANALYZING...";
    trigger.disabled = true;

    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('http://localhost:5000/api/classify', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        alert(`Classification: ${data.label}`);
    } catch (err) {
        alert("Failed to classify item.");
    } finally {
        trigger.textContent = "INITIATE SCAN";
        trigger.disabled = false;
    }
}

async function loadRecentScans(username) {
    const list = document.getElementById('activity-list');
    try {
        const res = await fetch(`http://localhost:5000/api/scans/${username}`);
        const scans = await res.json();
        list.innerHTML = scans.length > 0 ? scans.map(s => `
            <div class="flex justify-between p-2 bg-slate-950 border border-slate-800">
                <span>${s.item_name}</span>
                <span class="text-emerald-400 font-bold">+${s.points_earned} XP</span>
            </div>`).join('') : '<p class="text-slate-500">No scans yet.</p>';
    } catch (err) { console.error(err); }
}