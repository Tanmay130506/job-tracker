const API = window.location.hostname === 'localhost' 
  ? "http://localhost:8000" 
  : "https://job-tracker-api-production-0b2e.up.railway.app";

/* ── If no token found, user is not logged in — send to login page ── */
if (!localStorage.getItem('token')) {
  window.location.href = 'index.html';
}

/* ── Get the stored JWT token from localStorage ── */
function getToken() {
  return localStorage.getItem('token');
}

/* ── Build the Authorization header required for all protected API calls ──
   Every route except /login and /register needs this header */
function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

/* ── Show a brief toast notification at bottom-right of screen ── */
function toast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  /* Automatically hide after 3 seconds */
  setTimeout(() => el.classList.remove('show'), 3000);
}

/* ── Logout: remove token from storage and redirect to login ── */
function logout() {
  localStorage.removeItem('token');
  window.location.href = 'index.html';
}

/* ── Toggle the "Add Application" form open or closed ── */
function toggleAddForm() {
  document.getElementById('add-form').classList.toggle('open');
}

/* ── Format a raw ISO date string into a readable format ── */
function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric'
  });
}

/* ── Return a coloured badge HTML string for a given status ── */
function statusBadge(status) {
  const s = (status || 'unknown').toLowerCase();
  return `<span class="badge ${s}">${status || 'Unknown'}</span>`;
}

