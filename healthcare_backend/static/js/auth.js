/**
 * CareOS Authentication Page Handlers (Login & Register)
 */

document.addEventListener('DOMContentLoaded', () => {
  // If already authenticated, redirect to /console/
  if (getAccessToken() && window.location.pathname !== '/console/') {
    // Check if token still valid or redirect directly
    // Optional: window.location.href = '/console/';
  }

  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const authAlert = document.getElementById('auth-alert');

  function showAlert(msg, isSuccess = false) {
    if (!authAlert) return;
    authAlert.textContent = msg;
    authAlert.className = `auth-alert ${isSuccess ? 'success' : 'error'}`;
    authAlert.style.display = 'block';
  }

  function hideAlert() {
    if (!authAlert) return;
    authAlert.style.display = 'none';
  }

  // Login handler
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert();

      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const submitBtn = loginForm.querySelector('button[type="submit"]');

      if (!email || !password) {
        showAlert('Please provide both email and password.');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Authenticating...';

      try {
        const response = await fetch('/api/auth/login/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok && data.success) {
          setAuthSession(data.access, data.refresh, data.user);
          showAlert('Authentication verified. Redirecting...', true);
          showToast('Login successful! Welcome to CareOS.', 'success');
          setTimeout(() => {
            window.location.href = '/console/';
          }, 800);
        } else {
          showAlert(data.message || 'Invalid credentials.');
          showToast(data.message || 'Login failed.', 'error');
        }
      } catch (err) {
        showAlert('Network error. Please verify the server is running.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign In';
      }
    });
  }

  // Register handler
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert();

      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const confirm_password = document.getElementById('confirm_password').value;
      const submitBtn = registerForm.querySelector('button[type="submit"]');

      if (!name || !email || !password) {
        showAlert('Please fill in all required fields.');
        return;
      }

      if (password !== confirm_password) {
        showAlert('Passwords do not match.');
        return;
      }

      if (password.length < 6) {
        showAlert('Password must contain at least 6 characters.');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Creating account...';

      try {
        const response = await fetch('/api/auth/register/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, password, confirm_password })
        });

        const data = await response.json();

        if (response.ok && data.success) {
          setAuthSession(data.tokens.access, data.tokens.refresh, data.user);
          showAlert('Account registered! Launching console...', true);
          showToast('Registration successful! Launching console...', 'success');
          setTimeout(() => {
            window.location.href = '/console/';
          }, 900);
        } else {
          let errorMsg = data.message || 'Registration failed.';
          if (data.errors && typeof data.errors === 'object') {
            const firstKey = Object.keys(data.errors)[0];
            if (firstKey) {
              errorMsg = `${firstKey}: ${data.errors[firstKey]}`;
            }
          }
          showAlert(errorMsg);
          showToast(errorMsg, 'error');
        }
      } catch (err) {
        showAlert('Network error during registration.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Account';
      }
    });
  }
});
