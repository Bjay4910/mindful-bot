// chat.js — handles the full chat + recall challenge flow

let sessionId = null;
let currentUser = null;
let currentChallenge = null;
let isWaitingForResponse = false;

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    const session = await getSession();
    if (!session) {
        // Show auth modal, block chat until logged in
        document.getElementById('auth-modal').classList.remove('hidden');
        window.onAuthSuccess = initChat;
        return;
    }
    await initChat();
});

async function initChat() {
    currentUser = await getCurrentUser();

    const urlSessionId = new URLSearchParams(window.location.search).get('session');
    if (urlSessionId) {
        sessionId = urlSessionId;
    } else {
        sessionId = generateUUID();
    }

    await loadUserScore();
    setupInputHandlers();

    if (urlSessionId) {
        await loadSessionHistory();
    } else {
        displayWelcome();
    }
}

// ── Session UUID ──────────────────────────────────────────────────────────────
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
        const r = Math.random() * 16 | 0;
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
}

// ── Welcome message ───────────────────────────────────────────────────────────
function displayWelcome() {
    appendBotMessage(
        "Hi! I'm Mindful, your learning companion. I'm here to help you think deeply — " +
        "not just get quick answers. What topic would you like to explore today?"
    );
}

// ── Load existing session history ─────────────────────────────────────────────
async function loadSessionHistory() {
    try {
        const data = await apiFetch(`/chat/history?session_id=${sessionId}`);
        const messages = data.messages || [];
        if (messages.length === 0) {
            displayWelcome();
            return;
        }
        for (const msg of messages) {
            if (msg.role === 'user') {
                appendUserMessage(msg.content);
            } else {
                appendBotMessage(msg.content);
            }
        }
    } catch (err) {
        displayWelcome();
    }
}

// ── Input handlers ────────────────────────────────────────────────────────────
function setupInputHandlers() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    input.addEventListener('input', () => {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    });
}

// ── Send message ──────────────────────────────────────────────────────────────
async function sendMessage() {
    if (isWaitingForResponse) return;

    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    input.style.height = 'auto';

    appendUserMessage(message);
    showTypingIndicator();
    isWaitingForResponse = true;

    try {
        const data = await apiFetch('/chat', {
            method: 'POST',
            body: JSON.stringify({ message, session_id: sessionId }),
        });

        removeTypingIndicator();
        appendBotMessage(data.response);

        console.log('[mindful-bot] chat response:', data);
        console.log('[mindful-bot] exchange_count:', data.exchange_count, '| should_challenge:', data.should_challenge);

        if (data.should_challenge) {
            console.log('[mindful-bot] triggering challenge...');
            setTimeout(triggerChallenge, 800);
        }
    } catch (err) {
        removeTypingIndicator();
        appendBotMessage('Sorry, something went wrong. Please try again.');
        showToast(err.message, 'error');
    } finally {
        isWaitingForResponse = false;
    }
}

// ── DOM helpers ───────────────────────────────────────────────────────────────
function appendUserMessage(text) {
    const messages = document.getElementById('chat-messages');
    const el = document.createElement('div');
    el.className = 'chat-bubble user-bubble user-bubble-enter';
    el.textContent = text;
    messages.appendChild(el);
    scrollToBottom();
}

function appendBotMessage(text) {
    const messages = document.getElementById('chat-messages');
    const el = document.createElement('div');
    el.className = 'chat-bubble bot-bubble bot-bubble-enter';
    el.innerHTML = `
        <div class="bot-avatar">M</div>
        <div class="bubble-text">${escapeHtml(text)}</div>
    `;
    messages.appendChild(el);
    scrollToBottom();
}

function showTypingIndicator() {
    const messages = document.getElementById('chat-messages');
    const el = document.createElement('div');
    el.id = 'typing-indicator';
    el.className = 'chat-bubble bot-bubble bubble-enter';
    el.innerHTML = `
        <div class="bot-avatar">M</div>
        <div class="typing-dots">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
    `;
    messages.appendChild(el);
    scrollToBottom();
}

function removeTypingIndicator() {
    document.getElementById('typing-indicator')?.remove();
}

function scrollToBottom() {
    const messages = document.getElementById('chat-messages');
    messages.scrollTop = messages.scrollHeight;
}

function escapeHtml(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br>');
}

// ── Challenge flow ────────────────────────────────────────────────────────────
// Challenges render as inline cards inside #chat-messages (not an overlay).

