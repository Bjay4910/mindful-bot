// main.js — shared utilities loaded on every page

// ── Supabase client ──────────────────────────────────────────────────────────
const _supabase = supabase.createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_PUBLISHABLE_KEY);

// ── Auth helpers ─────────────────────────────────────────────────────────────
async function getSession() {
    const { data } = await _supabase.auth.getSession();
    return data.session;
}

async function getAccessToken() {
    const session = await getSession();
    return session?.access_token || null;
}

async function getCurrentUser() {
    const { data } = await _supabase.auth.getUser();
    return data.user || null;
}

async function logout() {
    await _supabase.auth.signOut();
    window.location.href = 'index.html';
}

// ── API helper ───────────────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
    const token = await getAccessToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...(options.headers || {}),
    };
    const response = await fetch(`${CONFIG.API_BASE_URL}${path}`, {
        ...options,
        headers,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
    return data;
}

// ── Toast notifications ───────────────────────────────────────────────────────
function showToast(message, type = 'default', duration = 3500) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${type} notif-enter`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('notif-exit');
        toast.addEventListener('animationend', () => toast.remove(), { once: true });
    }, duration);
}

// ── Nav user state ────────────────────────────────────────────────────────────
async function updateNavState() {
    const session = await getSession();
    const authLinks = document.getElementById('nav-auth-links');
    const userLinks = document.getElementById('nav-user-links');
    const userLabel = document.getElementById('nav-username');

    if (!authLinks || !userLinks) return;

    if (session) {
        authLinks.style.display = 'none';
        userLinks.style.display = 'flex';
        if (userLabel) {
            const user = await getCurrentUser();
            const { data } = await _supabase
                .from('users')
                .select('username')
                .eq('id', user.id)
                .single();
            userLabel.textContent = data?.username || user.email.split('@')[0];
        }
    } else {
        authLinks.style.display = 'flex';
        userLinks.style.display = 'none';
    }
}

// ── Auth modal logic ─────────────────────────────────────────────────────────
function initAuthModal() {
    const overlay = document.getElementById('auth-modal');
    if (!overlay) return;

    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const loginErr = document.getElementById('login-error');
    const regErr = document.getElementById('register-error');

    // Open / close
    document.querySelectorAll('[data-open-login]').forEach(el =>
        el.addEventListener('click', () => {
            overlay.classList.remove('hidden');
            showPanel('login');
        })
    );
    document.querySelectorAll('[data-open-register]').forEach(el =>
        el.addEventListener('click', () => {
            overlay.classList.remove('hidden');
            showPanel('register');
        })
    );
    document.getElementById('close-auth-modal')?.addEventListener('click', () =>
        overlay.classList.add('hidden')
    );
    overlay.addEventListener('click', e => {
        if (e.target === overlay) overlay.classList.add('hidden');
    });

    // Switch panels
    document.getElementById('switch-to-register')?.addEventListener('click', e => {
        e.preventDefault(); showPanel('register');
    });
    document.getElementById('switch-to-login')?.addEventListener('click', e => {
        e.preventDefault(); showPanel('login');
    });

    function showPanel(panel) {
        loginForm.closest('.auth-panel').style.display = panel === 'login' ? 'block' : 'none';
        registerForm.closest('.auth-panel').style.display = panel === 'register' ? 'block' : 'none';
    }

    // Login submit
    loginForm?.addEventListener('submit', async e => {
        e.preventDefault();
        loginErr.classList.remove('visible');
        const email = loginForm.email.value.trim();
        const password = loginForm.password.value;
        try {
            const data = await apiFetch('/users/login', {
                method: 'POST',
                body: JSON.stringify({ email, password }),
            });
            // Set session via Supabase client
            await _supabase.auth.setSession(data.session);
            overlay.classList.add('hidden');
            showToast('Welcome back!', 'success');
            await updateNavState();
            if (window.onAuthSuccess) window.onAuthSuccess(data.user);
        } catch (err) {
            loginErr.textContent = err.message;
            loginErr.classList.add('visible');
        }
    });

    // Register submit
    registerForm?.addEventListener('submit', async e => {
        e.preventDefault();
        regErr.classList.remove('visible');
        const email = registerForm.email.value.trim();
        const password = registerForm.password.value;
        const username = registerForm.username.value.trim();
        try {
            const data = await apiFetch('/users/register', {
                method: 'POST',
                body: JSON.stringify({ email, password, username }),
            });
            if (data.session) {
                await _supabase.auth.setSession(data.session);
                overlay.classList.add('hidden');
                showToast('Account created! Welcome.', 'success');
                await updateNavState();
                if (window.onAuthSuccess) window.onAuthSuccess(data.user);
            } else {
                overlay.classList.add('hidden');
                showToast('Check your email to confirm your account.', 'default');
            }
        } catch (err) {
            regErr.textContent = err.message;
            regErr.classList.add('visible');
        }
    });
}

// ── Hamburger menu (mobile) ───────────────────────────────────────────────────
function initHamburgerMenu() {
    const nav = document.querySelector('.topnav');
    const links = nav?.querySelector('.topnav-links');
    if (!nav || !links) return;

    const btn = document.createElement('button');
    btn.className = 'nav-hamburger';
    btn.setAttribute('aria-label', 'Toggle menu');
    btn.innerHTML = '<span></span><span></span><span></span>';

    nav.insertBefore(btn, links);

    // On mobile, move auth button groups into the dropdown so the nav bar
    // isn't overcrowded — existing show/hide logic in updateNavState() still works
    if (window.innerWidth <= 768) {
        ['nav-auth-links', 'nav-user-links'].forEach(id => {
            const el = document.getElementById(id);
            if (el) links.appendChild(el);
        });
    }

    btn.addEventListener('click', e => {
        e.stopPropagation();
        nav.classList.toggle('nav-open');
    });

    links.addEventListener('click', () => nav.classList.remove('nav-open'));

    document.addEventListener('click', e => {
        if (!nav.contains(e.target)) nav.classList.remove('nav-open');
    });
}

// ── Navbar scroll shrink ─────────────────────────────────────────────────────
function initNavScroll() {
    const nav = document.querySelector('.topnav');
    if (!nav) return;
    const onScroll = () => {
        nav.classList.toggle('nav-scrolled', window.scrollY > 20);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll(); // apply on load in case page is already scrolled
}

// ── Count-up animation ────────────────────────────────────────────────────────
function countUp(el, target, duration = 900) {
    if (!el) return;
    const start = parseInt(el.textContent) || 0;
    const diff = target - start;
    if (diff === 0) return;
    const startTime = performance.now();
    function step(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // ease-out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(start + diff * eased);
        if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

// ── Password visibility toggle ────────────────────────────────────────────────
function initPasswordToggles() {
    document.querySelectorAll('input[type="password"]').forEach(input => {
        const wrapper = document.createElement('div');
        wrapper.style.cssText = 'position:relative; display:block;';
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = '👁';
        btn.style.cssText =
            'position:absolute; right:10px; top:50%; transform:translateY(-50%);' +
            'background:none; border:none; cursor:pointer; font-size:1rem;' +
            'color:var(--color-text-secondary); padding:0; line-height:1;';
        btn.setAttribute('aria-label', 'Toggle password visibility');
        wrapper.appendChild(btn);

        input.style.paddingRight = '36px';

        btn.addEventListener('click', () => {
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            btn.textContent = isPassword ? '🙈' : '👁';
        });
    });
}

// ── Init on DOM ready ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    AOS.init({ duration: 600, once: true, offset: 40 });
    updateNavState();
    initAuthModal();
    initNavScroll();
    initHamburgerMenu();
    initPasswordToggles();

    // Logout button
    document.getElementById('logout-btn')?.addEventListener('click', async e => {
        e.preventDefault();
        await logout();
    });
});
