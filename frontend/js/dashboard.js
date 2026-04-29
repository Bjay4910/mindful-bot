// dashboard.js — loads and renders user dashboard data

document.addEventListener('DOMContentLoaded', async () => {
    const session = await getSession();
    if (!session) {
        document.getElementById('auth-modal').classList.remove('hidden');
        window.onAuthSuccess = loadDashboard;
        return;
    }
    await loadDashboard();
});

async function loadDashboard() {
    const user = await getCurrentUser();
    if (!user) return;

    // Load score
    try {
        const data = await apiFetch(`/scores/${user.id}`);
        document.getElementById('total-points').textContent = data.total_points ?? 0;
        document.getElementById('streak-count').textContent = data.streak ?? 0;
        document.getElementById('rank-number').textContent = data.rank ? `#${data.rank}` : '—';
    } catch (err) {
        showToast('Could not load score: ' + err.message, 'error');
    }

    // Load user profile
    try {
        const data = await apiFetch(`/users/${user.id}`);
        document.getElementById('profile-username').textContent = data.user.username;
        document.getElementById('profile-email').textContent = data.user.email;
        const joined = new Date(data.user.created_at);
        document.getElementById('profile-joined').textContent =
            joined.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    } catch (err) {
        // non-critical
    }

    // Load recent sessions with message counts
    await loadRecentSessions(user.id);
}

async function loadRecentSessions(userId) {
    const container = document.getElementById('sessions-list');
    if (!container) return;

    try {
        const { data: sessions, error } = await _supabase
            .from('sessions')
            .select('id, topic, started_at')
            .eq('user_id', userId)
            .order('started_at', { ascending: false })
            .limit(10);

        if (error) throw error;
        if (!sessions || sessions.length === 0) {
            container.innerHTML = '<p class="empty-state">No sessions yet. Start chatting!</p>';
            return;
        }

        container.innerHTML = sessions.map(s => `
            <div class="session-item" data-aos="fade-up">
                <div class="session-info">
                    <span class="session-topic">${escSafe(s.topic || 'General conversation')}</span>
                    <span class="session-date">${formatDate(s.started_at)}</span>
                </div>
                <a href="chat.html?session=${s.id}" class="btn btn-ghost btn-sm">Continue</a>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = '<p class="empty-state">Could not load sessions.</p>';
    }
}

function formatDate(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function escSafe(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}