async function triggerChallenge() {
    const messages = document.getElementById('chat-messages');

    // Append a loading card directly in the chat
    const card = document.createElement('div');
    card.className = 'challenge-card-inline challenge-card-enter';
    card.innerHTML = `
        <div class="challenge-loading-inline">
            <div class="spinner"></div>
            <span>Preparing your recall challenge...</span>
        </div>
    `;
    messages.appendChild(card);
    scrollToBottom();

    try {
        const challenge = await apiFetch('/challenge', {
            method: 'POST',
            body: JSON.stringify({ session_id: sessionId }),
        });
        currentChallenge = challenge;
        renderChallenge(challenge, card);
    } catch (err) {
        card.remove();
        showToast('Could not generate challenge: ' + err.message, 'error');
    }
}

function renderChallenge(challenge, card) {
    card.innerHTML = `
        <div class="challenge-header">
            <span class="badge badge-blue">⚡ Recall Challenge</span>
            <button class="btn btn-ghost btn-sm" id="skip-challenge">Skip</button>
        </div>
        <p class="challenge-question">${escapeHtml(challenge.question)}</p>
        <p class="challenge-hint"><strong>Hint:</strong> ${escapeHtml(challenge.hint || '')}</p>
        <textarea
            id="challenge-answer"
            class="input-field"
            placeholder="Type your answer here..."
            rows="3"
        ></textarea>
        <div id="challenge-error" class="form-error"></div>
        <div class="challenge-actions">
            <button class="btn btn-primary" id="submit-challenge">Submit Answer</button>
        </div>
    `;
    scrollToBottom();
    document.getElementById('skip-challenge').addEventListener('click', () => {
        card.remove();
        currentChallenge = null;
        appendBotMessage("No worries — let's keep exploring. What else is on your mind?");
    });
    document.getElementById('submit-challenge').addEventListener('click', () => submitChallengeAnswer(card));
}

async function submitChallengeAnswer(card) {
    const answer = document.getElementById('challenge-answer').value.trim();
    const errEl = document.getElementById('challenge-error');

    if (!answer) {
        errEl.textContent = 'Please write an answer before submitting.';
        errEl.classList.add('visible');
        return;
    }
    errEl.classList.remove('visible');

    const submitBtn = document.getElementById('submit-challenge');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Evaluating...';

    try {
        const result = await apiFetch('/challenge/evaluate', {
            method: 'POST',
            body: JSON.stringify({
                challenge_id: currentChallenge.challenge_id,
                question: currentChallenge.question,
                correct_answer: currentChallenge.correct_answer,
                user_answer: answer,
            }),
        });
        renderChallengeResult(result, card);
    } catch (err) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Answer';
        errEl.textContent = err.message;
        errEl.classList.add('visible');
    }
}

function renderChallengeResult(result, card) {
    const scoreColor = result.score >= 7 ? '#0f7b6c' : result.score >= 4 ? '#c17d23' : '#c73a2d';
    const scoreBg   = result.score >= 7 ? '#e3f5f1' : result.score >= 4 ? '#fdf3e3' : '#fde8e6';

    card.innerHTML = `
        <div class="challenge-header">
            <span class="badge badge-blue">Result</span>
        </div>
        <div class="score-display" style="background:${scoreBg}; color:${scoreColor}">
            <span class="score-number score-pulse">${result.score}</span>
            <span class="score-label">/10 points</span>
        </div>
        <p class="challenge-feedback">${escapeHtml(result.feedback)}</p>
        <div class="correct-answer">
            <strong>Correct answer:</strong>
            <p>${escapeHtml(result.correct_answer)}</p>
        </div>
        <div class="challenge-actions">
            <button class="btn btn-primary" id="close-challenge">Continue Learning</button>
        </div>
    `;
    scrollToBottom();
    // Refresh sidebar score immediately so user sees updated points right away
    loadUserScore();
    document.getElementById('close-challenge').addEventListener('click', () => {
        card.remove();
        currentChallenge = null;
        appendBotMessage(
            result.is_correct
                ? `Great job! You scored ${result.score}/10. Let's keep going — what else would you like to explore?`
                : `You scored ${result.score}/10. No worries — active recall takes practice. Let's continue.`
        );
    });
}

// ── Score display ─────────────────────────────────────────────────────────────
async function loadUserScore() {
    if (!currentUser) return;
    try {
        const data = await apiFetch(`/scores/${currentUser.id}`);
        const el = document.getElementById('user-score');
        if (el) {
            countUp(el, data.total_points ?? 0);
            el.classList.add('score-pop');
            el.addEventListener('animationend', () => el.classList.remove('score-pop'), { once: true });
        }
        const streak = document.getElementById('user-streak');
        if (streak) countUp(streak, data.streak ?? 0);
    } catch (err) {
        // score display is non-critical
    }
}
