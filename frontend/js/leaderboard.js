// leaderboard.js — loads and renders leaderboard data

document.addEventListener('DOMContentLoaded', async () => {
    await loadLeaderboard();
    await highlightCurrentUser();
});

async function loadLeaderboard() {
    const table = document.getElementById('leaderboard-body');
    if (!table) return;

    table.innerHTML = `
        <tr><td colspan="4" class="loading-row">
            <div class="spinner" style="margin:0 auto"></div>
        </td></tr>
    `;

    try {
        const data = await apiFetch('/leaderboard');
        const entries = data.leaderboard || [];

        if (entries.length === 0) {
            table.innerHTML = '<tr><td colspan="4" class="empty-row">No scores yet — be the first!</td></tr>';
            return;
        }

        table.innerHTML = entries.map((entry, i) => {
            const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : '';
            return `
                <tr class="lb-row" data-aos="fade-up" data-aos-delay="${i * 40}">
                    <td class="lb-rank">${medal || entry.rank}</td>
                    <td class="lb-username">${escSafe(entry.username)}</td>
                    <td class="lb-points">${entry.total_points.toLocaleString()}</td>
                    <td class="lb-streak">
                        <span class="streak-badge ${entry.streak > 0 ? 'active' : ''}">
                            ${entry.streak > 0 ? '🔥 ' + entry.streak : '—'}
                        </span>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        table.innerHTML = `<tr><td colspan="4" class="empty-row">Could not load leaderboard: ${err.message}</td></tr>`;
    }
}

async function highlightCurrentUser() {
    const user = await getCurrentUser();
    if (!user) return;

    const { data } = await _supabase.from('users').select('username').eq('id', user.id).single();
    if (!data) return;

    document.querySelectorAll('.lb-row').forEach(row => {
        if (row.querySelector('.lb-username')?.textContent.trim() === data.username) {
            row.classList.add('current-user-row');
        }
    });
}

function escSafe(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}
