/**
 * Library AI Agent — Main JavaScript
 * Handles: dark mode toggle, toast notifications, shared utilities
 */

'use strict';

/* ── Dark / Light Mode ─────────────────────────────────── */
(function initTheme() {
  const saved = localStorage.getItem('libai-theme') || 'light';
  applyTheme(saved);
})();

function applyTheme(theme) {
  document.documentElement.setAttribute('data-bs-theme', theme);
  const icon = document.getElementById('themeIcon');
  if (icon) {
    icon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
  }
  localStorage.setItem('libai-theme', theme);
}

document.addEventListener('DOMContentLoaded', function () {
  const btn = document.getElementById('themeToggle');
  if (btn) {
    btn.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-bs-theme');
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }
  // Sync icon on page load
  const saved = localStorage.getItem('libai-theme') || 'light';
  applyTheme(saved);
});


/* ── Toast Notification ────────────────────────────────── */
/**
 * Show a Bootstrap toast message.
 * @param {string} message   - Message text
 * @param {string} colorClass - 'success' | 'warning' | 'danger' | 'info' | any bg- class
 */
function showToast(message, colorClass = 'success') {
  // Map short names to bg- classes
  const classMap = {
    success: 'bg-success text-white',
    warning: 'bg-warning text-dark',
    danger:  'bg-danger text-white',
    info:    'bg-info text-dark',
  };
  const cls = classMap[colorClass] || colorClass;

  // Remove previous dynamic toasts
  document.querySelectorAll('.dynamic-toast').forEach(el => el.remove());

  const wrapper = document.createElement('div');
  wrapper.className = 'position-fixed bottom-0 end-0 p-3 dynamic-toast';
  wrapper.style.zIndex = '9999';
  wrapper.innerHTML = `
    <div class="toast align-items-center border-0 rounded-3 shadow ${cls}" role="alert" aria-live="assertive">
      <div class="d-flex">
        <div class="toast-body fw-medium">${message}</div>
        <button type="button" class="btn-close me-2 m-auto ${colorClass === 'warning' ? '' : 'btn-close-white'}" 
                data-bs-dismiss="toast"></button>
      </div>
    </div>`;
  document.body.appendChild(wrapper);
  const toastEl = wrapper.querySelector('.toast');
  const toast = new bootstrap.Toast(toastEl, { delay: 3500 });
  toast.show();
  toastEl.addEventListener('hidden.bs.toast', () => wrapper.remove());
}


/* ── Auto-hide alerts ──────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.alert:not(.alert-permanent)').forEach(el => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    }, 5000);
  });
});


/* ── Active nav link ───────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {
  const path = window.location.pathname;
  document.querySelectorAll('#navbarNav .nav-link').forEach(link => {
    if (link.getAttribute('href') === path) {
      link.classList.add('active');
    }
  });
});
