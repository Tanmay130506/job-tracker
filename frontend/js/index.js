const API = "http://localhost:8000";

/* If user already has a token, skip login and go straight to dashboard */
if (localStorage.getItem('token')) {
  window.location.href = 'dashboard.html';
}

/* Switch between Login and Register tabs */
function switchTab(tab) {
  document.querySelectorAll('.tab-btn').forEach((btn, i) => {
    btn.classList.toggle('active', (tab === 'login' ? i === 0 : i === 1));
  });
  document.getElementById('login-form').classList.toggle('active', tab === 'login');
  document.getElementById('register-form').classList.toggle('active', tab === 'register');
}

/* Show a status message inside a form (error or success) */
function showMsg(id, text, type) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = `msg ${type}`;
}

/* Handle login form submission */
async function handleLogin(e) {
  e.preventDefault(); // Prevent browser from refreshing the page on submit

  const email    = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;

  try {
    /* Send POST request to backend /login endpoint */
    const res = await fetch(`${API}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok) {
      /* Server returned an error (wrong credentials, etc.) */
      showMsg('login-msg', data.detail || 'Login failed', 'error');
      return;
    }

    /* Store JWT token in localStorage — every protected API call needs this */
    localStorage.setItem('token', data);

    /* Redirect to dashboard */
    window.location.href = 'dashboard.html';

  } catch (err) {
    /* Network error — server might not be running */
    showMsg('login-msg', 'Could not reach server. Is the backend running?', 'error');
  }
}

/* Handle register form submission */
async function handleRegister(e) {
  e.preventDefault();

  const username = document.getElementById('reg-username').value;
  const email    = document.getElementById('reg-email').value;
  const password = document.getElementById('reg-password').value;

  try {
    const res = await fetch(`${API}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password })
    });

    const data = await res.json();

    if (!res.ok) {
      showMsg('register-msg', data.detail || 'Registration failed', 'error');
      return;
    }

    /* Registration successful — switch to login tab after a short delay */
    showMsg('register-msg', 'Account created! Please sign in.', 'success');
    setTimeout(() => switchTab('login'), 1200);

  } catch (err) {
    showMsg('register-msg', 'Could not reach server. Is the backend running?', 'error');
  }
}