/* ── Fetch all applications for this user and render them in the table ── */
async function loadApplications() {
  try {
    const res = await fetch(`${API}/applications`, {
      headers: authHeaders()
    });

    /* If the token is expired or invalid, send user back to login */
    if (res.status === 401) { logout(); return; }

    const apps = await res.json();
    const tbody = document.getElementById('app-table-body');

    if (!apps || apps.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="empty-state">No applications yet — add one above.</td></tr>`;
      return;
    }

    /* Build a table row for each application using a template literal */
    tbody.innerHTML = apps.map(app => `
      <tr>
        <td><strong>${app.company_name}</strong></td>
        <td>${app.role || '—'}</td>
        <td>${statusBadge(app.status)}</td>
        <td>${formatDate(app.date)}</td>
        <td>
          <button class="action-btn" onclick="openUpdatePrompt(${app.application_id}, '${app.status}')">Update</button>
          <button class="action-btn delete" onclick="deleteApplication(${app.application_id})">Delete</button>
        </td>
      </tr>
    `).join('');

  } catch (err) {
    document.getElementById('app-table-body').innerHTML =
      `<tr><td colspan="5" class="empty-state">Could not load applications.</td></tr>`;
  }
}

/* ── Add a new application manually using the form fields ── */
async function addApplication() {
  const company = document.getElementById('f-company').value.trim();
  const role    = document.getElementById('f-role').value.trim();
  const status  = document.getElementById('f-status').value;
  const through = document.getElementById('f-email').value === 'true';

  /* Basic validation before sending to API */
  if (!company || !role) {
    toast('Company name and role are required.');
    return;
  }

  try {
    const res = await fetch(`${API}/applications`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({
        company_name: company,
        role: role,
        status: status,
        applied_through_email: through
      })
    });

    if (!res.ok) {
      const data = await res.json();
      toast(data.detail || 'Failed to add application');
      return;
    }

    /* Close form, reset fields, refresh the table and analytics */
    toggleAddForm();
    document.getElementById('f-company').value = '';
    document.getElementById('f-role').value    = '';
    toast('Application added.');
    loadApplications();
    loadAnalytics();

  } catch (err) {
    toast('Could not reach server.');
  }
}

/* ── Open a browser prompt asking for the new status ──
   In a bigger app this would be a custom modal */
function openUpdatePrompt(appId, currentStatus) {
  const newStatus = prompt(
    `Current status: ${currentStatus}\n\nEnter new status:\napplied / interviewing / offered / rejected`,
    currentStatus
  );

  /* If user cancelled or typed the same status, do nothing */
  if (!newStatus || newStatus.trim().toLowerCase() === currentStatus) return;

  updateApplication(appId, newStatus.trim().toLowerCase());
}

/* ── Send status update to the API ── */
async function updateApplication(appId, newStatus) {
  try {
    const res = await fetch(`${API}/applications/${appId}`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify({ status: newStatus })
    });

    if (!res.ok) {
      const data = await res.json();
      toast(typeof data.detail === 'string' ? data.detail : 'Invalid status. Use: applied, interviewing, offered, rejected');
      return;
    }

    toast('Status updated.');
    /* Reload both table and analytics so numbers stay accurate */
    loadApplications();
    loadAnalytics();

  } catch (err) {
    toast('Could not reach server.');
  }
}

/* ── Delete an application after browser confirmation ── */
async function deleteApplication(appId) {
  /* Simple confirm dialog — user must explicitly agree before deleting */
  if (!confirm('Delete this application? This cannot be undone.')) return;

  try {
    const res = await fetch(`${API}/applications/${appId}`, {
      method: 'DELETE',
      headers: authHeaders()
    });

    if (!res.ok) {
      toast('Could not delete application.');
      return;
    }

    toast('Application deleted.');
    loadApplications();
    loadAnalytics();

  } catch (err) {
    toast('Could not reach server.');
  }
}

// Check URL for gmail=connected parameter on page load
window.addEventListener('load', () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('gmail') === 'connected') {
        toast('Gmail connected successfully!');
        // Clean up URL
        window.history.replaceState({}, '', '/dashboard.html');
    }
});

// Connect Gmail — redirects to OAuth flow
function connectGmail() {
    const token = getToken();
    window.location.href = `${API}/auth/gmail?token=${token}`;
}

// Check Gmail connection status on page load
async function checkGmailStatus() {
    try {
        const res = await fetch(`${API}/auth/gmail/status`, {
            headers: authHeaders()
        });
        const data = await res.json();
        
        const connectBtn = document.getElementById('connect-gmail-btn');
        if (data.connected) {
            connectBtn.textContent = 'Gmail Connected';
            connectBtn.disabled = true;
            connectBtn.style.opacity = '0.6';
            connectBtn.style.cursor = 'default';
        }
    } catch (err) {
        console.error('Could not check Gmail status');
    }
}

// Updated scanEmails with Gmail connection check
async function scanEmails() {
    try {
        // Check if Gmail is connected first
        const statusRes = await fetch(`${API}/auth/gmail/status`, {
            headers: authHeaders()
        });
        const statusData = await statusRes.json();
        
        if (!statusData.connected) {
            toast('Please connect Gmail first before scanning.');
            return;
        }

        const res = await fetch(`${API}/scan-emails`, {
            method: 'POST',
            headers: authHeaders()
        });

        if (!res.ok) {
            toast('Could not start scan.');
            return;
        }

        toast('Gmail scan started — check back in a moment.');

    } catch (err) {
        toast('Could not reach server.');
    }
}

/* ── Fetch all analytics endpoints and render the stat cards ── */
async function loadAnalytics() {
  try {
    /* Fire all 3 requests at the same time using Promise.all
       This is faster than awaiting them one after another */
    const [statusRes, rateRes, avgRes] = await Promise.all([
      fetch(`${API}/analytics/status-counts`,         { headers: authHeaders() }),
      fetch(`${API}/analytics/response-rate`,         { headers: authHeaders() }),
      fetch(`${API}/analytics/average-response-days`, { headers: authHeaders() })
    ]);

    const statusData = await statusRes.json();
    const rateData   = await rateRes.json();
    const avgData    = await avgRes.json();

    /* Build a simple lookup object from the status counts array
       e.g. { applied: 5, rejected: 2, interviewing: 1 } */
    const counts = {};
    let total = 0;
    if (Array.isArray(statusData)) {
      statusData.forEach(row => {
        counts[row.status] = row.count;
        total += row.count;
      });
    }

    const rate = rateData ? parseFloat(rateData).toFixed(1) : '—';
    const avg  = avgData  ? parseFloat(avgData).toFixed(1)  : '—';

    /* Inject stat cards into the analytics grid */
    document.getElementById('analytics-grid').innerHTML = `
      <div class="stat-card">
        <div class="label">Total applications</div>
        <div class="value">${total}</div>
      </div>
      <div class="stat-card">
        <div class="label">Applied</div>
        <div class="value">${counts['applied'] || 0}</div>
      </div>
      <div class="stat-card">
        <div class="label">Interviewing</div>
        <div class="value" style="color:var(--warning)">${counts['interviewing'] || 0}</div>
      </div>
      <div class="stat-card">
        <div class="label">Offered</div>
        <div class="value" style="color:var(--success)">${counts['offered'] || 0}</div>
      </div>
      <div class="stat-card">
        <div class="label">Rejected</div>
        <div class="value" style="color:var(--error)">${counts['rejected'] || 0}</div>
      </div>
      <div class="stat-card">
        <div class="label">Response rate</div>
        <div class="value">${rate}%</div>
        <div class="sub">moved past "applied"</div>
      </div>
      <div class="stat-card">
        <div class="label">Avg. days to response</div>
        <div class="value">${avg}</div>
        <div class="sub">days from apply to reply</div>
      </div>
    `;

  } catch (err) {
    /* Analytics failing silently is fine — don't break the whole page */
    console.error('Analytics load error:', err);
  }
}

/* ── On page load: fetch everything ── */
loadApplications();
loadAnalytics();
checkGmailStatus();