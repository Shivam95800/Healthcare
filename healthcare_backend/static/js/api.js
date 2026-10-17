/**
 * CareOS API Client & Global Helpers
 * Handles JWT storage, authorization headers, transparent 401 token refresh,
 * toast alerts, and theme preferences.
 */

const TOKEN_KEY = 'careos_access_token';
const REFRESH_KEY = 'careos_refresh_token';
const USER_KEY = 'careos_user_data';
const THEME_KEY = 'careos_theme';

// Theme Management
function initTheme() {
  const savedTheme = localStorage.getItem(THEME_KEY);
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
  
  document.documentElement.setAttribute('data-theme', initialTheme);
  updateThemeIcon(initialTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem(THEME_KEY, newTheme);
  updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
  const btn = document.getElementById('theme-toggle-btn');
  if (btn) {
    btn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
    btn.title = `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`;
  }
}

// Authentication Token Helpers
function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY);
}

function getCurrentUser() {
  const data = localStorage.getItem(USER_KEY);
  try {
    return data ? JSON.parse(data) : null;
  } catch (e) {
    return null;
  }
}

function setAuthSession(access, refresh, user) {
  if (access) localStorage.setItem(TOKEN_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearAuthSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
}

// Toast Alert System
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
  toast.innerHTML = `<span style="font-weight:700">${icon}</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Transparent Authenticated Fetch with 401 Auto-Refresh
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

async function fetchWithAuth(url, options = {}) {
  const token = getAccessToken();
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...(options.headers || {})
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = { ...options, headers };

  try {
    let response = await fetch(url, config);

    // If 401 unauthorized, try refreshing token
    if (response.status === 401) {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        clearAuthSession();
        if (window.location.pathname.startsWith('/console')) {
          window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
        }
        return response;
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(newToken => {
          config.headers['Authorization'] = `Bearer ${newToken}`;
          return fetch(url, config);
        });
      }

      isRefreshing = true;

      try {
        const refreshResponse = await fetch('/api/auth/token/refresh/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh: refreshToken })
        });

        if (refreshResponse.ok) {
          const refreshData = await refreshResponse.json();
          const newAccess = refreshData.access;
          setAuthSession(newAccess, refreshData.refresh || refreshToken);
          processQueue(null, newAccess);

          // Retry initial request with new access token
          config.headers['Authorization'] = `Bearer ${newAccess}`;
          return fetch(url, config);
        } else {
          processQueue(new Error('Session expired'), null);
          clearAuthSession();
          if (window.location.pathname.startsWith('/console')) {
            window.location.href = '/login/?expired=1';
          }
          return response;
        }
      } catch (err) {
        processQueue(err, null);
        clearAuthSession();
        return response;
      } finally {
        isRefreshing = false;
      }
    }

    return response;
  } catch (error) {
    console.error('API Network Error:', error);
    throw error;
  }
}

// Auto-run theme initialization
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  const themeBtn = document.getElementById('theme-toggle-btn');
  if (themeBtn) {
    themeBtn.addEventListener('click', toggleTheme);
  }
});
